<script lang="ts">
  const archCode = `quiz-v7/
├── backend/    FastAPI + SQLAlchemy + PostgreSQL
├── frontend/   SvelteKit 2 + Svelte 5 + Tailwind v4 + Skeleton v4
├── dev.sh      → Development server (ports 8000, 5173)
├── start.sh    → Production server (ports 8000, 4173)
└── docker-compose.yml`;

  const backendCode = `backend/
├── app/
│   ├── main.py          # FastAPI app, lifespan, CORS, router mounts
│   ├── config.py        # pydantic-settings (env vars)
│   ├── database.py      # Engine, session factory, Base
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── auth.py          # JWT creation, password hashing (bcrypt)
│   └── routes/
│       ├── auth.py       # POST /register, /login, GET /me
│       ├── quizzes.py    # CRUD + /manage, /take (paginated)
│       ├── questions.py  # CRUD per quiz
│       ├── categories.py # CRUD + subcategories
│       ├── attempts.py   # Submit, mine, stats, get by id
│       ├── share.py      # Share links + OG cards
│       ├── challenges.py # Challenge system
│       ├── ratings.py    # 5-star ratings + reviews
│       ├── gamification.py # XP, levels, badges, leaderboard
│       ├── email.py      # Email verify, forgot/reset password
│       └── embed.py      # Embed widget, data API, submit, submissions, snippet
├── tests/
│   ├── conftest.py       # Fixtures: test client, SQLite override
│   ├── test_auth.py
│   ├── test_quizzes.py
│   ├── test_questions.py
│   ├── test_categories.py
│   ├── test_attempts.py
│   ├── test_share_challenge.py
│   ├── test_gamification.py
│       ├── test_search_ratings.py
│       ├── test_embed.py
│       └── test_questions.py
├── seed.py               # Demo data seeder (categories + subcategories + quiz + questions)
└── requirements.txt`;

  const frontendCode = `frontend/
├── src/
│   ├── app.html           # data-theme="cerberus"
│   ├── app.css            # Tailwind v4 imports + Skeleton theme
│   ├── lib/
│   │   ├── api.ts         # API client (buildApi pattern)
│   │   └── stores/
│   │       ├── auth.ts    # JWT + user state
│   │       └── theme.ts   # Skeleton theme toggle
│   └── routes/
│       ├── +layout.svelte  # Navbar, theme toggle
│       ├── +error.svelte   # Error boundary
│       ├── login/, register/
│       ├── quizzes/
│       │   ├── +page.svelte          # Browse (paginated, filter/sort)
│       │   └── [id]/
│       │       ├── +page.svelte      # Detail
│       │       ├── take/             # Player
│       │       ├── results/          # Score + share + challenge
│       │       └── edit/             # Manage (category + subcategory dropdowns)
│       │   └── challenge/[code]/     # Challenge landing + accept
│       ├── dashboard/                # User's quizzes + attempt history + XP card
│       ├── create/                   # Create quiz (category dropdown + import JSON tab)
│       ├── achievements/             # Badges gallery + XP history + level progress
│       ├── verify-email/             # Email verification (?token=)
│       ├── forgot-password/          # Request password reset
│       ├── reset-password/           # Reset password (?token=)
│       └── docs/                     # Documentation hub
├── package.json
├── vite.config.ts         # @tailwindcss/vite plugin`;

  const quickStartCode = `# One command to start everything:
./dev.sh

# Other commands:
./dev.sh stop       # stop dev servers
./dev.sh restart    # restart dev servers
./dev.sh status     # check if running

# Frontend: http://localhost:5173 (Vite HMR)
# Backend:  http://localhost:8000/docs (hot-reload)`;

  const manualSetupCode = `# Backend
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python seed.py    # seeds admin/demo users + sample quiz
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev`;

  const prodCode = `# One command to start production:
./start.sh

# Other commands:
./start.sh stop       # stop prod servers
./start.sh restart    # restart prod servers
./start.sh status     # check if running

# Frontend: http://localhost:4173 (built, 4 workers)
# Backend:  http://localhost:8000/docs`;

  const dockerCode = `docker-compose up

# Frontend: http://localhost:5173
# Backend:  http://localhost:8000/docs
# Database: localhost:5432`;

  const migrationCode = `alembic revision --autogenerate -m "description"
alembic upgrade head`;

  const envCode = `DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/quiztime
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440`;

  const apiClientCode = `// SSR load functions use server-provided fetch:
export const load = async ({ fetch }) => {
  const api = createApi(fetch);
  const quiz = await api.getQuiz(id);
  return { quiz };
};

// Client-side uses the default singleton:
import { api } from '$lib/api';
const quiz = await api.getQuiz(id);`;

  const themeCode = `// stores/theme.ts
// Dark/light toggle using Skeleton themes
// 'cerberus' = dark, 'modern' = light
import { theme } from '$lib/stores/theme';
theme.toggle();  // toggles: cerberus ↔ modern

// app.css imports both themes:
@import "tailwindcss";
@import "@skeletonlabs/skeleton";
@import "@skeletonlabs/skeleton/themes/cerberus";
@import "@skeletonlabs/skeleton/themes/modern";

// app.html sets the default:
// <html lang="en" data-theme="cerberus">`;

  const testCode = `python -m pytest tests/ -q
python -m pytest tests/test_auth.py
python -m pytest -k "register"`;

  const feTestCode = `npm run test
npm run test:watch`;

  const commitCode = `feat: add attempt stats endpoint
fix: guard setattr loop in question update
docs: add developer guide`;
</script>

<svelte:head>
  <title>Developer Guide — QuizTime</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&family=DM+Serif+Display:ital@0;1&display=swap" rel="stylesheet" />
</svelte:head>

<div class="mb-8">
  <h1 class="mb-2 text-4xl font-bold heading-serif">Developer Guide</h1>
  <p class="opacity-60">Architecture, setup, and contribution guidelines for QuizTime.</p>
</div>

<!-- Mobile TOC -->
<details class="mb-6 rounded-xl border border-[var(--color-surface-300-700)] bg-[var(--color-surface-100-900)] lg:hidden">
  <summary class="flex cursor-pointer items-center gap-2 px-4 py-3 text-sm font-semibold transition-colors hover:bg-[var(--color-surface-200-800)] rounded-xl">
    <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" /></svg>
    Contents
  </summary>
  <div class="space-y-0.5 border-t border-[var(--color-surface-300-700)] px-3 py-2">
    <a href="#architecture" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Architecture</a>
    <a href="#tech-stack" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Tech Stack</a>
    <a href="#project-structure" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Project Structure</a>
    <a href="#setup" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Local Setup</a>
    <a href="#database" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Database</a>
    <a href="#api" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">API Reference</a>
    <a href="#auth" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Authentication</a>
    <a href="#frontend" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Frontend</a>
    <a href="#testing" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Testing</a>
    <a href="#deployment" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Deployment</a>
    <a href="#contributing" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Contributing</a>
  </div>
</details>

<div class="grid gap-8 lg:grid-cols-[220px_1fr]">
  <aside class="hidden lg:block">
    <div class="sticky top-20 w-52 rounded-2xl border border-[var(--color-surface-300-700)] bg-[var(--color-surface-100-900)] shadow-lg">
      <div class="border-b border-[var(--color-surface-300-700)] px-4 py-3">
        <span class="text-sm font-semibold heading-serif">Contents</span>
      </div>
      <div class="space-y-0.5 px-2 py-2">
        <a href="#architecture" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Architecture</a>
        <a href="#tech-stack" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Tech Stack</a>
        <a href="#project-structure" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Project Structure</a>
        <a href="#setup" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Local Setup</a>
        <a href="#database" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Database</a>
        <a href="#api" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">API Reference</a>
        <a href="#auth" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Authentication</a>
        <a href="#frontend" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Frontend</a>
        <a href="#testing" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Testing</a>
        <a href="#deployment" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Deployment</a>
        <a href="#contributing" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Contributing</a>
      </div>
    </div>
  </aside>

  <main class="min-w-0 space-y-12 stagger">

    <section id="architecture" class="frame p-6">
        <h2 class="mb-4 text-2xl font-bold">Architecture</h2>
        <p>QuizTime is a full-stack monorepo with a clear separation between backend API and frontend SPA.</p>
        <pre class="code mt-2 p-4"><code>{archCode}</code></pre>
        <hr class="my-4 border-[var(--color-surface-300-700)]" />
        <h3 class="mt-4 font-semibold">Data Flow</h3>
        <ol class="mt-1 space-y-1 text-sm">
          <li>1. Frontend makes HTTP requests to <code class="badge variant-ghost">/api/*</code> endpoints.</li>
          <li>2. Vite dev proxy forwards requests to FastAPI on port 8000.</li>
          <li>3. FastAPI validates JWT tokens, enforces RBAC, and queries PostgreSQL via async SQLAlchemy.</li>
          <li>4. Responses are JSON; the frontend updates Svelte stores and re-renders.</li>
        </ol>
    </section>

    <section id="tech-stack" class="frame p-6">
        <h2 class="mb-4 text-2xl font-bold">Tech Stack</h2>
        <div class="-mx-6 overflow-x-auto px-6">
          <table class="table w-full min-w-[500px]">
            <thead><tr><th>Layer</th><th>Technology</th><th>Version</th><th>Notes</th></tr></thead>
            <tbody>
              <tr><td>Backend Framework</td><td>FastAPI</td><td>0.104.1</td><td></td></tr>
              <tr><td>ORM</td><td>SQLAlchemy (async)</td><td>2.0.23+</td><td>lazy engine init</td></tr>
              <tr><td>Database</td><td>PostgreSQL + asyncpg</td><td>15+</td><td>binary install for Python 3.14</td></tr>
              <tr><td>Migrations</td><td>Alembic</td><td>1.13.0</td><td></td></tr>
              <tr><td>Auth</td><td>JWT + bcrypt</td><td>jose 3.3 / bcrypt 5.0</td><td>direct bcrypt, not passlib</td></tr>
              <tr><td>Frontend Framework</td><td>SvelteKit + Svelte</td><td>2.x + 5.x</td><td>runes syntax ($state, $derived, $effect)</td></tr>
              <tr><td>CSS</td><td>Tailwind CSS + Skeleton</td><td>4.x / 4.x</td><td>Tailwind v4 CSS-based config</td></tr>
              <tr><td>Build Tool</td><td>Vite</td><td>8.x</td><td>@tailwindcss/vite plugin</td></tr>
              <tr><td>Testing (BE)</td><td>pytest + aiosqlite</td><td>7.4+</td><td>SQLite for tests, no PG needed</td></tr>
              <tr><td>Testing (FE)</td><td>Vitest</td><td>4.x</td><td></td></tr>
            </tbody>
          </table>
        </div>
    </section>

    <section id="project-structure" class="frame p-6">
        <h2 class="mb-4 text-2xl font-bold">Project Structure</h2>
        <h3 class="mt-4 font-semibold">Backend</h3>
        <pre class="code mt-2 p-4"><code>{backendCode}</code></pre>
        <h3 class="mt-4 font-semibold">Frontend</h3>
        <pre class="code mt-2 p-4"><code>{frontendCode}</code></pre>
    </section>

    <section id="setup" class="frame p-6">
        <h2 class="mb-4 text-2xl font-bold">Local Setup</h2>
        <h3 class="mt-4 font-semibold">Prerequisites</h3>
        <ul class="mt-1 space-y-1 text-sm">
          <li>• Python 3.11+ (3.14 supported with asyncpg binary)</li>
          <li>• Node.js 18+</li>
          <li>• PostgreSQL 15+ (running locally, or use Docker)</li>
        </ul>

        <h3 class="mt-4 font-semibold">Quick Start (Recommended)</h3>
        <p class="text-sm opacity-70 mb-2"><code>./dev.sh</code> starts both backend and frontend with one command.</p>
        <pre class="code mt-2 p-4"><code>{quickStartCode}</code></pre>

        <h3 class="mt-4 font-semibold">Manual Setup</h3>
        <pre class="code mt-2 p-4"><code>{manualSetupCode}</code></pre>

        <h3 class="mt-4 font-semibold">Docker</h3>
        <pre class="code mt-2 p-4"><code>{dockerCode}</code></pre>
    </section>

    <section id="database" class="frame p-6">
        <h2 class="mb-4 text-2xl font-bold">Database</h2>
        <p>PostgreSQL with async SQLAlchemy. All primary keys are UUIDs. Engine uses lazy init pattern.</p>
        <div class="-mx-6 mt-4 overflow-x-auto px-6">
          <table class="table w-full min-w-[400px] text-sm">
            <thead><tr><th>Table</th><th>Key Columns</th><th>Notes</th></tr></thead>
            <tbody>
              <tr><td><code>users</code></td><td>id, username, email, hashed_password, role, xp, level, streak_count, last_activity_date, email_verified</td><td>role: admin | user</td></tr>
              <tr><td><code>quizzes</code></td><td>id, title, description, category_id FK, created_by FK</td><td>Index on created_by</td></tr>
              <tr><td><code>questions</code></td><td>id, quiz_id FK, subcategory_id FK, type, text, options, answer</td><td>JSON columns, FK indexes</td></tr>
              <tr><td><code>categories</code></td><td>id, name</td><td>Unique name</td></tr>
              <tr><td><code>subcategories</code></td><td>id, name, category_id FK</td><td>FK to categories</td></tr>
              <tr><td><code>quiz_attempts</code></td><td>id, quiz_id FK, user_id FK, answers, score, total, time_spent</td><td>FK indexes, leaderboard index (quiz_id, score desc, time_spent asc, created_at)</td></tr>
              <tr><td><code>embed_submissions</code></td><td>id, quiz_id FK, submission_name, answers, score, total, time_spent</td><td>Anonymous submissions from embed widget</td></tr>
              <tr><td><code>share_links</code></td><td>id, quiz_id FK, attempt_id FK, code (unique)</td><td>Unique code index</td></tr>
              <tr><td><code>challenges</code></td><td>id, quiz_id FK, challenger_id FK, challenge_code (unique), score_to_beat, status, expires_at, challenger_attempt_id, challengee_attempt_id</td><td>Auto-expires after 7 days</td></tr>
              <tr><td><code>ratings</code></td><td>id, quiz_id FK, user_id FK, score, review, created_at</td><td>Unique per user+quiz</td></tr>
              <tr><td><code>badge_definitions</code></td><td>id, key, name, description, icon, criteria</td><td>6 seeded badges</td></tr>
              <tr><td><code>user_badges</code></td><td>user_id FK, badge_id FK, earned_at</td><td>PK: (user_id, badge_id)</td></tr>
              <tr><td><code>xp_events</code></td><td>id, user_id FK, source, amount, created_at</td><td>Audit log for XP changes</td></tr>
              <tr><td><code>email_tokens</code></td><td>id, user_id FK, token, type (verify|reset), expires_at, used</td><td>Used on verify/reset</td></tr>
            </tbody>
          </table>
        </div>
        <h3 class="mt-4 font-semibold">Migrations</h3>
        <pre class="code mt-2 p-4"><code>{migrationCode}</code></pre>
    </section>

    <section id="api" class="frame p-6">
        <h2 class="mb-4 text-2xl font-bold">API Reference</h2>
        <p>Interactive docs at <a href="http://localhost:8000/docs" class="text-[var(--color-primary-500)] hover:underline" target="_blank">localhost:8000/docs</a></p>
        <div class="-mx-6 mt-4 overflow-x-auto px-6">
          <table class="table w-full min-w-[500px] text-sm">
            <thead><tr><th>Method</th><th>Endpoint</th><th>Auth</th><th>Description</th></tr></thead>
            <tbody>
              <tr><td><span class="badge variant-filled-success">POST</span></td><td>/api/auth/register</td><td>No</td><td>Create account</td></tr>
              <tr><td><span class="badge variant-filled-success">POST</span></td><td>/api/auth/login</td><td>No</td><td>Get JWT token</td></tr>
              <tr><td><span class="badge variant-filled-secondary">GET</span></td><td>/api/auth/me</td><td>Yes</td><td>Current user</td></tr>
              <tr><td><span class="badge variant-filled-secondary">GET</span></td><td>/api/quizzes</td><td>No</td><td>List quizzes (paginated, filter/sort: ?category_id=&q=&sort_by=)</td></tr>
              <tr><td><span class="badge variant-filled-success">POST</span></td><td>/api/quizzes</td><td>Yes</td><td>Create quiz (accepts category_id)</td></tr>
              <tr><td><span class="badge variant-filled-secondary">GET</span></td><td>/api/quizzes/{'{id}'}</td><td>No</td><td>Quiz detail (answers hidden)</td></tr>
              <tr><td><span class="badge variant-filled-secondary">GET</span></td><td>/api/quizzes/{'{id}'}/manage</td><td>Owner</td><td>Quiz with answers</td></tr>
              <tr><td><span class="badge variant-filled-secondary">GET</span></td><td>/api/quizzes/{'{id}'}/take</td><td>Yes</td><td>Quiz with questions for taking</td></tr>
              <tr><td><span class="badge variant-filled-secondary">GET</span></td><td>/api/quizzes/{'{id}'}/leaderboard</td><td>Yes</td><td>Per-quiz leaderboard (?period=today|week|month|all)</td></tr>
              <tr><td><span class="badge variant-filled-warning">PUT</span></td><td>/api/quizzes/{'{id}'}</td><td>Owner</td><td>Update quiz (accepts category_id)</td></tr>
              <tr><td><span class="badge variant-filled-error">DELETE</span></td><td>/api/quizzes/{'{id}'}</td><td>Owner</td><td>Delete quiz</td></tr>
              <tr><td><span class="badge variant-filled-success">POST</span></td><td>/api/questions/{'{quizId}'}</td><td>Owner</td><td>Add question (accepts subcategory_id)</td></tr>
              <tr><td><span class="badge variant-filled-warning">PUT</span></td><td>/api/questions/{'{id}'}</td><td>Owner</td><td>Update question (accepts subcategory_id)</td></tr>
              <tr><td><span class="badge variant-filled-error">DELETE</span></td><td>/api/questions/{'{id}'}</td><td>Owner</td><td>Delete question</td></tr>
              <tr><td><span class="badge variant-filled-secondary">GET</span></td><td>/api/categories</td><td>No</td><td>List categories</td></tr>
              <tr><td><span class="badge variant-filled-success">POST</span></td><td>/api/categories</td><td>Admin</td><td>Create category</td></tr>
              <tr><td><span class="badge variant-filled-secondary">GET</span></td><td>/api/categories/subcategories</td><td>No</td><td>List subcategories (?category_id=)</td></tr>
              <tr><td><span class="badge variant-filled-success">POST</span></td><td>/api/attempts</td><td>Yes</td><td>Submit attempt (server-side scoring, optional challenge_code)</td></tr>
              <tr><td><span class="badge variant-filled-secondary">GET</span></td><td>/api/attempts/mine</td><td>Yes</td><td>User's attempts</td></tr>
              <tr><td><span class="badge variant-filled-secondary">GET</span></td><td>/api/attempts/{'{id}'}</td><td>Yes</td><td>Get attempt by ID</td></tr>
              <tr><td><span class="badge variant-filled-secondary">GET</span></td><td>/api/attempts/quiz/{'{id}'}/stats</td><td>No</td><td>Quiz statistics (total, avg, best)</td></tr>
              <tr><td><span class="badge variant-filled-success">POST</span></td><td>/api/share</td><td>Yes</td><td>Create share link (dedup per attempt)</td></tr>
              <tr><td><span class="badge variant-filled-secondary">GET</span></td><td>/api/share/{'{code}'}</td><td>No</td><td>Resolve share link</td></tr>
              <tr><td><span class="badge variant-filled-secondary">GET</span></td><td>/api/share/{'{code}'}/og</td><td>No</td><td>OG image card HTML page (base64 SVG)</td></tr>
              <tr><td><span class="badge variant-filled-success">POST</span></td><td>/api/challenges</td><td>Yes</td><td>Create challenge (score-to-beat)</td></tr>
              <tr><td><span class="badge variant-filled-secondary">GET</span></td><td>/api/challenges</td><td>Yes</td><td>List my created challenges</td></tr>
              <tr><td><span class="badge variant-filled-secondary">GET</span></td><td>/api/challenges/{'{code}'}</td><td>No</td><td>Get challenge details</td></tr>
              <tr><td><span class="badge variant-filled-success">POST</span></td><td>/api/challenges/{'{code}'}/accept</td><td>Yes</td><td>Accept challenge</td></tr>
              <tr><td><span class="badge variant-filled-secondary">GET</span></td><td>/api/challenges/{'{code}'}/result</td><td>No</td><td>Challenge comparison page</td></tr>
              <tr><td><span class="badge variant-filled-success">POST</span></td><td>/api/ratings</td><td>Yes</td><td>Rate a quiz (score 1-5, optional review)</td></tr>
              <tr><td><span class="badge variant-filled-secondary">GET</span></td><td>/api/ratings/{'{quizId}'}</td><td>No</td><td>List ratings for a quiz</td></tr>
              <tr><td><span class="badge variant-filled-secondary">GET</span></td><td>/api/ratings/{'{quizId}'}/stats</td><td>No</td><td>Average rating + count</td></tr>
              <tr><td><span class="badge variant-filled-secondary">GET</span></td><td>/api/ratings/{'{quizId}'}/my</td><td>Yes</td><td>Current user's rating</td></tr>
              <tr><td><span class="badge variant-filled-error">DELETE</span></td><td>/api/ratings/{'{ratingId}'}</td><td>Owner</td><td>Delete rating</td></tr>
              <tr><td><span class="badge variant-filled-success">POST</span></td><td>/api/email/verify</td><td>No</td><td>Verify email with token</td></tr>
              <tr><td><span class="badge variant-filled-success">POST</span></td><td>/api/email/resend-verification</td><td>Yes</td><td>Resend verification email</td></tr>
              <tr><td><span class="badge variant-filled-success">POST</span></td><td>/api/email/forgot-password</td><td>No</td><td>Request password reset</td></tr>
              <tr><td><span class="badge variant-filled-success">POST</span></td><td>/api/email/reset-password</td><td>No</td><td>Reset password with token</td></tr>
              <tr><td><span class="badge variant-filled-secondary">GET</span></td><td>/api/gamification/my-profile</td><td>Yes</td><td>Current user's XP/profile/streak/badges</td></tr>
              <tr><td><span class="badge variant-filled-secondary">GET</span></td><td>/api/gamification/profile/{'{id}'}</td><td>No</td><td>Any user's public gamification profile</td></tr>
              <tr><td><span class="badge variant-filled-secondary">GET</span></td><td>/api/gamification/xp-history</td><td>Yes</td><td>Paginated XP event history</td></tr>
              <tr><td><span class="badge variant-filled-secondary">GET</span></td><td>/api/gamification/badges</td><td>No</td><td>All badges with earned status</td></tr>
              <tr><td><span class="badge variant-filled-secondary">GET</span></td><td>/api/gamification/leaderboard</td><td>No</td><td>XP leaderboard (top users)</td></tr>
              <tr><td><span class="badge variant-filled-secondary">GET</span></td><td>/api/quizzes/{'{id}'}/export</td><td>Owner</td><td>Export quiz as JSON (with answers)</td></tr>
              <tr><td><span class="badge variant-filled-success">POST</span></td><td>/api/quizzes/import</td><td>Yes</td><td>Import quiz from JSON file</td></tr>
              <tr><td><span class="badge variant-filled-secondary">GET</span></td><td>/api/embed/{'{quiz_id}'}/data</td><td>No</td><td>Public quiz data for embed</td></tr>
              <tr><td><span class="badge variant-filled-success">POST</span></td><td>/api/embed/{'{quiz_id}'}/submit</td><td>No</td><td>Anonymous embed submission</td></tr>
              <tr><td><span class="badge variant-filled-secondary">GET</span></td><td>/api/embed/{'{quiz_id}'}</td><td>No</td><td>Self-contained HTML embed widget</td></tr>
              <tr><td><span class="badge variant-filled-secondary">GET</span></td><td>/api/embed/{'{quiz_id}'}/snippet</td><td>No</td><td>iframe embed snippet</td></tr>
              <tr><td><span class="badge variant-filled-secondary">GET</span></td><td>/api/embed/{'{quiz_id}'}/submissions</td><td>Owner</td><td>List embed submissions</td></tr>
            </tbody>
          </table>
        </div>
    </section>

    <section id="auth" class="frame p-6">
        <h2 class="mb-4 text-2xl font-bold">Authentication</h2>
        <p>JWT-based. Passwords hashed with <code>bcrypt</code> (direct, not passlib). Tokens stored in <code>localStorage</code>, sent via <code>Authorization: Bearer &lt;token&gt;</code>.</p>
        <h3 class="mt-4 font-semibold">Token Flow</h3>
        <ol class="mt-1 space-y-1 text-sm">
          <li>1. Client POSTs credentials to <code>/api/auth/login</code>.</li>
          <li>2. Server returns <code>{'{ access_token, user }'}</code>.</li>
          <li>3. Client stores token in <code>localStorage</code> and Svelte <code>auth</code> store.</li>
          <li>4. Every API call attaches the token header; 401 triggers logout + redirect.</li>
        </ol>
        <h3 class="mt-4 font-semibold">Roles &amp; Permissions</h3>
        <div class="-mx-6 mt-2 overflow-x-auto px-6">
          <table class="table w-full min-w-[400px] text-sm">
            <thead><tr><th>Action</th><th>User</th><th>Admin</th></tr></thead>
            <tbody>
              <tr><td>Take quiz</td><td>Yes</td><td>Yes</td></tr>
              <tr><td>Create quiz</td><td>Yes</td><td>Yes</td></tr>
              <tr><td>Edit/Delete own quiz</td><td>Yes</td><td>Yes</td></tr>
              <tr><td>Edit/Delete any quiz</td><td>No</td><td>Yes</td></tr>
              <tr><td>Create category</td><td>No</td><td>Yes</td></tr>
            </tbody>
          </table>
        </div>
        <h3 class="mt-4 font-semibold">Environment Variables</h3>
        <pre class="code mt-2 p-4"><code>{envCode}</code></pre>
        <div class="alert mt-2 bg-[var(--color-warning-500)] text-white">
          <span>Never commit <code>SECRET_KEY</code> to version control. Fails hard in production if using the default.</span>
        </div>
    </section>

    <section id="frontend" class="frame p-6">
        <h2 class="mb-4 text-2xl font-bold">Frontend Architecture</h2>
        <p>Built with Svelte 5 (runes syntax), SvelteKit 2, Tailwind CSS v4, and Skeleton v4 UI components.</p>

        <h3 class="mt-4 font-semibold">API Client Pattern</h3>
        <pre class="code mt-2 p-4"><code>{apiClientCode}</code></pre>

        <h3 class="mt-4 font-semibold">Stores</h3>
        <div class="-mx-6 mt-2 overflow-x-auto px-6">
          <table class="table w-full min-w-[400px] text-sm">
            <thead><tr><th>Store</th><th>Purpose</th><th>Persistence</th></tr></thead>
            <tbody>
              <tr><td><code>auth</code></td><td>Token + user object</td><td>localStorage</td></tr>
              <tr><td><code>isLoggedIn</code></td><td>Derived boolean</td><td>—</td></tr>
              <tr><td><code>currentUser</code></td><td>Derived user object</td><td>—</td></tr>
              <tr><td><code>isAdmin</code></td><td>Derived role check</td><td>—</td></tr>
              <tr><td><code>theme</code></td><td>Skeleton theme toggle</td><td>localStorage</td></tr>
            </tbody>
          </table>
        </div>

        <h3 class="mt-4 font-semibold">Skeleton Theming</h3>
        <p class="text-sm mb-2">Themes are applied via the <code>data-theme</code> attribute on <code>&lt;html&gt;</code>. The theme store toggles between two Skeleton themes:</p>
        <div class="mt-2 grid gap-2 sm:grid-cols-2 text-sm">
          <div class="rounded-lg bg-[var(--color-surface-200-800)] p-3 text-center"><strong>🌙 Dark (Cerberus)</strong> — default</div>
          <div class="rounded-lg bg-[var(--color-surface-200-800)] p-3 text-center"><strong>☀️ Light (Modern)</strong></div>
        </div>
        <pre class="code mt-2 p-4"><code>{themeCode}</code></pre>
        <p class="text-sm mt-2">Skeleton v4 uses CSS custom properties for theming. Components use classes like <code>variant-filled-primary</code>, <code>variant-ghost</code>, <code>variant-outline</code> instead of DaisyUI's <code>btn-primary</code> pattern.</p>

        <h3 class="mt-4 font-semibold">Svelte 5 Runes</h3>
        <p class="text-sm">All components use Svelte 5 runes syntax instead of Svelte 4 <code>export let</code> / stores:</p>
        <ul class="mt-1 space-y-1 text-sm">
          <li>• <code>$props()</code> — component props (replaces <code>export let</code>)</li>
          <li>• <code>$state()</code> — reactive local state (replaces <code>let x = value</code>)</li>
          <li>• <code>$derived()</code> — computed values (replaces <code>$:</code> reactive statements)</li>
          <li>• <code>$effect()</code> — side effects (replaces <code>onMount</code> / <code>afterUpdate</code>)</li>
          <li>• <code>&#123;@render children()&#125;</code> — slot rendering (replaces <code>&lt;slot /&gt;</code>)</li>
        </ul>
    </section>

    <section id="testing" class="frame p-6">
        <h2 class="mb-4 text-2xl font-bold">Testing</h2>
        <h3 class="mt-4 font-semibold">Backend (pytest)</h3>
        <pre class="code mt-2 p-4"><code>{testCode}</code></pre>
        <ul class="mt-2 space-y-1 text-sm">
          <li>• Uses <code>aiosqlite</code> — no PostgreSQL needed for tests.</li>
          <li>• Fixtures: <code>client</code>, <code>auth_headers</code>, <code>admin_headers</code>, <code>created_quiz</code>, <code>category</code>, <code>subcategory</code>, <code>registered_user</code>.</li>
          <li>• Database uses lazy init: call <code>get_engine()</code> / <code>get_session_factory()</code> before use.</li>
        </ul>
        <h3 class="mt-4 font-semibold">Frontend (vitest)</h3>
        <pre class="code mt-2 p-4"><code>{feTestCode}</code></pre>
    </section>

    <section id="deployment" class="frame p-6">
        <h2 class="mb-4 text-2xl font-bold">Deployment</h2>
        <h3 class="mt-4 font-semibold">Production (Recommended)</h3>
        <p class="text-sm opacity-70 mb-2"><code>./start.sh</code> builds the frontend and starts production servers.</p>
        <pre class="code mt-2 p-4"><code>{prodCode}</code></pre>
        <h3 class="mt-4 font-semibold">Production Checklist</h3>
        <ul class="mt-1 space-y-1 text-sm">
          <li>• Set a strong <code>SECRET_KEY</code> (app fails hard if using default).</li>
          <li>• Configure CORS origins for your domain.</li>
          <li>• Run <code>alembic upgrade head</code> after deploys.</li>
          <li>• Frontend built with <code>npm run build</code>, served by Vite preview (4 workers).</li>
          <li>• Enable HTTPS via reverse proxy (Nginx/Caddy).</li>
        </ul>
    </section>

    <section id="contributing" class="frame p-6">
        <h2 class="mb-4 text-2xl font-bold">Contributing</h2>
        <h3 class="mt-4 font-semibold">Code Style</h3>
        <ul class="mt-1 space-y-1 text-sm">
          <li>• Python: PEP 8, type hints, async/await throughout.</li>
          <li>• TypeScript: strict mode, prefer <code>const</code>.</li>
          <li>• Svelte: <code>&lt;script lang="ts"&gt;</code>, Svelte 5 runes (<code>$state</code>, <code>$derived</code>, <code>$effect</code>).</li>
          <li>• CSS: Skeleton v4 component classes, Tailwind utility classes.</li>
        </ul>
        <h3 class="mt-4 font-semibold">Workflow</h3>
        <ol class="mt-1 space-y-1 text-sm">
          <li>1. Branch from <code>main</code>.</li>
          <li>2. Run <code>./dev.sh</code> to start dev servers.</li>
          <li>3. Write/update tests.</li>
          <li>4. Run <code>pytest</code> and <code>npm run test</code>.</li>
          <li>5. Run <code>npm run check</code> for type validation.</li>
          <li>6. Open a PR.</li>
        </ol>
        <h3 class="mt-4 font-semibold">Commit Messages</h3>
        <pre class="code mt-2 p-4"><code>{commitCode}</code></pre>
    </section>
  </main>
</div>