import uuid
import random
import string
import base64
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import ShareLink, QuizAttempt, Quiz, User
from app.schemas import ShareLinkCreate, ShareLinkResponse, ShareLinkDetail
from app.auth import get_current_user

router = APIRouter(prefix="/api/share", tags=["share"])


def generate_share_code(length=12):
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


@router.post("", response_model=ShareLinkResponse, status_code=201)
async def create_share_link(
    data: ShareLinkCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(QuizAttempt).where(
            QuizAttempt.id == data.attempt_id,
            QuizAttempt.user_id == user.id,
        )
    )
    attempt = result.scalar_one_or_none()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    existing = await db.execute(
        select(ShareLink).where(ShareLink.attempt_id == data.attempt_id)
    )
    link = existing.scalar_one_or_none()
    if link:
        return ShareLinkResponse(
            code=link.code,
            share_url=f"/share/{link.code}",
            og_url=f"/api/share/{link.code}/og",
        )

    code = generate_share_code()
    while True:
        check = await db.execute(select(ShareLink).where(ShareLink.code == code))
        if not check.scalar_one_or_none():
            break
        code = generate_share_code()

    link = ShareLink(quiz_id=data.quiz_id, attempt_id=data.attempt_id, code=code)
    db.add(link)
    await db.commit()
    await db.refresh(link)

    return ShareLinkResponse(
        code=link.code,
        share_url=f"/share/{link.code}",
        og_url=f"/api/share/{link.code}/og",
    )


@router.get("/{code}", response_model=ShareLinkDetail)
async def get_share_link(code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ShareLink).where(ShareLink.code == code))
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="Share link not found")

    attempt_result = await db.execute(
        select(QuizAttempt).where(QuizAttempt.id == link.attempt_id)
    )
    attempt = attempt_result.scalar_one_or_none()

    quiz_result = await db.execute(select(Quiz).where(Quiz.id == link.quiz_id))
    quiz = quiz_result.scalar_one_or_none()

    user_result = await db.execute(select(User).where(User.id == attempt.user_id))
    attempt_user = user_result.scalar_one_or_none()

    percentage = round((attempt.score / attempt.total) * 100, 1) if attempt.total else 0

    return ShareLinkDetail(
        quiz_title=quiz.title,
        username=attempt_user.username,
        score=attempt.score,
        total=attempt.total,
        percentage=percentage,
        grade=compute_grade(percentage),
        time_spent=attempt.time_spent,
    )


@router.get("/{code}/og", response_class=HTMLResponse)
async def share_og_page(code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ShareLink).where(ShareLink.code == code))
    link = result.scalar_one_or_none()
    if not link:
        return HTMLResponse("<html><body>Not found</body></html>", status_code=404)

    attempt_result = await db.execute(
        select(QuizAttempt).where(QuizAttempt.id == link.attempt_id)
    )
    attempt = attempt_result.scalar_one_or_none()

    quiz_result = await db.execute(select(Quiz).where(Quiz.id == link.quiz_id))
    quiz = quiz_result.scalar_one_or_none()

    user_result = await db.execute(select(User).where(User.id == attempt.user_id))
    attempt_user = user_result.scalar_one_or_none()

    percentage = round((attempt.score / attempt.total) * 100, 1) if attempt.total else 0
    grade = compute_grade(percentage)

    score_color = "#22c55e" if percentage >= 60 else "#f59e0b" if percentage >= 40 else "#ef4444"

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
      <rect width="1200" height="630" fill="#0f172a" rx="16"/>
      <text x="600" y="120" text-anchor="middle" font-family="system-ui" font-size="48" font-weight="700" fill="#e2e8f0">{quiz.title}</text>
      <text x="600" y="180" text-anchor="middle" font-family="system-ui" font-size="28" fill="#94a3b8">by {attempt_user.username}</text>
      <circle cx="600" cy="340" r="100" fill="none" stroke="{score_color}" stroke-width="12"/>
      <text x="600" y="350" text-anchor="middle" font-family="system-ui" font-size="64" font-weight="800" fill="{score_color}">{percentage}%</text>
      <text x="600" y="390" text-anchor="middle" font-family="system-ui" font-size="24" fill="{score_color}">{grade}</text>
      <text x="600" y="460" text-anchor="middle" font-family="system-ui" font-size="32" fill="#cbd5e1">{attempt.score}/{attempt.total} correct</text>
      <text x="600" y="520" text-anchor="middle" font-family="system-ui" font-size="22" fill="#64748b">Think you can beat this score?</text>
    </svg>'''

    b64 = base64.b64encode(svg.encode()).decode()

    html = f'''<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{attempt_user.username} scored {percentage}% on {quiz.title}</title>
  <meta name="description" content="{attempt_user.username} got {attempt.score}/{attempt.total} ({percentage}%) - {grade}">
  <meta property="og:title" content="{attempt_user.username} scored {percentage}% on {quiz.title}">
  <meta property="og:description" content="{attempt.score}/{attempt.total} correct - Grade: {grade}">
  <meta property="og:image" content="data:image/svg+xml;base64,{b64}">
  <meta property="og:type" content="website">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{attempt_user.username} scored {percentage}% on {quiz.title}">
  <meta name="twitter:description" content="{attempt.score}/{attempt.total} correct - Grade: {grade}">
</head>
<body>
  <h1>{attempt_user.username} scored {percentage}% on {quiz.title}</h1>
  <p>{attempt.score}/{attempt.total} correct - {grade}</p>
  <a href="/share/{code}">View details</a>
</body>
</html>'''
    return HTMLResponse(content=html)
