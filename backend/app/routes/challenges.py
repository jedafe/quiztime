import uuid
import random
import string
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.database import get_db
from app.models import Challenge, Quiz, QuizAttempt, User
from app.schemas import ChallengeCreate, ChallengeResponse, ChallengeResult
from app.auth import get_current_user

router = APIRouter(prefix="/api/challenges", tags=["challenges"])


def generate_challenge_code(length=12):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def compute_grade(percentage: float) -> str:
    if percentage <= 40:
        return "Failed"
    elif percentage <= 59:
        return "Pass"
    elif percentage <= 69:
        return "Good"
    return "Excellent"


@router.post("", response_model=ChallengeResponse, status_code=201)
async def create_challenge(
    data: ChallengeCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    quiz_result = await db.execute(select(Quiz).where(Quiz.id == data.quiz_id))
    quiz = quiz_result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    attempt_result = await db.execute(
        select(QuizAttempt).where(
            QuizAttempt.id == data.challenger_attempt_id,
            QuizAttempt.user_id == user.id,
        )
    )
    if not attempt_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Attempt not found")

    code = generate_challenge_code()
    while True:
        check = await db.execute(select(Challenge).where(Challenge.challenge_code == code))
        if not check.scalar_one_or_none():
            break
        code = generate_challenge_code()

    challenge = Challenge(
        quiz_id=data.quiz_id,
        challenger_id=user.id,
        score_to_beat=data.score_to_beat,
        total_questions=data.total_questions,
        challenger_attempt_id=data.challenger_attempt_id,
        challenge_code=code,
        status="pending",
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=7),
    )
    db.add(challenge)
    await db.commit()
    await db.refresh(challenge)

    return ChallengeResponse(
        id=challenge.id,
        quiz_id=challenge.quiz_id,
        quiz_title=quiz.title,
        challenger_username=user.username,
        score_to_beat=challenge.score_to_beat,
        total_questions=challenge.total_questions,
        challenge_code=challenge.challenge_code,
        status=challenge.status,
        expires_at=challenge.expires_at,
        created_at=challenge.created_at,
    )


@router.get("", response_model=list[ChallengeResponse])
async def my_challenges(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Challenge)
        .where(Challenge.challenger_id == user.id)
        .order_by(Challenge.created_at.desc())
        .limit(50)
    )
    challenges = result.scalars().all()

    response = []
    for c in challenges:
        quiz_result = await db.execute(select(Quiz).where(Quiz.id == c.quiz_id))
        quiz = quiz_result.scalar_one_or_none()
        response.append(ChallengeResponse(
            id=c.id,
            quiz_id=c.quiz_id,
            quiz_title=quiz.title if quiz else "",
            challenger_username=user.username,
            score_to_beat=c.score_to_beat,
            total_questions=c.total_questions,
            challenge_code=c.challenge_code,
            status=c.status,
            expires_at=c.expires_at,
            created_at=c.created_at,
        ))
    return response


@router.get("/{code}", response_model=ChallengeResponse)
async def get_challenge(code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Challenge).where(Challenge.challenge_code == code)
    )
    challenge = result.scalar_one_or_none()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    quiz_result = await db.execute(select(Quiz).where(Quiz.id == challenge.quiz_id))
    quiz = quiz_result.scalar_one_or_none()

    user_result = await db.execute(select(User).where(User.id == challenge.challenger_id))
    challenger = user_result.scalar_one_or_none()

    return ChallengeResponse(
        id=challenge.id,
        quiz_id=challenge.quiz_id,
        quiz_title=quiz.title if quiz else "",
        challenger_username=challenger.username if challenger else "",
        score_to_beat=challenge.score_to_beat,
        total_questions=challenge.total_questions,
        challenge_code=challenge.challenge_code,
        status=challenge.status,
        expires_at=challenge.expires_at,
        created_at=challenge.created_at,
    )


@router.post("/{code}/accept", response_model=ChallengeResponse)
async def accept_challenge(
    code: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Challenge).where(Challenge.challenge_code == code)
    )
    challenge = result.scalar_one_or_none()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    if challenge.status != "pending":
        raise HTTPException(status_code=400, detail="Challenge already accepted or completed or expired")
    if challenge.expires_at.replace(tzinfo=None) < datetime.now(timezone.utc).replace(tzinfo=None):
        challenge.status = "expired"
        await db.commit()
        raise HTTPException(status_code=400, detail="Challenge has expired")

    challenge.status = "accepted"
    await db.commit()
    await db.refresh(challenge)

    quiz_result = await db.execute(select(Quiz).where(Quiz.id == challenge.quiz_id))
    quiz = quiz_result.scalar_one_or_none()

    user_result = await db.execute(select(User).where(User.id == challenge.challenger_id))
    challenger = user_result.scalar_one_or_none()

    return ChallengeResponse(
        id=challenge.id,
        quiz_id=challenge.quiz_id,
        quiz_title=quiz.title if quiz else "",
        challenger_username=challenger.username if challenger else "",
        score_to_beat=challenge.score_to_beat,
        total_questions=challenge.total_questions,
        challenge_code=challenge.challenge_code,
        status=challenge.status,
        expires_at=challenge.expires_at,
        created_at=challenge.created_at,
    )


@router.get("/{code}/result", response_model=ChallengeResult)
async def get_challenge_result(code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Challenge).where(Challenge.challenge_code == code)
    )
    challenge = result.scalar_one_or_none()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    challenger_user = await db.execute(
        select(User).where(User.id == challenge.challenger_id)
    )
    challenger = challenger_user.scalar_one_or_none()

    challenger_attempt = None
    if challenge.challenger_attempt_id:
        att_result = await db.execute(
            select(QuizAttempt).where(QuizAttempt.id == challenge.challenger_attempt_id)
        )
        challenger_attempt = att_result.scalar_one_or_none()

    chal_score = challenger_attempt.score if challenger_attempt else challenge.score_to_beat
    chal_total = challenger_attempt.total if challenger_attempt else challenge.total_questions
    chal_percentage = round((chal_score / chal_total) * 100, 1) if chal_total else 0

    result_data = ChallengeResult(
        challenger_username=challenger.username if challenger else "",
        challenger_score=chal_score,
        challenger_total=chal_total,
        challenger_percentage=chal_percentage,
        challenger_time=challenger_attempt.time_spent if challenger_attempt else 0,
        status=challenge.status,
    )

    if challenge.challengee_attempt_id:
        chall_att_result = await db.execute(
            select(QuizAttempt).where(QuizAttempt.id == challenge.challengee_attempt_id)
        )
        challengee_attempt = chall_att_result.scalar_one_or_none()

        if challengee_attempt:
            chall_e_score = challengee_attempt.score
            chall_e_total = challengee_attempt.total
            chall_e_percentage = round((chall_e_score / chall_e_total) * 100, 1) if chall_e_total else 0

            # Get challengee username
            chall_e_user_result = await db.execute(
                select(User).where(User.id == challengee_attempt.user_id)
            )
            challengee_user = chall_e_user_result.scalar_one_or_none()

            result_data.challengee_username = challengee_user.username if challengee_user else ""
            result_data.challengee_score = chall_e_score
            result_data.challengee_total = chall_e_total
            result_data.challengee_percentage = chall_e_percentage
            result_data.challengee_time = challengee_attempt.time_spent

            if chal_score > chall_e_score:
                result_data.winner = "challenger"
            elif chall_e_score > chal_score:
                result_data.winner = "challengee"
            else:
                result_data.winner = "draw"

            result_data.status = "completed"

    return result_data
