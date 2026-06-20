import asyncio
import uuid
from sqlalchemy import select
from app.database import get_session_factory, get_engine, Base
from app.models import User, Category, Subcategory, Quiz, Question, BadgeDefinition
from app.auth import hash_password


SEED_CATEGORIES = [
    "Database", "Programming", "Web Development",
    "Networking", "General Knowledge", "Mathematics",
]

SEED_SUBCATEGORIES = {
    "Database": ["SQL", "NoSQL", "ORM", "Schema Design", "Query Optimization"],
    "Programming": ["Python", "JavaScript", "TypeScript", "Go", "Rust"],
    "Web Development": ["HTML/CSS", "React", "Svelte", "Backend", "APIs"],
    "Networking": ["TCP/IP", "DNS", "HTTP", "Security", "Protocols"],
    "General Knowledge": ["Science", "History", "Geography", "Arts", "Sports"],
    "Mathematics": ["Algebra", "Calculus", "Statistics", "Geometry", "Logic"],
}

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
    eng = get_engine()
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with get_session_factory()() as db:
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
        subcats = {}
        for name in SEED_CATEGORIES:
            cat = Category(id=uuid.uuid4(), name=name)
            db.add(cat)
            cats[name] = cat
        await db.flush()

        # Seed subcategories
        for cat_name, sub_names in SEED_SUBCATEGORIES.items():
            for sname in sub_names:
                sc = Subcategory(id=uuid.uuid4(), name=sname, category_id=cats[cat_name].id)
                db.add(sc)
                subcats[sname] = sc
        await db.flush()

        # Seed badges
        badges_data = [
            {"key": "first_quiz", "name": "First Quiz", "description": "Complete your first quiz", "icon": "🎯"},
            {"key": "perfect_score", "name": "Perfect Score", "description": "Get 100% on any quiz", "icon": "💯"},
            {"key": "quiz_creator", "name": "Quiz Creator", "description": "Create 5 quizzes", "icon": "✍️"},
            {"key": "streak_master", "name": "Streak Master", "description": "Maintain a 7-day streak", "icon": "🔥"},
            {"key": "knowledge_seeker", "name": "Knowledge Seeker", "description": "Complete 50 quizzes", "icon": "📚"},
            {"key": "centurion", "name": "Centurion", "description": "Reach level 10", "icon": "🏅"},
        ]
        for b in badges_data:
            existing = await db.execute(select(BadgeDefinition).where(BadgeDefinition.key == b["key"]))
            if not existing.scalar_one_or_none():
                db.add(BadgeDefinition(**b))

        # Seed quiz
        gk_cat = cats["General Knowledge"]
        quiz = Quiz(
            id=uuid.uuid4(),
            title="General Knowledge Quiz",
            description="Test your general knowledge with these questions!",
            category_id=gk_cat.id,
            created_by=users["admin"].id,
        )
        db.add(quiz)
        await db.flush()

        # Seed questions — assign first subcategory of the matching category
        for q in SEED_QUESTIONS:
            cat_name = q.get("category", "General Knowledge")
            cat = cats[cat_name]
            # pick the first subcategory for this category
            first_sub = next((sc for name, sc in subcats.items() if sc.category_id == cat.id), None)
            question = Question(
                id=uuid.uuid4(),
                quiz_id=quiz.id,
                subcategory_id=first_sub.id if first_sub else None,
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
