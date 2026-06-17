from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Question, Quiz, User
from app.schemas import QuestionCreate, QuestionUpdate, QuestionResponse
from app.auth import get_current_user

router = APIRouter(prefix="/api/questions", tags=["questions"])

QUESTION_UPDATE_FIELDS = {"category_id", "type", "text", "options", "answer"}


@router.post("/{quiz_id}", response_model=QuestionResponse, status_code=201)
async def create_question(
    quiz_id: UUID,
    data: QuestionCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    quiz_result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = quiz_result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if quiz.created_by != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    question = Question(
        quiz_id=quiz_id,
        category_id=data.category_id,
        type=data.type,
        text=data.text,
        options=data.options,
        answer=data.answer,
    )
    db.add(question)
    await db.commit()
    await db.refresh(question)
    return question


@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: UUID,
    data: QuestionUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    quiz_result = await db.execute(select(Quiz).where(Quiz.id == question.quiz_id))
    quiz = quiz_result.scalar_one_or_none()
    if not quiz or (quiz.created_by != user.id and user.role != "admin"):
        raise HTTPException(status_code=403, detail="Not authorized")

    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        if field in QUESTION_UPDATE_FIELDS:
            setattr(question, field, value)

    await db.commit()
    await db.refresh(question)
    return question


@router.delete("/{question_id}", status_code=204)
async def delete_question(
    question_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    quiz_result = await db.execute(select(Quiz).where(Quiz.id == question.quiz_id))
    quiz = quiz_result.scalar_one_or_none()
    if not quiz or (quiz.created_by != user.id and user.role != "admin"):
        raise HTTPException(status_code=403, detail="Not authorized")

    await db.delete(question)
    await db.commit()
