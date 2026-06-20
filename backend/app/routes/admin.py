from datetime import datetime, timezone, timedelta
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import User, Quiz, Question, QuizAttempt, Category, Subcategory, BadgeDefinition, UserBadge, Rating
from app.schemas import UserResponse, QuizResponse
from app.auth import require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/stats")
async def admin_stats(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)

    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar() or 0

    total_quizzes_result = await db.execute(select(func.count(Quiz.id)))
    total_quizzes = total_quizzes_result.scalar() or 0

    total_attempts_result = await db.execute(select(func.count(QuizAttempt.id)))
    total_attempts = total_attempts_result.scalar() or 0

    dau_result = await db.execute(
        select(func.count(func.distinct(QuizAttempt.user_id)))
        .where(QuizAttempt.created_at >= today_start)
    )
    dau = dau_result.scalar() or 0

    wau_result = await db.execute(
        select(func.count(func.distinct(QuizAttempt.user_id)))
        .where(QuizAttempt.created_at >= week_ago)
    )
    wau = wau_result.scalar() or 0

    return {
        "total_users": total_users,
        "total_quizzes": total_quizzes,
        "total_attempts": total_attempts,
        "daily_active_users": dau,
        "weekly_active_users": wau,
    }


@router.get("/users")
async def admin_list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    offset = (page - 1) * page_size

    count_result = await db.execute(select(func.count(User.id)))
    total = count_result.scalar() or 0

    result = await db.execute(
        select(User).order_by(User.created_at.desc()).offset(offset).limit(page_size)
    )
    users = result.scalars().all()

    return {
        "items": [
            UserResponse(
                id=u.id, username=u.username, email=u.email,
                role=u.role, created_at=u.created_at, email_verified=u.email_verified,
            )
            for u in users
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, -(-total // page_size)),
    }


@router.patch("/users/{user_id}/role")
async def admin_change_role(
    user_id: UUID,
    role: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    if role not in ("admin", "user"):
        raise HTTPException(status_code=400, detail="Invalid role")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if str(user.id) == str(admin.id):
        raise HTTPException(status_code=400, detail="Cannot change your own role")

    user.role = role
    await db.commit()
    return {"message": f"User role updated to {role}"}


@router.get("/top-quizzes")
async def admin_top_quizzes(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    attempt_count_subq = (
        select(func.count(QuizAttempt.id).label("cnt"))
        .where(QuizAttempt.quiz_id == Quiz.id)
        .correlate(Quiz)
        .scalar_subquery()
    )

    result = await db.execute(
        select(Quiz, User.username, attempt_count_subq.label("attempt_count"))
        .join(User, User.id == Quiz.created_by)
        .order_by(attempt_count_subq.desc().nullslast())
        .limit(limit)
    )

    return [
        {
            "id": str(quiz.id),
            "title": quiz.title,
            "creator_username": username,
            "attempt_count": acount or 0,
            "created_at": quiz.created_at.isoformat() if quiz.created_at else None,
        }
        for quiz, username, acount in result.all()
    ]


@router.get("/top-creators")
async def admin_top_creators(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    quiz_count_subq = (
        select(func.count(Quiz.id))
        .where(Quiz.created_by == User.id)
        .correlate(User)
        .scalar_subquery()
    )

    total_attempts_on_quizzes_subq = (
        select(func.count(QuizAttempt.id))
        .where(
            QuizAttempt.quiz_id.in_(
                select(Quiz.id).where(Quiz.created_by == User.id)
            )
        )
        .correlate(User)
        .scalar_subquery()
    )

    result = await db.execute(
        select(
            User.id,
            User.username,
            User.xp,
            quiz_count_subq.label("quiz_count"),
            total_attempts_on_quizzes_subq.label("total_attempts"),
        )
        .order_by(quiz_count_subq.desc().nullslast())
        .limit(limit)
    )

    return [
        {
            "user_id": str(row.id),
            "username": row.username,
            "xp": row.xp or 0,
            "quiz_count": row.quiz_count or 0,
            "total_attempts": row.total_attempts or 0,
        }
        for row in result.all()
    ]


# ===== Admin Categories CRUD =====


@router.get("/categories")
async def admin_list_categories(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    result = await db.execute(select(Category).order_by(Category.name))
    return [{"id": str(c.id), "name": c.name} for c in result.scalars().all()]


@router.post("/categories")
async def admin_create_category(
    data: dict,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    existing = await db.execute(select(Category).where(Category.name == data["name"]))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Category already exists")
    cat = Category(name=data["name"])
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return {"id": str(cat.id), "name": cat.name}


@router.put("/categories/{category_id}")
async def admin_update_category(
    category_id: UUID,
    data: dict,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    result = await db.execute(select(Category).where(Category.id == category_id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    if "name" in data:
        cat.name = data["name"]
    await db.commit()
    await db.refresh(cat)
    return {"id": str(cat.id), "name": cat.name}


@router.delete("/categories/{category_id}")
async def admin_delete_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    result = await db.execute(select(Category).where(Category.id == category_id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    await db.execute(Subcategory.__table__.delete().where(Subcategory.category_id == category_id))
    await db.delete(cat)
    await db.commit()
    return {"message": "Category deleted"}


# ===== Admin Subcategories CRUD =====


@router.get("/subcategories")
async def admin_list_subcategories(
    category_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    q = select(Subcategory)
    if category_id:
        q = q.where(Subcategory.category_id == category_id)
    q = q.order_by(Subcategory.name)
    result = await db.execute(q)
    return [{"id": str(s.id), "name": s.name, "category_id": str(s.category_id)} for s in result.scalars().all()]


@router.post("/subcategories")
async def admin_create_subcategory(
    data: dict,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    sub = Subcategory(name=data["name"], category_id=UUID(data["category_id"]))
    db.add(sub)
    await db.commit()
    await db.refresh(sub)
    return {"id": str(sub.id), "name": sub.name, "category_id": str(sub.category_id)}


@router.put("/subcategories/{subcategory_id}")
async def admin_update_subcategory(
    subcategory_id: UUID,
    data: dict,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    result = await db.execute(select(Subcategory).where(Subcategory.id == subcategory_id))
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    if "name" in data:
        sub.name = data["name"]
    if "category_id" in data:
        sub.category_id = UUID(data["category_id"])
    await db.commit()
    await db.refresh(sub)
    return {"id": str(sub.id), "name": sub.name, "category_id": str(sub.category_id)}


@router.delete("/subcategories/{subcategory_id}")
async def admin_delete_subcategory(
    subcategory_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    result = await db.execute(select(Subcategory).where(Subcategory.id == subcategory_id))
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    await db.delete(sub)
    await db.commit()
    return {"message": "Subcategory deleted"}


# ===== Admin Badge Definitions CRUD =====


@router.get("/badge-definitions")
async def admin_list_badge_definitions(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    result = await db.execute(select(BadgeDefinition).order_by(BadgeDefinition.name))
    return [
        {
            "id": str(b.id),
            "key": b.key,
            "name": b.name,
            "description": b.description,
            "icon": b.icon,
        }
        for b in result.scalars().all()
    ]


@router.post("/badge-definitions")
async def admin_create_badge_definition(
    data: dict,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    bdg = BadgeDefinition(
        key=data["key"],
        name=data["name"],
        description=data.get("description", ""),
        icon=data.get("icon", ""),
    )
    db.add(bdg)
    await db.commit()
    await db.refresh(bdg)
    return {
        "id": str(bdg.id),
        "key": bdg.key,
        "name": bdg.name,
        "description": bdg.description,
        "icon": bdg.icon,
    }


@router.put("/badge-definitions/{badge_id}")
async def admin_update_badge_definition(
    badge_id: UUID,
    data: dict,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    result = await db.execute(select(BadgeDefinition).where(BadgeDefinition.id == badge_id))
    bdg = result.scalar_one_or_none()
    if not bdg:
        raise HTTPException(status_code=404, detail="Badge definition not found")
    if "key" in data:
        bdg.key = data["key"]
    if "name" in data:
        bdg.name = data["name"]
    if "description" in data:
        bdg.description = data["description"]
    if "icon" in data:
        bdg.icon = data["icon"]
    await db.commit()
    await db.refresh(bdg)
    return {
        "id": str(bdg.id),
        "key": bdg.key,
        "name": bdg.name,
        "description": bdg.description,
        "icon": bdg.icon,
    }


@router.delete("/badge-definitions/{badge_id}")
async def admin_delete_badge_definition(
    badge_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    result = await db.execute(select(BadgeDefinition).where(BadgeDefinition.id == badge_id))
    bdg = result.scalar_one_or_none()
    if not bdg:
        raise HTTPException(status_code=404, detail="Badge definition not found")
    await db.execute(UserBadge.__table__.delete().where(UserBadge.badge_id == badge_id))
    await db.delete(bdg)
    await db.commit()
    return {"message": "Badge definition deleted"}


# ===== Admin Attempts (read-only) =====


@router.get("/attempts")
async def admin_list_attempts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    quiz_id: UUID | None = None,
    user_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    q = select(QuizAttempt)
    if quiz_id:
        q = q.where(QuizAttempt.quiz_id == quiz_id)
    if user_id:
        q = q.where(QuizAttempt.user_id == user_id)

    count_q = select(func.count()).select_from(q.subquery())
    count_result = await db.execute(count_q)
    total = count_result.scalar() or 0

    offset = (page - 1) * page_size
    q = q.order_by(QuizAttempt.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(q)
    attempts = result.scalars().all()

    items = []
    for att in attempts:
        user_result = await db.execute(select(User.username).where(User.id == att.user_id))
        username = user_result.scalar() or "unknown"
        quiz_result = await db.execute(select(Quiz.title).where(Quiz.id == att.quiz_id))
        quiz_title = quiz_result.scalar() or "unknown"
        items.append({
            "id": str(att.id),
            "quiz_id": str(att.quiz_id),
            "user_id": str(att.user_id),
            "username": username,
            "quiz_title": quiz_title,
            "score": att.score,
            "total": att.total,
            "time_spent": att.time_spent,
            "created_at": att.created_at.isoformat() if att.created_at else None,
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, -(-total // page_size)),
    }


# ===== Admin Quiz Management =====


@router.get("/quizzes")
async def admin_list_all_quizzes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    offset = (page - 1) * page_size

    count_result = await db.execute(select(func.count(Quiz.id)))
    total = count_result.scalar() or 0

    result = await db.execute(
        select(Quiz, User.username)
        .join(User, User.id == Quiz.created_by)
        .order_by(Quiz.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    rows = result.all()

    return {
        "items": [
            {
                "id": str(quiz.id),
                "title": quiz.title,
                "description": quiz.description,
                "creator_username": username,
                "created_by": str(quiz.created_by),
                "category_id": str(quiz.category_id) if quiz.category_id else None,
                "language": quiz.language or "en",
                "created_at": quiz.created_at.isoformat() if quiz.created_at else None,
            }
            for quiz, username in rows
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, -(-total // page_size)),
    }


@router.delete("/quizzes/{quiz_id}")
async def admin_delete_any_quiz(
    quiz_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    await db.execute(Question.__table__.delete().where(Question.quiz_id == quiz_id))
    await db.execute(QuizAttempt.__table__.delete().where(QuizAttempt.quiz_id == quiz_id))
    await db.execute(Rating.__table__.delete().where(Rating.quiz_id == quiz_id))
    await db.delete(quiz)
    await db.commit()
    return {"message": "Quiz deleted"}
