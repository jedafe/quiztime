from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.database import get_db
from app.models import User, BadgeDefinition, UserBadge, XpEvent
from app.schemas import (
    UserProfileResponse, BadgeResponse, XpEventResponse, XpLeaderboardEntry,
)
from app.auth import get_current_user

router = APIRouter(prefix="/api/gamification", tags=["gamification"])


@router.get("/my-profile", response_model=UserProfileResponse)
async def my_profile(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await _build_profile(db, user)


@router.get("/profile/{user_id}", response_model=UserProfileResponse)
async def user_profile(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await _build_profile(db, user)


async def _build_profile(db: AsyncSession, user: User) -> UserProfileResponse:
    badge_result = await db.execute(
        select(BadgeDefinition, UserBadge.earned_at)
        .outerjoin(UserBadge, (UserBadge.badge_id == BadgeDefinition.id) & (UserBadge.user_id == user.id))
        .order_by(BadgeDefinition.key)
    )
    badges = [
        BadgeResponse(
            id=bd.id, key=bd.key, name=bd.name,
            description=bd.description, icon=bd.icon,
            earned_at=earned_at,
        )
        for bd, earned_at in badge_result.all()
    ]
    return UserProfileResponse(
        id=user.id, username=user.username, created_at=user.created_at,
        xp=user.xp, level=user.level, streak_count=user.streak_count or 0,
        badges=badges, email_verified=user.email_verified,
    )


@router.get("/xp-history", response_model=dict)
async def xp_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    offset = (page - 1) * page_size
    count_result = await db.execute(
        select(func.count(XpEvent.id)).where(XpEvent.user_id == user.id)
    )
    total = count_result.scalar() or 0

    result = await db.execute(
        select(XpEvent)
        .where(XpEvent.user_id == user.id)
        .order_by(XpEvent.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    items = [XpEventResponse.model_validate(e) for e in result.scalars().all()]
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/badges", response_model=list[BadgeResponse])
async def list_badges(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(BadgeDefinition, UserBadge.earned_at)
        .outerjoin(UserBadge, (UserBadge.badge_id == BadgeDefinition.id) & (UserBadge.user_id == user.id))
        .order_by(BadgeDefinition.key)
    )
    return [
        BadgeResponse(
            id=bd.id, key=bd.key, name=bd.name,
            description=bd.description, icon=bd.icon,
            earned_at=earned_at,
        )
        for bd, earned_at in result.all()
    ]


@router.get("/leaderboard", response_model=list[XpLeaderboardEntry])
async def xp_leaderboard(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User)
        .order_by(User.xp.desc())
        .limit(limit)
    )
    return [
        XpLeaderboardEntry(rank=i + 1, username=u.username, user_id=u.id, xp=u.xp, level=u.level)
        for i, u in enumerate(result.scalars().all())
    ]
