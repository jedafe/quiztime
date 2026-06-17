from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/quiztime"
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    if s.SECRET_KEY == "change-this-in-production":
        import os
        if os.getenv("ENVIRONMENT", "development") == "production":
            raise RuntimeError(
                "SECRET_KEY must be set in production. "
                "Add SECRET_KEY=your-secret to .env"
            )
    return s
