import math
from datetime import datetime, timezone, timedelta
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from app.database import get_db
from app.models import Quiz, Question, User, QuizAttempt, Rating
from app.schemas import (
    QuizCreate, QuizUpdate, QuizResponse, QuizDetail, QuizWithAnswers,
    QuestionPublic, PaginatedQuizzes, LeaderboardResponse, LeaderboardEntry,
    RatingStats, QuizExport, QuestionExport, QuizImport, MessageResponse,
)
from app.auth import get_current_user, require_admin
from app.gamification import award_xp, check_and_award_badges
from app.models import Category

router = APIRouter(prefix="/api/quizzes", tags=["quizzes"])


@router.get("", response_model=PaginatedQuizzes)
async def list_quizzes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query("", max_length=200),
    category_id: UUID = Query(None),
    sort_by: str = Query("newest", pattern="^(newest|popular|rating)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size

    # Build base query
    q = select(Quiz, func.count(Question.id).label("question_count"))

    if category_id:
        q = q.where(Quiz.category_id == category_id)
    q = q.outerjoin(Question)

    if search:
        pattern = f"%{search}%"
        q = q.where(
            Quiz.title.ilike(pattern) | Quiz.description.ilike(pattern)
        )

    q = q.group_by(Quiz.id)

    # Total count (without LIMIT/OFFSET)
    count_q = select(func.count()).select_from(q.subquery())
    count_result = await db.execute(count_q)
    total = count_result.scalar() or 0

    # Add computed columns for sorting
    attempt_count_subq = (
        select(func.count(QuizAttempt.id).label("cnt"))
        .where(QuizAttempt.quiz_id == Quiz.id)
        .correlate(Quiz)
        .scalar_subquery()
    )
    avg_rating_subq = (
        select(func.coalesce(func.avg(Rating.score), 0).label("avg_r"))
        .where(Rating.quiz_id == Quiz.id)
        .correlate(Quiz)
        .scalar_subquery()
    )

    q = q.add_columns(attempt_count_subq.label("attempt_count"))
    q = q.add_columns(avg_rating_subq.label("avg_rating"))

    order_col = Quiz.created_at
    if sort_by == "popular":
        order_col = attempt_count_subq
    elif sort_by == "rating":
        order_col = avg_rating_subq

    order_fn = order_col.desc() if sort_order == "desc" else order_col.asc()
    q = q.order_by(order_fn)

    result = await db.execute(q.offset(offset).limit(page_size))
    items = [
        QuizResponse(
            id=quiz.id,
            title=quiz.title,
            description=quiz.description,
            created_by=quiz.created_by,
            category_id=quiz.category_id,
            created_at=quiz.created_at,
            question_count=qcount,
            attempt_count=acount or 0,
            avg_rating=round(float(arating or 0), 1),
        )
        for quiz, qcount, acount, arating in result.all()
    ]
    return PaginatedQuizzes(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 0,
    )


@router.post("", response_model=QuizResponse, status_code=201)
async def create_quiz(
    data: QuizCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    quiz = Quiz(title=data.title, description=data.description, category_id=data.category_id, created_by=user.id)
    db.add(quiz)
    await db.commit()
    await db.refresh(quiz)

    leveled_up = await award_xp(db, user, "quiz_created", 25, quiz_id=quiz.id)
    badges = await check_and_award_badges(db, user, "quiz_created")
    if leveled_up:
        await check_and_award_badges(db, user, "level_up", level=user.level)
    await db.commit()

    return QuizResponse(
        id=quiz.id, title=quiz.title, description=quiz.description,
        category_id=quiz.category_id,
        created_by=quiz.created_by, created_at=quiz.created_at, question_count=0,
    )


@router.get("/{quiz_id}", response_model=QuizDetail)
async def get_quiz(quiz_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    q_result = await db.execute(select(Question).where(Question.quiz_id == quiz_id))
    questions = q_result.scalars().all()

    ac_result = await db.execute(
        select(func.count(QuizAttempt.id)).where(QuizAttempt.quiz_id == quiz_id)
    )
    attempt_count = ac_result.scalar() or 0

    ar_result = await db.execute(
        select(func.coalesce(func.avg(Rating.score), 0)).where(Rating.quiz_id == quiz_id)
    )
    avg_rating = round(float(ar_result.scalar() or 0), 1)

    return QuizDetail(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        created_by=quiz.created_by,
        category_id=quiz.category_id,
        created_at=quiz.created_at,
        attempt_count=attempt_count,
        avg_rating=avg_rating,
        questions=[
            QuestionPublic(id=q.id, type=q.type, text=q.text, options=q.options)
            for q in questions
        ],
    )


@router.get("/{quiz_id}/manage", response_model=QuizWithAnswers)
async def get_quiz_manage(
    quiz_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if quiz.created_by != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    q_result = await db.execute(select(Question).where(Question.quiz_id == quiz_id))
    questions = q_result.scalars().all()

    return QuizWithAnswers(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        created_by=quiz.created_by,
        category_id=quiz.category_id,
        created_at=quiz.created_at,
        questions=questions,
    )


@router.get("/{quiz_id}/export")
async def export_quiz(
    quiz_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if quiz.created_by != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    q_result = await db.execute(select(Question).where(Question.quiz_id == quiz_id))
    questions = q_result.scalars().all()

    category_name = None
    if quiz.category_id:
        cat_result = await db.execute(select(Category).where(Category.id == quiz.category_id))
        cat = cat_result.scalar_one_or_none()
        category_name = cat.name if cat else None

    return QuizExport(
        title=quiz.title,
        description=quiz.description,
        category_name=category_name,
        questions=[
            QuestionExport(type=q.type, text=q.text, options=q.options, answer=q.answer)
            for q in questions
        ],
    )


@router.post("/import", response_model=QuizResponse, status_code=201)
async def import_quiz(
    data: QuizImport,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    category_id = None
    if data.category_name:
        cat_result = await db.execute(select(Category).where(Category.name == data.category_name))
        cat = cat_result.scalar_one_or_none()
        if cat:
            category_id = cat.id

    quiz = Quiz(
        title=data.title,
        description=data.description,
        category_id=category_id,
        created_by=user.id,
    )
    db.add(quiz)
    await db.flush()

    for qi in data.questions:
        question = Question(
            quiz_id=quiz.id,
            type=qi.type,
            text=qi.text,
            options=qi.options,
            answer=qi.answer,
        )
        db.add(question)

    await db.commit()
    await db.refresh(quiz)

    leveled_up = await award_xp(db, user, "quiz_created", 25, quiz_id=quiz.id)
    badges = await check_and_award_badges(db, user, "quiz_created")
    if leveled_up:
        await check_and_award_badges(db, user, "level_up", level=user.level)
    await db.commit()

    count_result = await db.execute(
        select(func.count(Question.id)).where(Question.quiz_id == quiz.id)
    )
    count = count_result.scalar() or 0

    return QuizResponse(
        id=quiz.id, title=quiz.title, description=quiz.description,
        category_id=quiz.category_id,
        created_by=quiz.created_by, created_at=quiz.created_at, question_count=count,
    )


@router.get("/{quiz_id}/take", response_model=QuizWithAnswers)
async def get_quiz_for_taking(
    quiz_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    q_result = await db.execute(select(Question).where(Question.quiz_id == quiz_id))
    questions = q_result.scalars().all()

    return QuizWithAnswers(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        created_by=quiz.created_by,
        category_id=quiz.category_id,
        created_at=quiz.created_at,
        questions=questions,
    )


@router.put("/{quiz_id}", response_model=QuizResponse)
async def update_quiz(
    quiz_id: UUID,
    data: QuizUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if quiz.created_by != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    if data.title is not None:
        quiz.title = data.title
    if data.description is not None:
        quiz.description = data.description
    if data.category_id is not None:
        quiz.category_id = data.category_id
    elif "category_id" in data.model_dump(exclude_unset=True):
        quiz.category_id = None

    await db.commit()
    await db.refresh(quiz)

    count_result = await db.execute(
        select(func.count(Question.id)).where(Question.quiz_id == quiz_id)
    )
    count = count_result.scalar() or 0

    return QuizResponse(
        id=quiz.id, title=quiz.title, description=quiz.description,
        created_by=quiz.created_by, category_id=quiz.category_id,
        created_at=quiz.created_at, question_count=count,
    )


@router.delete("/{quiz_id}", status_code=204)
async def delete_quiz(
    quiz_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if quiz.created_by != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    await db.delete(quiz)
    await db.commit()


@router.get("/{quiz_id}/leaderboard", response_model=LeaderboardResponse)
async def quiz_leaderboard(
    quiz_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    period: str = Query("all", pattern="^(today|week|month|all)$"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    quiz_result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    if not quiz_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Quiz not found")

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if period == "today":
        since = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        since = now - timedelta(days=7)
    elif period == "month":
        since = now - timedelta(days=30)
    else:
        since = None

    base_query = (
        select(QuizAttempt, User.username)
        .join(User, User.id == QuizAttempt.user_id)
        .where(QuizAttempt.quiz_id == quiz_id)
        .order_by(QuizAttempt.score.desc(), QuizAttempt.time_spent.asc())
    )
    if since:
        base_query = base_query.where(QuizAttempt.created_at >= since)

    result = await db.execute(base_query)
    all_rows = result.all()

    seen_users = set()
    best_attempts = []
    for attempt, username in all_rows:
        uid_str = str(attempt.user_id)
        if uid_str not in seen_users:
            seen_users.add(uid_str)
            best_attempts.append((attempt, username))

    total_entries = len(seen_users)
    top_entries = best_attempts[:limit]

    entries = []
    for i, (attempt, username) in enumerate(top_entries):
        percentage = round((attempt.score / attempt.total) * 100, 1) if attempt.total else 0
        entries.append(LeaderboardEntry(
            rank=i + 1,
            username=username,
            user_id=attempt.user_id,
            score=attempt.score,
            total=attempt.total,
            percentage=percentage,
            time_spent=attempt.time_spent,
            created_at=attempt.created_at,
        ))

    current_user_entry = None
    current_user_rank = None
    for rank, (attempt, username) in enumerate(best_attempts, 1):
        if attempt.user_id == user.id:
            percentage = round((attempt.score / attempt.total) * 100, 1) if attempt.total else 0
            current_user_entry = LeaderboardEntry(
                rank=rank,
                username=username,
                user_id=attempt.user_id,
                score=attempt.score,
                total=attempt.total,
                percentage=percentage,
                time_spent=attempt.time_spent,
                created_at=attempt.created_at,
            )
            current_user_rank = rank
            break

    return LeaderboardResponse(
        quiz_id=quiz_id,
        entries=entries,
        total_entries=total_entries,
        current_user_entry=current_user_entry,
        current_user_rank=current_user_rank,
    )
