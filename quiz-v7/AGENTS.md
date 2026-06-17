# AGENTS.md — quiz-v7

## Architecture

Full-stack monorepo: **FastAPI** (Python) backend + **SvelteKit** (TypeScript) frontend.

```
quiz-v7/
├── backend/    → FastAPI + SQLAlchemy + PostgreSQL
├── frontend/   → SvelteKit + Tailwind + DaisyUI
└── docker-compose.yml
```

## Running

**Docker (fastest):**
```bash
docker-compose up
# Frontend: http://localhost:5173
# Backend: http://localhost:8000/docs
```

**Manual:**
```bash
# Backend
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt && cp .env.example .env
python seed.py  # creates admin/demo users + sample quiz
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend && npm install && npm run dev
```

## Key Commands

```bash
# Backend
uvicorn app.main:app --reload          # dev server
python seed.py                          # seed demo data
python -m pytest tests/ -q             # run tests (uses SQLite aiosqlite)

# Frontend
npm run dev                             # dev server (port 5173)
npm run build                           # production build
npm run check                           # type-check
npm run test                            # run vitest tests
```

## Default Credentials

| User  | Password | Role  |
|-------|----------|-------|
| admin | admin123 | admin |
| demo  | demo123  | user  |

## API Structure

All endpoints prefixed with `/api/`:

| Route | Auth | Purpose |
|-------|------|---------|
| `POST /auth/register` | No | Create account |
| `POST /auth/login` | No | Get JWT token |
| `GET /auth/me` | Yes | Current user |
| `GET /quizzes` | No | List quizzes |
| `POST /quizzes` | Yes | Create quiz |
| `GET /quizzes/{id}` | No | Quiz detail (answers hidden) |
| `GET /quizzes/{id}/manage` | Yes (owner) | Quiz with answers |
| `PUT /quizzes/{id}` | Yes (owner) | Update quiz |
| `DELETE /quizzes/{id}` | Yes (owner) | Delete quiz |
| `POST /questions/{quizId}` | Yes (owner) | Add question |
| `PUT /questions/{id}` | Yes (owner) | Update question |
| `DELETE /questions/{id}` | Yes (owner) | Delete question |
| `GET /categories` | No | List categories |
| `POST /categories` | Admin | Create category |
| `POST /attempts` | Yes | Submit quiz attempt |
| `GET /attempts/mine` | Yes | User's attempt history |
| `GET /attempts/quiz/{id}/stats` | No | Quiz statistics |

## Data Model

- **User**: id, username, email, hashed_password, role (`admin`|`user`)
- **Quiz**: id, title, description, created_by FK
- **Question**: id, quiz_id FK, category_id FK, type, text, options (JSON), answer (JSON)
- **Category**: id, name
- **QuizAttempt**: id, quiz_id FK, user_id FK, answers (JSON), score, total, time_spent

## Frontend Routes

| Path | Page |
|------|------|
| `/` | Landing page |
| `/login` | Login form |
| `/register` | Registration form |
| `/quizzes` | Browse all quizzes |
| `/quizzes/[id]` | Quiz detail + start |
| `/quizzes/[id]/take` | Quiz player (timer, check, skip) |
| `/quizzes/[id]/results` | Score + grade display |
| `/quizzes/[id]/edit` | Edit quiz + manage questions |
| `/dashboard` | User's quizzes + attempt history |
| `/create` | Create new quiz |
| `/docs` | Documentation hub |
| `/docs/developer` | Developer guide |
| `/docs/admin` | Admin guide |
| `/docs/user` | User guide |

## Gotchas

- **Scoring is server-side only** — never trust client-side answer validation for persistence
- **Answers hidden** from `GET /quizzes/{id}` — only exposed via `/manage` endpoint (owner only)
- **JWT stored in localStorage** — token sent via `Authorization: Bearer` header
- **Vite proxy** — frontend proxies `/api/*` to backend in dev mode
- **UUID primary keys** — all IDs are UUIDs, not integers
- **JSON columns** — `options` and `answer` fields are JSON in PostgreSQL
- `npm install` must be run in `frontend/` before dev server starts
- Backend requires PostgreSQL running (use Docker or local install)
