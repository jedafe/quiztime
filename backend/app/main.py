from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import get_settings
from app.database import get_engine, Base
from app.routes import auth, quizzes, questions, categories, attempts, share, challenges, ratings, gamification, email

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="QuizTime API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(quizzes.router)
app.include_router(questions.router)
app.include_router(categories.router)
app.include_router(attempts.router)
app.include_router(share.router)
app.include_router(challenges.router)
app.include_router(ratings.router)
app.include_router(gamification.router)
app.include_router(email.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
