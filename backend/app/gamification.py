from datetime import datetime, timezone, date, timedelta
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models import User, BadgeDefinition, UserBadge, QuizAttempt, Quiz, XpEvent

XP_QUIZ_COMPLETE = 10
XP_PERFECT_BONUS = 50
XP_CREATE_QUIZ = 25
XP_DAILY_STREAK_BASE = 10
XP_STREAK_BONUS_MULTIPLIER = 5


async def award_xp(
    db: AsyncSession,
    user: User,
    source: str,
    amount: int,
    quiz_id: UUID | None = None,
    attempt_id: UUID | None = None,
) -> bool:
    user.xp += amount
    new_level = (user.xp // 100) + 1
    leveled_up = new_level > user.level
    user.level = new_level

    event = XpEvent(
        user_id=user.id, source=source, amount=amount,
        quiz_id=quiz_id, attempt_id=attempt_id,
    )
    db.add(event)
    return leveled_up


async def update_streak(db: AsyncSession, user: User) -> int:
    today = date.today()
    last = user.last_activity_date.date() if user.last_activity_date else None

    if last == today:
        return user.streak_count

    if last == today - timedelta(days=1):
        user.streak_count += 1
    else:
        user.streak_count = 1

    user.last_activity_date = datetime.now(timezone.utc).replace(tzinfo=None)
    return user.streak_count


async def check_and_award_badges(
    db: AsyncSession,
    user: User,
    source: str,
    **kwargs,
) -> list[str]:
    earned: list[str] = []

    result = await db.execute(select(BadgeDefinition))
    badges = {b.key: b for b in result.scalars().all()}

    async def _has(key: str) -> bool:
        if key not in badges:
            return True
        r = await db.execute(
            select(UserBadge).where(
                UserBadge.user_id == user.id,
                UserBadge.badge_id == badges[key].id,
            )
        )
        return r.scalar_one_or_none() is not None

    async def _award(key: str):
        if key not in badges:
            return
        if await _has(key):
            return
        ub = UserBadge(user_id=user.id, badge_id=badges[key].id)
        db.add(ub)
        earned.append(key)

    match source:
        case "quiz_complete":
            r = await db.execute(
                select(func.count()).select_from(QuizAttempt).where(
                    QuizAttempt.user_id == user.id,
                )
            )
            total_attempts = r.scalar() or 0
            if total_attempts >= 1:
                await _award("first_quiz")
            if total_attempts >= 50:
                await _award("knowledge_seeker")

            attempt_id = kwargs.get("attempt_id")
            if attempt_id:
                r = await db.execute(select(QuizAttempt).where(QuizAttempt.id == attempt_id))
                attempt = r.scalar_one_or_none()
                if attempt and attempt.total > 0 and attempt.score == attempt.total:
                    await _award("perfect_score")

        case "quiz_created":
            r = await db.execute(
                select(func.count()).select_from(Quiz).where(Quiz.created_by == user.id)
            )
            total_created = r.scalar() or 0
            if total_created >= 5:
                await _award("quiz_creator")

        case "streak":
            streak = kwargs.get("streak", 0)
            if streak >= 7:
                await _award("streak_master")

        case "level_up":
            level = kwargs.get("level", 0)
            if level >= 10:
                await _award("centurion")

    return earned
