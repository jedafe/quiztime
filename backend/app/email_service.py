import secrets
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.config import get_settings
from app.models import User, EmailToken, Quiz, QuizAttempt

settings = get_settings()


def generate_token(length=64) -> str:
    return secrets.token_urlsafe(length)


async def create_email_token(
    db: AsyncSession,
    user: User,
    token_type: str,
    expires_in_hours: int = 48,
) -> str:
    result = await db.execute(
        select(EmailToken).where(
            EmailToken.user_id == user.id,
            EmailToken.type == token_type,
            EmailToken.used == False,
        )
    )
    for old in result.scalars().all():
        old.used = True

    token = generate_token()
    expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=expires_in_hours)

    et = EmailToken(
        user_id=user.id,
        token=token,
        type=token_type,
        expires_at=expires_at,
    )
    db.add(et)
    await db.commit()
    return token


async def send_email(to: str, subject: str, body: str):
    if not settings.SMTP_HOST:
        return

    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to

    import asyncio
    loop = asyncio.get_event_loop()

    def _send():
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg)

    await loop.run_in_executor(None, _send)


async def send_verification_email(db: AsyncSession, user: User):
    token = await create_email_token(db, user, "verify")
    link = f"{settings.FRONTEND_URL}/verify-email?token={token}"

    body = f"""<h2>Welcome to QuizTime!</h2>
<p>Click the link below to verify your email address:</p>
<p><a href="{link}">{link}</a></p>
<p>This link expires in 48 hours.</p>
<p>If you didn't create an account, ignore this email.</p>"""

    await send_email(user.email, "Verify your QuizTime account", body)


async def send_password_reset_email(db: AsyncSession, user: User):
    token = await create_email_token(db, user, "reset", expires_in_hours=1)
    link = f"{settings.FRONTEND_URL}/reset-password?token={token}"

    body = f"""<h2>Password Reset Request</h2>
<p>Click the link below to reset your password:</p>
<p><a href="{link}">{link}</a></p>
<p>This link expires in 1 hour.</p>
<p>If you didn't request this, ignore this email.</p>"""

    await send_email(user.email, "Reset your QuizTime password", body)
