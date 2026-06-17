# FastAPI Backend Skill

## Overview
This skill covers working with the FastAPI backend in `quiz-v7/backend/`.

## Project Structure
```
backend/
├── app/
│   ├── main.py        # FastAPI app, CORS, route registration
│   ├── config.py      # Pydantic Settings (env-based config)
│   ├── database.py    # SQLAlchemy async engine + session
│   ├── models.py      # SQLAlchemy ORM models
│   ├── schemas.py     # Pydantic request/response schemas
│   ├── auth.py        # JWT creation/validation, password hashing
│   └── routes/
│       ├── auth.py    # POST /register, /login, GET /me
│       ├── quizzes.py # Quiz CRUD + permissions
│       ├── questions.py # Question CRUD
│       ├── categories.py # Category management
│       └── attempts.py # Quiz submission + scoring
├── seed.py            # Demo data seeder
├── requirements.txt
└── Dockerfile
```

## Commands
```bash
# Run dev server
uvicorn app.main:app --reload --port 8000

# Seed demo data (creates tables + sample data)
python seed.py

# Install dependencies
pip install -r requirements.txt
```

## Key Patterns

### Adding a new route
1. Create route function in `app/routes/`
2. Use `Depends(get_db)` for database access
3. Use `Depends(get_current_user)` for auth
4. Register router in `app/main.py`

### Database models
- All models inherit from `app.database.Base`
- Use `UUID` primary keys (import from `sqlalchemy.dialects.postgresql`)
- Relationships defined with `relationship()` back_populates

### Authentication
- JWT tokens via `python-jose`
- Password hashing via `passlib[bcrypt]`
- Token sent in `Authorization: Bearer <token>` header
- `get_current_user` dependency extracts user from token

### Scoring logic (in attempts.py)
```python
# Server-side scoring — never trust client
for q in questions:
    user_answer = data.answers.get(str(q.id), [])
    if sorted(user_answer) == sorted(q.answer):
        score += 1
```

## Environment Variables
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/quiztime
SECRET_KEY=your-secret-key
CORS_ORIGINS=["http://localhost:5173"]
```
