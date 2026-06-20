# QuizTime v7

Full-stack quiz application built with FastAPI + SvelteKit.

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### One-Command Start

**Development** (hot-reload, auto-restart):
```bash
./dev.sh
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000/docs
```

**Production** (built frontend, 4 workers):
```bash
./start.sh
# Frontend: http://localhost:4173
# Backend API: http://localhost:8000/docs
```

**Other commands:**
```bash
./dev.sh stop       # stop dev servers
./dev.sh status     # check if running
./dev.sh restart    # restart dev servers

./start.sh stop     # stop prod servers
./start.sh status   # check if running
./start.sh restart  # restart prod servers
```

### Docker

```bash
docker-compose up
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000/docs
# Database: localhost:5432
```

### Manual Setup

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

## API Endpoints

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | /api/auth/register | No | Create account |
| POST | /api/auth/login | No | Get JWT token |
| GET | /api/auth/me | Yes | Current user |
| GET | /api/quizzes | No | List quizzes (paginated) |
| POST | /api/quizzes | Yes | Create quiz |
| GET | /api/quizzes/{id} | No | Quiz detail (answers hidden) |
| GET | /api/quizzes/{id}/manage | Owner | Quiz with answers |
| GET | /api/quizzes/{id}/leaderboard | Yes | Per-quiz leaderboard |
| PUT | /api/quizzes/{id} | Owner | Update quiz |
| DELETE | /api/quizzes/{id} | Owner | Delete quiz |
| POST | /api/questions/{quizId} | Owner | Add question |
| PUT | /api/questions/{id} | Owner | Update question |
| DELETE | /api/questions/{id} | Owner | Delete question |
| GET | /api/categories | No | List categories |
| POST | /api/categories | Admin | Create category |
| POST | /api/attempts | Yes | Submit quiz attempt |
| GET | /api/attempts/mine | Yes | User's attempt history |
| GET | /api/attempts/{id} | Yes | Get attempt by ID |
| GET | /api/attempts/quiz/{id}/stats | No | Quiz statistics |
| POST | /api/share | Yes | Create share link |
| GET | /api/share/{code} | No | Resolve share link |
| GET | /api/share/{code}/og | No | OG image card HTML |
| POST | /api/challenges | Yes | Create challenge |
| GET | /api/challenges | Yes | List my challenges |
| GET | /api/challenges/{code} | No | Get challenge |
| POST | /api/challenges/{code}/accept | Yes | Accept challenge |
| GET | /api/challenges/{code}/result | No | Challenge comparison result |
| POST | /api/email/verify | No | Verify email with token |
| POST | /api/email/resend-verification | Yes | Resend verification email |
| POST | /api/email/forgot-password | No | Request password reset |
| POST | /api/email/reset-password | No | Reset password with token |
| GET | /api/gamification/my-profile | Yes | Current user's XP/profile/streak |
| GET | /api/gamification/profile/{id} | No | Any user's gamification profile |
| GET | /api/gamification/xp-history | Yes | Paginated XP event history |
| GET | /api/gamification/badges | No | All badges with earned status |
| GET | /api/gamification/leaderboard | No | XP leaderboard (top users) |

Visit http://localhost:8000/docs for interactive Swagger documentation.

## Project Structure

```
.
├── backend/           → FastAPI + SQLAlchemy + PostgreSQL
│   ├── app/
│   │   ├── main.py          # FastAPI app + CORS
│   │   ├── config.py        # Settings (env-based)
│   │   ├── database.py      # SQLAlchemy async engine
│   │   ├── models.py        # DB models (User, Quiz, Question, Badge, etc.)
│   │   ├── schemas.py       # Pydantic request/response schemas
│   │   ├── auth.py          # JWT auth + password hashing
│   │   ├── gamification.py  # XP/streak/badge logic
│   │   ├── email_service.py # Token gen + SMTP email sending
│   │   └── routes/          # API endpoints
│   │       ├── auth.py      # Register, login, /me
│   │       ├── quizzes.py   # Quiz CRUD
│   │       ├── questions.py # Question CRUD
│   │       ├── categories.py# Category management
│   │       ├── attempts.py  # Quiz submission + stats
│   │       ├── share.py     # Share link creation + OG cards
│   │       ├── challenges.py# Challenge system
│   │       ├── gamification.py # XP/profile/badges/leaderboard
│   │       └── email.py     # Verify/resend/forgot/reset
│   ├── seed.py              # Seed demo data
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/          → SvelteKit + Tailwind + Skeleton
│   ├── src/
│   │   ├── routes/          # SvelteKit pages
│   │   │   └── challenge/[code]/  # Challenge landing page
│   │   ├── lib/
│   │   │   ├── api.ts       # API client
│   │   │   └── stores/      # Svelte stores (auth)
│   │   └── app.html
│   ├── package.json
│   └── Dockerfile
├── dev.sh             # Dev server control
├── start.sh           # Production server control
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
- Shareable result links with OG image cards
- Challenge system (score-to-beat, accept, compare results)
- Per-quiz leaderboard with period filtering (today/week/month/all)
- Gamification: XP, levels, daily streak, 6 badges, achievements page
- Email verification and password reset flow
