import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Integer, Float, ForeignKey, DateTime, JSON, Index, Boolean
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"


class QuestionType(str, enum.Enum):
    single = "single"
    multiple = "multiple"
    true_false = "true-false"


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default=UserRole.user, nullable=False)
    created_at = Column(DateTime, default=utcnow)
    xp = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=1, nullable=False)
    streak_count = Column(Integer, default=0, nullable=False)
    last_activity_date = Column(DateTime, nullable=True)
    email_verified = Column(Boolean, default=False, nullable=False)

    quizzes = relationship("Quiz", back_populates="owner", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="user", cascade="all, delete-orphan")
    badges = relationship("UserBadge", back_populates="user", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)

    subcategories = relationship("Subcategory", back_populates="category", cascade="all, delete-orphan")


class Subcategory(Base):
    __tablename__ = "subcategories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)

    category = relationship("Category", back_populates="subcategories")
    questions = relationship("Question", back_populates="subcategory")


class Quiz(Base):
    __tablename__ = "quizzes"
    __table_args__ = (
        Index("ix_quizzes_created_by", "created_by"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    language = Column(String(10), default="en", nullable=False)
    created_at = Column(DateTime, default=utcnow)

    owner = relationship("User", back_populates="quizzes")
    category = relationship("Category")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="quiz", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"
    __table_args__ = (
        Index("ix_questions_quiz_id", "quiz_id"),
        Index("ix_questions_subcategory_id", "subcategory_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=False)
    subcategory_id = Column(UUID(as_uuid=True), ForeignKey("subcategories.id"), nullable=True)
    type = Column(String(20), nullable=False, default=QuestionType.single)
    text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)
    answer = Column(JSON, nullable=False)

    quiz = relationship("Quiz", back_populates="questions")
    subcategory = relationship("Subcategory", back_populates="questions")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    __table_args__ = (
        Index("ix_quiz_attempts_quiz_id", "quiz_id"),
        Index("ix_quiz_attempts_user_id", "user_id"),
        Index("ix_quiz_attempts_score_desc", "quiz_id", "score", "time_spent"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    answers = Column(JSON, nullable=False, default=list)
    score = Column(Integer, nullable=False, default=0)
    total = Column(Integer, nullable=False, default=0)
    time_spent = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=utcnow)

    quiz = relationship("Quiz", back_populates="attempts")
    user = relationship("User", back_populates="attempts")


class ShareLink(Base):
    __tablename__ = "share_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=False)
    attempt_id = Column(UUID(as_uuid=True), ForeignKey("quiz_attempts.id"), nullable=False)
    code = Column(String(12), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=utcnow)

    quiz = relationship("Quiz")
    attempt = relationship("QuizAttempt")


class ChallengeStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    completed = "completed"
    expired = "expired"


class Rating(Base):
    __tablename__ = "ratings"
    __table_args__ = (
        Index("ix_ratings_quiz_id", "quiz_id"),
        Index("ix_ratings_user_id", "user_id"),
        Index("ix_ratings_quiz_user", "quiz_id", "user_id", unique=True),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    score = Column(Integer, nullable=False)
    review = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    quiz = relationship("Quiz", back_populates="ratings")
    user = relationship("User")


class BadgeDefinition(Base):
    __tablename__ = "badge_definitions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)
    icon = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=utcnow)

    awards = relationship("UserBadge", back_populates="badge")


class UserBadge(Base):
    __tablename__ = "user_badges"
    __table_args__ = (
        Index("ix_user_badges_user_id", "user_id"),
        Index("ix_user_badges_user_badge", "user_id", "badge_id", unique=True),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    badge_id = Column(UUID(as_uuid=True), ForeignKey("badge_definitions.id"), nullable=False)
    earned_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="badges")
    badge = relationship("BadgeDefinition", back_populates="awards")


class XpEvent(Base):
    __tablename__ = "xp_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    source = Column(String(50), nullable=False)
    amount = Column(Integer, nullable=False)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=True)
    attempt_id = Column(UUID(as_uuid=True), ForeignKey("quiz_attempts.id"), nullable=True)
    created_at = Column(DateTime, default=utcnow)


class EmailToken(Base):
    __tablename__ = "email_tokens"
    __table_args__ = (
        Index("ix_email_tokens_user_id", "user_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token = Column(String(128), unique=True, nullable=False, index=True)
    type = Column(String(20), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    user = relationship("User")


class EmbedSubmission(Base):
    __tablename__ = "embed_submissions"
    __table_args__ = (
        Index("ix_embed_submissions_quiz_id", "quiz_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=False)
    submission_name = Column(String(100), default="")
    answers = Column(JSON, nullable=False, default=dict)
    score = Column(Integer, nullable=False, default=0)
    total = Column(Integer, nullable=False, default=0)
    time_spent = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=utcnow)

    quiz = relationship("Quiz")


class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=False)
    challenger_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    score_to_beat = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    challenger_attempt_id = Column(UUID(as_uuid=True), ForeignKey("quiz_attempts.id"), nullable=True)
    challengee_attempt_id = Column(UUID(as_uuid=True), ForeignKey("quiz_attempts.id"), nullable=True)
    challenge_code = Column(String(12), unique=True, nullable=False, index=True)
    status = Column(String(20), default=ChallengeStatus.pending, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    quiz = relationship("Quiz")
    challenger = relationship("User", foreign_keys=[challenger_id])
    challenger_attempt = relationship("QuizAttempt", foreign_keys=[challenger_attempt_id])
    challengee_attempt = relationship("QuizAttempt", foreign_keys=[challengee_attempt_id])
