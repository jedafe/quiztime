import math
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import Quiz, Question, User
from app.schemas import QuizCreate, QuizUpdate, QuizResponse, QuizDetail, QuizWithAnswers, QuestionPublic, PaginatedQuizzes
from app.auth import get_current_user, require_admin

router = APIRouter(prefix="/api/quizzes", tags=["quizzes"])


@router.get("", response_model=PaginatedQuizzes)
async def list_quizzes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size

    # Total count
    count_q = await db.execute(select(func.count(Quiz.id)))
    total = count_q.scalar() or 0

    result = await db.execute(
        select(Quiz, func.count(Question.id).label("question_count"))
        .outerjoin(Question)
        .group_by(Quiz.id)
        .order_by(Quiz.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    items = [
        QuizResponse(
            id=quiz.id,
            title=quiz.title,
            description=quiz.description,
            created_by=quiz.created_by,
            created_at=quiz.created_at,
            question_count=count,
        )
        for quiz, count in result.all()
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
    quiz = Quiz(title=data.title, description=data.description, created_by=user.id)
    db.add(quiz)
    await db.commit()
    await db.refresh(quiz)
    return QuizResponse(
        id=quiz.id, title=quiz.title, description=quiz.description,
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

    return QuizDetail(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        created_by=quiz.created_by,
        created_at=quiz.created_at,
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
        created_at=quiz.created_at,
        questions=questions,
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

    await db.commit()
    await db.refresh(quiz)

    count_result = await db.execute(
        select(func.count(Question.id)).where(Question.quiz_id == quiz_id)
    )
    count = count_result.scalar() or 0

    return QuizResponse(
        id=quiz.id, title=quiz.title, description=quiz.description,
        created_by=quiz.created_by, created_at=quiz.created_at, question_count=count,
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
