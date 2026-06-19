from pydantic import BaseModel, EmailStr, Field, model_validator
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal


# ── Auth ──────────────────────────────────────────────
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ── Category ──────────────────────────────────────────
class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class CategoryResponse(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True


# ── Question ──────────────────────────────────────────
class QuestionCreate(BaseModel):
    category_id: Optional[UUID] = None
    type: Literal["single", "multiple", "true-false"] = "single"
    text: str = Field(min_length=1)
    options: list[str] = Field(min_length=2)
    answer: list[int] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_answer_indices(self):
        for idx in self.answer:
            if idx < 0 or idx >= len(self.options):
                raise ValueError(f"Answer index {idx} is out of bounds for {len(self.options)} options")
        if self.type == "true-false" and len(self.options) != 2:
            raise ValueError("True/false questions must have exactly 2 options")
        if self.type == "true-false" and set(self.options) != {"True", "False"}:
            raise ValueError("True/false options must be 'True' and 'False'")
        return self


class QuestionUpdate(BaseModel):
    category_id: Optional[UUID] = None
    type: Optional[Literal["single", "multiple", "true-false"]] = None
    text: Optional[str] = None
    options: Optional[list[str]] = None
    answer: Optional[list[int]] = None


class QuestionResponse(BaseModel):
    id: UUID
    quiz_id: UUID
    category_id: Optional[UUID]
    type: str
    text: str
    options: list[str]
    answer: list[int]

    class Config:
        from_attributes = True


class QuestionPublic(BaseModel):
    """Question without answer for quiz browsing."""
    id: UUID
    type: str
    text: str
    options: list[str]

    class Config:
        from_attributes = True


# ── Quiz ──────────────────────────────────────────────
class QuizCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = ""


class QuizUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class QuizResponse(BaseModel):
    id: UUID
    title: str
    description: str
    created_by: UUID
    created_at: datetime
    question_count: int = 0

    class Config:
        from_attributes = True


class QuizDetail(BaseModel):
    id: UUID
    title: str
    description: str
    created_by: UUID
    created_at: datetime
    questions: list[QuestionPublic] = []

    class Config:
        from_attributes = True


class QuizWithAnswers(BaseModel):
    """Full quiz with answers (for owner/admin/taking)."""
    id: UUID
    title: str
    description: str
    created_by: UUID
    created_at: datetime
    questions: list[QuestionResponse] = []

    class Config:
        from_attributes = True


# ── Attempt ───────────────────────────────────────────
class AttemptSubmit(BaseModel):
    quiz_id: UUID
    answers: dict[str, list[int]] = {}
    time_spent: int = Field(default=0, ge=0)
    challenge_code: Optional[str] = None


class AttemptResponse(BaseModel):
    id: UUID
    quiz_id: UUID
    user_id: UUID
    score: int
    total: int
    time_spent: int
    answers: dict
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedQuizzes(BaseModel):
    items: list[QuizResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class QuizStats(BaseModel):
    total_attempts: int
    avg_score: float
    avg_percentage: float
    best_score: int


# ── Share ──────────────────────────────────────────────
class ShareLinkCreate(BaseModel):
    quiz_id: UUID
    attempt_id: UUID


class ShareLinkResponse(BaseModel):
    code: str
    share_url: str
    og_url: str


class ShareLinkDetail(BaseModel):
    quiz_title: str
    username: str
    score: int
    total: int
    percentage: float
    grade: str
    time_spent: int

    class Config:
        from_attributes = True


# ── Challenge ──────────────────────────────────────────
class ChallengeCreate(BaseModel):
    quiz_id: UUID
    score_to_beat: int
    total_questions: int
    challenger_attempt_id: UUID


class ChallengeResponse(BaseModel):
    id: UUID
    quiz_id: UUID
    quiz_title: str = ""
    challenger_username: str = ""
    score_to_beat: int
    total_questions: int
    challenge_code: str
    status: str
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class ChallengeResult(BaseModel):
    challenger_username: str
    challenger_score: int
    challenger_total: int
    challenger_percentage: float
    challenger_time: int
    challengee_username: Optional[str] = None
    challengee_score: Optional[int] = None
    challengee_total: Optional[int] = None
    challengee_percentage: Optional[float] = None
    challengee_time: Optional[int] = None
    winner: Optional[str] = None
    status: str


# ── Leaderboard ────────────────────────────────────────
class LeaderboardEntry(BaseModel):
    rank: int
    username: str
    user_id: UUID
    score: int
    total: int
    percentage: float
    time_spent: int
    created_at: datetime


class LeaderboardResponse(BaseModel):
    quiz_id: UUID
    entries: list[LeaderboardEntry]
    total_entries: int
    current_user_entry: Optional[LeaderboardEntry] = None
    current_user_rank: Optional[int] = None
