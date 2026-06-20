# AGENTS.md — quiz-v7

## Feature Roadmap

See [FEATURES.md](./FEATURES.md) for the full planned feature roadmap. All tiers are implemented.

| Priority | Feature | Status |
|----------|---------|--------|
| Tier 1 | Share & Challenge System | ✅ Implemented |
| Tier 1 | Public Leaderboards | ✅ Implemented |
| Tier 2 | Search, Filtering & Sorting | ✅ Implemented |
| Tier 2 | Ratings & Reviews | ✅ Implemented |
| Tier 3 | Gamification (XP/Badges) | ✅ Implemented |
| Tier 3 | Email System | ✅ Implemented |
| Tier 4 | Embeddable Quizzes | ✅ Implemented |
| Tier 4 | Quiz Import/Export | ✅ Implemented |
| Tier 5 | Multi-Language / i18n | ✅ Implemented |
| Tier 5 | Admin Dashboard | ✅ Implemented |

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
npm run test:e2e          # run Playwright e2e tests (dev servers must be running)
npx playwright test       # run Playwright e2e tests
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
| `GET /quizzes` | No | List quizzes (paginated, filterable) |
| `POST /quizzes` | Yes | Create quiz |
| `GET /quizzes/{id}` | No | Quiz detail (answers hidden) |
| `GET /quizzes/{id}/manage` | Yes (owner) | Quiz with answers |
| `PUT /quizzes/{id}` | Yes (owner) | Update quiz |
| `DELETE /quizzes/{id}` | Yes (owner) | Delete quiz |
| `POST /questions/{quizId}` | Yes (owner) | Add question |
| `PUT /questions/{id}` | Yes (owner) | Update question |
| `DELETE /questions/{id}` | Yes (owner) | Delete question |
| `GET /quizzes/{id}/export` | Yes (owner) | Export quiz as JSON (with answers) |
| `POST /quizzes/import` | Yes | Import quiz from JSON |
| `GET /categories` | No | List categories |
| `POST /categories` | Admin | Create category |
| `GET /categories/subcategories` | No | List subcategories (?category_id=) |
| `POST /attempts` | Yes | Submit quiz attempt |
| `GET /attempts/mine` | Yes | User's attempt history |
| `GET /attempts/quiz/{id}/stats` | No | Quiz statistics |
| `GET /attempts/{id}` | Yes | Get attempt by ID |
| `POST /share` | Yes | Create share link |
| `GET /share/{code}` | No | Resolve share link |
| `GET /share/{code}/og` | No | OG image card HTML |
| `POST /challenges` | Yes | Create challenge |
| `GET /challenges` | Yes | List my challenges |
| `GET /challenges/{code}` | No | Get challenge |
| `POST /challenges/{code}/accept` | Yes | Accept challenge |
| `GET /challenges/{code}/result` | No | Challenge comparison result |
| `POST /email/verify` | No | Verify email with token |
| `POST /email/resend-verification` | Yes | Resend verification email |
| `POST /email/forgot-password` | No | Request password reset |
| `POST /email/reset-password` | No | Reset password with token |
| `GET /gamification/my-profile` | Yes | Current user's XP/profile/streak |
| `GET /gamification/profile/{id}` | No | Any user's gamification profile |
| `GET /gamification/xp-history` | Yes | Paginated XP event history |
| `GET /gamification/badges` | No | All badges with earned status |
| `GET /gamification/leaderboard` | No | XP leaderboard (top users) |
| `GET /embed/{quiz_id}/data` | No | Public quiz data for embed (no answers) |
| `POST /embed/{quiz_id}/submit` | No | Anonymous embed submission with server scoring |
| `GET /embed/{quiz_id}` | No | Self-contained HTML embed widget |
| `GET /embed/{quiz_id}/snippet` | No | iframe embed HTML snippet |
| `GET /embed/{quiz_id}/submissions` | Yes (owner) | List embed submissions |
| `GET /admin/stats` | Admin | Site-wide stats (users, quizzes, attempts, DAU) |
| `GET /admin/users` | Admin | List all users with pagination |
| `PATCH /admin/users/{id}/role` | Admin | Change user role |
| `DELETE /admin/users/{id}` | Admin | Delete user |
| `GET /admin/quizzes` | Admin | List all quizzes site-wide |
| `DELETE /admin/quizzes/{id}` | Admin | Force-delete any quiz |
| `GET /admin/creators` | Admin | Top creators by quiz count |
| `GET /admin/categories` | Admin | List categories |
| `POST /admin/categories` | Admin | Create category |
| `PUT /admin/categories/{id}` | Admin | Update category |
| `DELETE /admin/categories/{id}` | Admin | Delete category |
| `GET /admin/subcategories` | Admin | List subcategories |
| `POST /admin/subcategories` | Admin | Create subcategory |
| `PUT /admin/subcategories/{id}` | Admin | Update subcategory |
| `DELETE /admin/subcategories/{id}` | Admin | Delete subcategory |
| `GET /admin/badge-definitions` | Admin | List badge definitions |
| `POST /admin/badge-definitions` | Admin | Create badge definition |
| `PUT /admin/badge-definitions/{id}` | Admin | Update badge definition |
| `DELETE /admin/badge-definitions/{id}` | Admin | Delete badge definition |
| `GET /admin/attempts` | Admin | List all attempts (paginated, filterable) |

## Data Model

- **User**: id, username, email, hashed_password, role (`admin`|`user`), xp, level, streak_count, last_activity_date, email_verified
- **Quiz**: id, title, description, category_id FK, created_by FK, language (String(10), default "en")
- **Question**: id, quiz_id FK, subcategory_id FK, type, text, options (JSON), answer (JSON)
- **Category**: id, name
- **Subcategory**: id, name, category_id FK
- **QuizAttempt**: id, quiz_id FK, user_id FK, answers (JSON), score, total, time_spent
- **EmbedSubmission**: id, quiz_id FK, submission_name, answers (JSON), score, total, time_spent
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
| `/quizzes` | Browse all quizzes (search, filter, sort, paginate) |
| `/quizzes/[id]` | Quiz detail + start |
| `/quizzes/[id]/take` | Quiz player (timer, check, skip) |
| `/quizzes/[id]/results` | Score + grade display |
| `/quizzes/[id]/edit` | Edit quiz + manage questions |
| `/dashboard` | User's quizzes + attempt history + XP profile card |
| `/achievements` | Badges gallery + XP history + level progress |
| `/create` | Create new quiz |
| `/challenge/[code]` | Challenge landing (score-to-beat, accept) |
| `/verify-email` | Email verification (accepts `?token=`) |
| `/forgot-password` | Request password reset |
| `/reset-password` | Reset password (accepts `?token=`) |
| `/docs` | Documentation hub |
| `/docs/developer` | Developer guide |
| `/docs/admin` | Admin guide |
| `/docs/user` | User guide |
| `/admin` | Admin dashboard (8 tabs: overview, users, quizzes, creators, categories, subcategories, badges, attempts) |

## i18n System

- **3 locales**: English (`en`), Spanish (`es`), French (`fr`)
- **Store**: `frontend/src/lib/stores/i18n.ts` — writable `locale` + derived `$translate()` function
- **Locale files**: `frontend/src/lib/i18n/en.ts`, `es.ts`, `fr.ts` (~450 lines each, 22 namespace sections)
- **Usage**: `{$translate('path.to.key')}` in templates, `{$translate('key', {param: val})}` for template params
- **Persistence**: Locale stored in localStorage, restored on page load
- **Language switcher**: Dropdown in navbar (flag + code)
- **Quiz language**: `language` column on Quiz model, settable on create/edit

## Gotchas

- **Scoring is server-side only** — never trust client-side answer validation for persistence
- **Answers hidden** from `GET /quizzes/{id}` — only exposed via `/manage` endpoint (owner only)
- **JWT stored in localStorage** — token sent via `Authorization: Bearer` header
- **Vite proxy** — frontend proxies `/api/*` to backend in dev mode
- **UUID primary keys** — all IDs are UUIDs, not integers
- **JSON columns** — `options` and `answer` fields are JSON in PostgreSQL
- **Pagination** — `GET /quizzes` returns `{items, total, page, page_size, total_pages}`
- **Embed widget** served as inline HTML from FastAPI at `/api/embed/{id}` — no frontend route; uses `window.parent.postMessage` for result communication
- **Import/Export endpoints** only accessible to quiz owner or admin (prevents answer leakage)
- `npm install` must be run in `frontend/` before dev server starts
- Backend requires PostgreSQL running (use Docker or local install)
- `$translate` returns a function — use `{$translate('key')}` in templates (curly braces required)
- Admin CRUD endpoints use `require_admin` dependency; all return plain dict responses
- Playwright tests in `frontend/e2e/` — run with `npx playwright test` while dev servers are up
