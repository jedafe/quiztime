from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import QuizAttempt, Quiz, Question, User, Challenge
from app.schemas import AttemptSubmit, AttemptResponse, QuizStats
from app.auth import get_current_user

router = APIRouter(prefix="/api/attempts", tags=["attempts"])


@router.post("", response_model=AttemptResponse, status_code=201)
async def submit_attempt(
    data: AttemptSubmit,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    quiz_result = await db.execute(select(Quiz).where(Quiz.id == data.quiz_id))
    quiz = quiz_result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    q_result = await db.execute(select(Question).where(Question.quiz_id == data.quiz_id))
    questions = q_result.scalars().all()

    score = 0
    total = len(questions)
    for q in questions:
        q_id_str = str(q.id)
        user_answer = data.answers.get(q_id_str, [])
        # Validate answer indices are within bounds
        if any(idx < 0 or idx >= len(q.options) for idx in user_answer):
            raise HTTPException(
                status_code=400,
                detail=f"Answer index out of bounds for question {q.id}",
            )
        if sorted(user_answer) == sorted(q.answer):
            score += 1

    attempt = QuizAttempt(
        quiz_id=data.quiz_id,
        user_id=user.id,
        answers=data.answers,
        score=score,
        total=total,
        time_spent=data.time_spent,
    )
    db.add(attempt)
    await db.commit()
    await db.refresh(attempt)

    if data.challenge_code:
        chal_result = await db.execute(
            select(Challenge).where(
                Challenge.challenge_code == data.challenge_code,
                Challenge.quiz_id == data.quiz_id,
                Challenge.status.in_(["pending", "accepted"]),
            )
        )
        challenge = chal_result.scalar_one_or_none()
        if challenge:
            challenge.challengee_attempt_id = attempt.id
            challenge.status = "completed"
            await db.commit()

    return attempt


@router.get("/mine", response_model=list[AttemptResponse])
async def my_attempts(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(QuizAttempt)
        .where(QuizAttempt.user_id == user.id)
        .order_by(QuizAttempt.created_at.desc())
    )
    return [AttemptResponse.model_validate(a) for a in result.scalars().all()]


@router.get("/{attempt_id}", response_model=AttemptResponse)
async def get_attempt(
    attempt_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(QuizAttempt).where(QuizAttempt.id == attempt_id))
    attempt = result.scalar_one_or_none()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if attempt.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return attempt


@router.get("/quiz/{quiz_id}/stats", response_model=QuizStats)
async def quiz_stats(quiz_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            func.count(QuizAttempt.id).label("total"),
            func.avg(QuizAttempt.score).label("avg_score"),
            func.max(QuizAttempt.score).label("best"),
        ).where(QuizAttempt.quiz_id == quiz_id)
    )
    row = result.one()
    total = row.total or 0
    avg_score = float(row.avg_score or 0)
    best = row.best or 0

    # Get total questions for percentage
    q_count = await db.execute(
        select(func.count(Question.id)).where(Question.quiz_id == quiz_id)
    )
    total_questions = q_count.scalar() or 1

    return QuizStats(
        total_attempts=total,
        avg_score=avg_score,
        avg_percentage=round((avg_score / total_questions) * 100, 2) if total_questions else 0,
        best_score=best,
    )
