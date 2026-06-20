# AGENTS.md — quiz-v7

## Feature Roadmap

See [FEATURES.md](./FEATURES.md) for the full planned feature roadmap. Each feature has a detailed implementation skill file in `.config/opencode/skills/`.

| Priority | Feature | Skill File |
|----------|---------|------------|
| Tier 1 | Share & Challenge System | `share-challenge-feature.md` |
| Tier 1 | Public Leaderboards | `leaderboard-feature.md` |
| Tier 2 | Search, Filtering & Sorting | `search-filter-sort-feature.md` |
| Tier 2 | Ratings & Reviews | `ratings-reviews-feature.md` |
| Tier 3 | Gamification (XP/Badges) | `gamification-xp-badges-feature.md` |
| Tier 3 | Email System | `email-system-feature.md` |
| Tier 4 | Embeddable Quizzes | — |
| Tier 4 | Quiz Import/Export | — |
| Tier 5 | Multi-Language / i18n | — |
| Tier 5 | Admin Dashboard | — |

## Architecture

Full-stack monorepo: **FastAPI** (Python) backend + **SvelteKit** (TypeScript) frontend.

```
.
├── backend/    → FastAPI + SQLAlchemy + PostgreSQL
├── frontend/   → SvelteKit + Tailwind + Skeleton
├── dev.sh      → Development server control
├── start.sh    → Production server control
└── docker-compose.yml
```

## Running

**Development (one command):**
```bash
./dev.sh              # start dev servers
./dev.sh stop         # stop dev servers
./dev.sh restart      # restart dev servers
./dev.sh status       # check if running
# Frontend: http://localhost:5173 (Vite HMR)
# Backend:  http://localhost:8000/docs (hot-reload)
```

**Production (one command):**
```bash
./start.sh            # build + start prod servers
./start.sh stop       # stop prod servers
./start.sh restart    # restart prod servers
./start.sh status     # check if running
# Frontend: http://localhost:4173 (built)
# Backend:  http://localhost:8000/docs (4 workers)
```

**Docker (fastest):**
```bash
docker-compose up
# Frontend: http://localhost:5173
# Backend:  http://localhost:8000/docs
```

**Manual (for reference):**
```bash
# Backend
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt && cp .env.example .env
python seed.py  # creates admin/demo users + sample quiz
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend && npm install && npm run dev
```

## Key Commands

```bash
# Backend
uvicorn app.main:app --reload --port 8000  # dev server
python seed.py                              # seed demo data
python -m pytest tests/ -q                 # run tests (uses SQLite aiosqlite)

# Frontend
npm run dev               # dev server (port 5173, Vite HMR)
npm run build             # production build
npm run check             # type-check
npm run test              # run vitest tests
npm run preview           # preview production build (port 4173)
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
| `GET /quizzes` | No | List quizzes (paginated) |
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
| `POST /email/verify` | No | Verify email with token |
| `POST /email/resend-verification` | Yes | Resend verification email |
| `POST /email/forgot-password` | No | Request password reset |
| `POST /email/reset-password` | No | Reset password with token |
| `GET /gamification/my-profile` | Yes | Current user's XP/profile/streak |
| `GET /gamification/profile/{id}` | No | Any user's gamification profile |
| `GET /gamification/xp-history` | Yes | Paginated XP event history |
| `GET /gamification/badges` | No | All badges with earned status |
| `GET /gamification/leaderboard` | No | XP leaderboard (top users) |

## Data Model

- **User**: id, username, email, hashed_password, role (`admin`|`user`), xp, level, streak_count, last_activity_date, email_verified
- **Quiz**: id, title, description, created_by FK
- **Question**: id, quiz_id FK, category_id FK, type, text, options (JSON), answer (JSON)
- **Category**: id, name
- **QuizAttempt**: id, quiz_id FK, user_id FK, answers (JSON), score, total, time_spent
- **BadgeDefinition**: id, name, description, icon, criteria (JSON)
- **UserBadge**: user_id FK, badge_id FK, earned_at
- **XpEvent**: id, user_id FK, source, amount, created_at
- **EmailToken**: id, user_id FK, token, type, expires_at, used

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
| `/dashboard` | User's quizzes + attempt history + XP profile card |
| `/achievements` | Badges gallery + XP history + level progress |
| `/create` | Create new quiz |
| `/verify-email` | Email verification (accepts `?token=`) |
| `/forgot-password` | Request password reset |
| `/reset-password` | Reset password (accepts `?token=`) |
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
- **Pagination** — `GET /quizzes` returns `{items, total, page, page_size, total_pages}`
- `npm install` must be run in `frontend/` before dev server starts
- Backend requires PostgreSQL running (use Docker or local install)
