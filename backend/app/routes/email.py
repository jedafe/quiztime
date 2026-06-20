from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User, EmailToken
from app.schemas import (
    EmailVerificationRequest, PasswordResetRequest,
    PasswordResetConfirm, MessageResponse,
)
from app.auth import hash_password, get_current_user, require_admin
from app.email_service import send_verification_email, send_password_reset_email

router = APIRouter(prefix="/api/email", tags=["email"])


@router.post("/verify", response_model=MessageResponse)
async def verify_email(
    data: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(EmailToken).where(
            EmailToken.token == data.token,
            EmailToken.type == "verify",
            EmailToken.used == False,
        )
    )
    token_record = result.scalar_one_or_none()
    if not token_record:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")

    if datetime.now(timezone.utc).replace(tzinfo=None) > token_record.expires_at:
        raise HTTPException(status_code=400, detail="Token expired")

    token_record.used = True
    user_result = await db.execute(select(User).where(User.id == token_record.user_id))
    user = user_result.scalar_one_or_none()
    user.email_verified = True
    await db.commit()

    return MessageResponse(message="Email verified successfully")


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.email_verified:
        raise HTTPException(status_code=400, detail="Email already verified")
    await send_verification_email(db, user)
    return MessageResponse(message="Verification email sent")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if user:
        await send_password_reset_email(db, user)

    return MessageResponse(message="If the email exists, a reset link has been sent")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(EmailToken).where(
            EmailToken.token == data.token,
            EmailToken.type == "reset",
            EmailToken.used == False,
        )
    )
    token_record = result.scalar_one_or_none()
    if not token_record:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    if datetime.now(timezone.utc).replace(tzinfo=None) > token_record.expires_at:
        raise HTTPException(status_code=400, detail="Token expired")

    token_record.used = True
    user_result = await db.execute(select(User).where(User.id == token_record.user_id))
    user = user_result.scalar_one_or_none()
    user.hashed_password = hash_password(data.new_password)
    await db.commit()

    return MessageResponse(message="Password reset successfully")
