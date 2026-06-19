from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import Quiz, Rating, User
from app.schemas import RatingCreate, RatingUpdate, RatingResponse, RatingStats
from app.auth import get_current_user

router = APIRouter(prefix="/api/ratings", tags=["ratings"])


@router.post("", response_model=RatingResponse, status_code=201)
async def create_or_update_rating(
    data: RatingCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    quiz_result = await db.execute(select(Quiz).where(Quiz.id == data.quiz_id))
    if not quiz_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Quiz not found")

    result = await db.execute(
        select(Rating).where(
            Rating.quiz_id == data.quiz_id,
            Rating.user_id == user.id,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.score = data.score
        if data.review is not None:
            existing.review = data.review
        await db.commit()
        await db.refresh(existing)
        return RatingResponse(
            id=existing.id,
            quiz_id=existing.quiz_id,
            user_id=existing.user_id,
            username=user.username,
            score=existing.score,
            review=existing.review,
            created_at=existing.created_at,
        )

    rating = Rating(
        quiz_id=data.quiz_id,
        user_id=user.id,
        score=data.score,
        review=data.review,
    )
    db.add(rating)
    await db.commit()
    await db.refresh(rating)
    return RatingResponse(
        id=rating.id,
        quiz_id=rating.quiz_id,
        user_id=rating.user_id,
        username=user.username,
        score=rating.score,
        review=rating.review,
        created_at=rating.created_at,
    )


@router.get("/{quiz_id}", response_model=dict)
async def list_ratings(
    quiz_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    quiz_result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    if not quiz_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Quiz not found")

    offset = (page - 1) * page_size

    count_result = await db.execute(
        select(func.count(Rating.id)).where(Rating.quiz_id == quiz_id)
    )
    total = count_result.scalar() or 0

    result = await db.execute(
        select(Rating, User.username)
        .join(User, User.id == Rating.user_id)
        .where(Rating.quiz_id == quiz_id)
        .order_by(Rating.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )

    items = [
        RatingResponse(
            id=rating.id,
            quiz_id=rating.quiz_id,
            user_id=rating.user_id,
            username=username,
            score=rating.score,
            review=rating.review,
            created_at=rating.created_at,
        )
        for rating, username in result.all()
    ]
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{quiz_id}/stats", response_model=RatingStats)
async def rating_stats(
    quiz_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    quiz_result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    if not quiz_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Quiz not found")

    result = await db.execute(
        select(
            func.coalesce(func.avg(Rating.score), 0),
            func.count(Rating.id),
        ).where(Rating.quiz_id == quiz_id)
    )
    avg, total = result.one()
    avg_rating = round(float(avg), 1)

    dist_result = await db.execute(
        select(Rating.score, func.count(Rating.id))
        .where(Rating.quiz_id == quiz_id)
        .group_by(Rating.score)
        .order_by(Rating.score)
    )
    distribution = {score: count for score, count in dist_result.all()}
    for i in range(1, 6):
        distribution.setdefault(i, 0)

    return RatingStats(
        avg_rating=avg_rating,
        total_ratings=total,
        distribution=distribution,
    )


@router.get("/{quiz_id}/my", response_model=RatingResponse)
async def my_rating(
    quiz_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Rating).where(
            Rating.quiz_id == quiz_id,
            Rating.user_id == user.id,
        )
    )
    rating = result.scalar_one_or_none()
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")

    return RatingResponse(
        id=rating.id,
        quiz_id=rating.quiz_id,
        user_id=rating.user_id,
        username=user.username,
        score=rating.score,
        review=rating.review,
        created_at=rating.created_at,
    )


@router.delete("/{rating_id}", status_code=204)
async def delete_rating(
    rating_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Rating).where(Rating.id == rating_id))
    rating = result.scalar_one_or_none()
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    if rating.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    await db.delete(rating)
    await db.commit()
