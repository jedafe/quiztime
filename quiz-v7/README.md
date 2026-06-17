# QuizTime v7

Full-stack quiz application built with FastAPI + SvelteKit.

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### Option 1: Docker (Recommended)

```bash
docker-compose up
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/docs
- Database: localhost:5432

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your DATABASE_URL
python seed.py  # Seeds demo data
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Default Users

| User  | Password | Role  |
|-------|----------|-------|
| admin | admin123 | admin |
| demo  | demo123  | user  |

## API Docs

Visit http://localhost:8000/docs for interactive Swagger documentation.

## Project Structure

```
quiz-v7/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app + CORS
│   │   ├── config.py        # Settings (env-based)
│   │   ├── database.py      # SQLAlchemy async engine
│   │   ├── models.py        # DB models (User, Quiz, Question, etc.)
│   │   ├── schemas.py       # Pydantic request/response schemas
│   │   ├── auth.py          # JWT auth + password hashing
│   │   └── routes/          # API endpoints
│   │       ├── auth.py      # Register, login, /me
│   │       ├── quizzes.py   # Quiz CRUD
│   │       ├── questions.py # Question CRUD
│   │       ├── categories.py# Category management
│   │       └── attempts.py  # Quiz submission + stats
│   ├── seed.py              # Seed demo data
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── routes/          # SvelteKit pages
│   │   ├── lib/
│   │   │   ├── api.ts       # API client
│   │   │   └── stores/      # Svelte stores (auth)
│   │   └── app.html
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml
```

## Features

- Quiz taking with countdown timer
- Single, multiple, and true/false question types
- Server-side scoring (tamper-proof)
- User authentication (JWT)
- Role-based access (admin/user)
- Quiz creation and management
- Attempt history and statistics
