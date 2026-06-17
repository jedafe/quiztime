import asyncio
import uuid
from app.database import async_session, engine, Base
from app.models import User, Category, Quiz, Question
from app.auth import hash_password


SEED_CATEGORIES = [
    "Database", "Programming", "Web Development",
    "Networking", "General Knowledge", "Mathematics",
]

SEED_USERS = [
    {"username": "admin", "email": "admin@quiztime.com", "password": "admin123", "role": "admin"},
    {"username": "demo", "email": "demo@quiztime.com", "password": "demo123", "role": "user"},
]

SEED_QUESTIONS = [
    {
        "question": "A Thief is also known as___",
        "category": "General Knowledge",
        "type": "multiple",
        "options": ["Criminal", "Armed Robber", "Doctor", "Pirate"],
        "answer": [0, 1, 3],
    },
    {
        "question": "Is Python a programming language?",
        "category": "Programming",
        "type": "true-false",
        "options": ["True", "False"],
        "answer": [0],
    },
    {
        "question": "Who owns Twitter/X?",
        "category": "General Knowledge",
        "type": "single",
        "options": ["Pius", "Elon Musk", "Donald", "Peter"],
        "answer": [1],
    },
    {
        "question": "Who Controls Facebook?",
        "category": "General Knowledge",
        "type": "single",
        "options": ["Mark Zuckerberg", "Friday", "Ben", "Bryan"],
        "answer": [0],
    },
    {
        "question": "What is the name of Nigeria's President?",
        "category": "General Knowledge",
        "type": "single",
        "options": ["Olusegun Obasanjo", "Obafemi Awolowo", "Pius Anyim", "Bola Ahmed Tinubu"],
        "answer": [3],
    },
    {
        "question": "Who is the Founder of Microsoft?",
        "category": "Programming",
        "type": "single",
        "options": ["Richard Bale", "Steve Jobs", "Bill Gates", "Malik Jeffery"],
        "answer": [2],
    },
    {
        "question": "How many days do we have in a leap year?",
        "category": "Mathematics",
        "type": "single",
        "options": ["453 days", "355 days", "366 days", "365 days"],
        "answer": [2],
    },
    {
        "question": "How many weeks in a year?",
        "category": "Mathematics",
        "type": "single",
        "options": ["52", "53", "54", "55"],
        "answer": [0],
    },
    {
        "question": "What is the most popular Programming language in 2024?",
        "category": "Programming",
        "type": "single",
        "options": ["Java", "Javascript", "Python", "Golang"],
        "answer": [1],
    },
    {
        "question": "What does HTML stand for?",
        "category": "Web Development",
        "type": "single",
        "options": [
            "Hyper Text Markup Language",
            "High Tech Modern Language",
            "Hyper Transfer Markup Language",
            "Home Tool Markup Language",
        ],
        "answer": [0],
    },
    {
        "question": "Which of these is a relational database?",
        "category": "Database",
        "type": "single",
        "options": ["MongoDB", "Redis", "PostgreSQL", "Elasticsearch"],
        "answer": [2],
    },
    {
        "question": "Is SQL a programming language?",
        "category": "Database",
        "type": "true-false",
        "options": ["True", "False"],
        "answer": [1],
    },
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        # Seed users
        users = {}
        for u in SEED_USERS:
            user = User(
                id=uuid.uuid4(),
                username=u["username"],
                email=u["email"],
                hashed_password=hash_password(u["password"]),
                role=u["role"],
            )
            db.add(user)
            users[u["username"]] = user
        await db.flush()

        # Seed categories
        cats = {}
        for name in SEED_CATEGORIES:
            cat = Category(id=uuid.uuid4(), name=name)
            db.add(cat)
            cats[name] = cat
        await db.flush()

        # Seed quiz
        quiz = Quiz(
            id=uuid.uuid4(),
            title="General Knowledge Quiz",
            description="Test your general knowledge with these questions!",
            created_by=users["admin"].id,
        )
        db.add(quiz)
        await db.flush()

        # Seed questions
        for q in SEED_QUESTIONS:
            question = Question(
                id=uuid.uuid4(),
                quiz_id=quiz.id,
                category_id=cats.get(q["category"], cats["General Knowledge"]).id,
                type=q["type"],
                text=q["question"],
                options=q["options"],
                answer=q["answer"],
            )
            db.add(question)

        await db.commit()
        print("Seed complete!")
        print("  Admin: admin / admin123")
        print("  Demo:  demo / demo123")


if __name__ == "__main__":
    asyncio.run(seed())
