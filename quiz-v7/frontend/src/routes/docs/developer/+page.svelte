<script lang="ts">
  const archCode = `quiz-v7/
├── backend/    FastAPI + SQLAlchemy + PostgreSQL
├── frontend/   SvelteKit + Tailwind + DaisyUI
└── docker-compose.yml`;

  const backendCode = `backend/
├── app/
│   ├── main.py          # FastAPI app, lifespan, CORS, router mounts
│   ├── config.py         # pydantic-settings (env vars)
│   ├── database.py       # Engine, session factory, Base
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── auth.py           # JWT creation, password hashing
│   └── routes/
│       ├── auth.py       # POST /register, /login, GET /me
│       ├── quizzes.py    # CRUD + /manage, /take
│       ├── questions.py  # CRUD per quiz
│       ├── categories.py # CRUD
│       └── attempts.py   # Submit, mine, stats, get by id
├── tests/
│   ├── conftest.py       # Fixtures: test client, SQLite override
│   ├── test_auth.py
│   ├── test_quizzes.py
│   ├── test_questions.py
│   ├── test_categories.py
│   └── test_attempts.py
├── alembic/              # DB migrations
├── seed.py               # Demo data seeder
└── requirements.txt`;

  const frontendCode = `frontend/
├── src/
│   ├── app.html, app.css
│   ├── lib/
│   │   ├── api.ts         # API client (buildApi pattern)
│   │   └── stores/
│   │       ├── auth.ts    # JWT + user state
│   │       └── theme.ts   # Dark/light/night toggle
│   └── routes/
│       ├── +layout.svelte  # Navbar, theme toggle
│       ├── +error.svelte   # Error boundary
│       ├── login/, register/
│       ├── quizzes/
│       │   ├── +page.svelte         # Browse
│       │   └── [id]/
│       │       ├── +page.svelte     # Detail
│       │       ├── take/            # Player
│       │       ├── results/         # Score
│       │       └── edit/            # Manage
│       ├── dashboard/
│       └── create/
└── package.json`;

  const setupCode = `cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python seed.py
uvicorn app.main:app --reload`;

  const frontendSetupCode = `cd frontend
npm install
npm run dev`;

  const dockerCode = `docker-compose up`;

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

  const testCode = `python -m pytest tests/ -q
python -m pytest tests/test_auth.py
python -m pytest -k "register"`;

  const feTestCode = `npm run test
npm run test:watch`;

  const dockerComposeCode = `version: "3.8"
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: quiztime
      POSTGRES_USER: quizuser
      POSTGRES_PASSWORD: changeme
    volumes: [pgdata:/var/lib/postgresql/data]
  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql+asyncpg://quizuser:changeme@db:5432/quiztime
      SECRET_KEY: change-me-in-production
    depends_on: [db]
  frontend:
    build: ./frontend
volumes:
  pgdata:`;

  const commitCode = `feat: add attempt stats endpoint
fix: guard setattr loop in question update
docs: add developer guide`;
</script>

<svelte:head>
  <title>Developer Guide — QuizTime</title>
</svelte:head>

<div class="mb-8">
  <h1 class="text-4xl font-bold mb-2">Developer Guide</h1>
  <p class="text-base-content/60">Architecture, setup, and contribution guidelines for QuizTime.</p>
</div>

<div class="grid lg:grid-cols-[220px_1fr] gap-8">
  <aside class="hidden lg:block">
    <ul class="menu bg-base-100 rounded-box shadow w-52 sticky top-20">
      <li class="menu-title">Contents</li>
      <li><a href="#architecture">Architecture</a></li>
      <li><a href="#tech-stack">Tech Stack</a></li>
      <li><a href="#project-structure">Project Structure</a></li>
      <li><a href="#setup">Local Setup</a></li>
      <li><a href="#database">Database</a></li>
      <li><a href="#api">API Reference</a></li>
      <li><a href="#auth">Authentication</a></li>
      <li><a href="#frontend">Frontend</a></li>
      <li><a href="#testing">Testing</a></li>
      <li><a href="#deployment">Deployment</a></li>
      <li><a href="#contributing">Contributing</a></li>
    </ul>
  </aside>

  <main class="space-y-12">

    <section id="architecture" class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">Architecture</h2>
        <p>QuizTime is a full-stack monorepo with a clear separation between backend API and frontend SPA.</p>
        <div class="mockup-code mt-4"><pre><code>{archCode}</code></pre></div>
        <div class="divider"></div>
        <h3 class="font-semibold text-lg">Data Flow</h3>
        <ol class="list-decimal list-inside space-y-1 text-sm">
          <li>Frontend makes HTTP requests to <code class="badge badge-ghost">/api/*</code> endpoints.</li>
          <li>Vite dev proxy forwards requests to FastAPI on port 8000.</li>
          <li>FastAPI validates JWT tokens, enforces RBAC, and queries PostgreSQL via async SQLAlchemy.</li>
          <li>Responses are JSON; the frontend updates Svelte stores and re-renders.</li>
        </ol>
      </div>
    </section>

    <section id="tech-stack" class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">Tech Stack</h2>
        <div class="overflow-x-auto">
          <table class="table table-zebra">
            <thead><tr><th>Layer</th><th>Technology</th><th>Version</th></tr></thead>
            <tbody>
              <tr><td>Backend Framework</td><td>FastAPI</td><td>0.104.1</td></tr>
              <tr><td>ORM</td><td>SQLAlchemy (async)</td><td>2.0.23+</td></tr>
              <tr><td>Database</td><td>PostgreSQL (asyncpg)</td><td>15+</td></tr>
              <tr><td>Migrations</td><td>Alembic</td><td>1.13.0</td></tr>
              <tr><td>Auth</td><td>JWT (python-jose) + bcrypt</td><td>3.3.0 / 4.1.3</td></tr>
              <tr><td>Frontend Framework</td><td>SvelteKit</td><td>2.x</td></tr>
              <tr><td>CSS</td><td>Tailwind CSS + DaisyUI</td><td>4.x / 4.x</td></tr>
              <tr><td>Build Tool</td><td>Vite</td><td>5.x</td></tr>
              <tr><td>Testing (BE)</td><td>pytest + pytest-asyncio + httpx</td><td>7.4 / 0.23 / 0.25</td></tr>
              <tr><td>Testing (FE)</td><td>Vitest</td><td>4.x</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <section id="project-structure" class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">Project Structure</h2>
        <h3 class="font-semibold mt-4">Backend</h3>
        <div class="mockup-code mt-2"><pre><code>{backendCode}</code></pre></div>
        <h3 class="font-semibold mt-4">Frontend</h3>
        <div class="mockup-code mt-2"><pre><code>{frontendCode}</code></pre></div>
      </div>
    </section>

    <section id="setup" class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">Local Setup</h2>
        <h3 class="font-semibold mt-4">Prerequisites</h3>
        <ul class="list-disc list-inside text-sm space-y-1">
          <li>Python 3.11+</li>
          <li>Node.js 18+</li>
          <li>PostgreSQL 15+</li>
        </ul>
        <h3 class="font-semibold mt-4">Backend</h3>
        <div class="mockup-code mt-2"><pre><code>{setupCode}</code></pre></div>
        <h3 class="font-semibold mt-4">Frontend</h3>
        <div class="mockup-code mt-2"><pre><code>{frontendSetupCode}</code></pre></div>
        <h3 class="font-semibold mt-4">Docker</h3>
        <div class="mockup-code mt-2"><pre><code>{dockerCode}</code></pre></div>
      </div>
    </section>

    <section id="database" class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">Database</h2>
        <p>PostgreSQL with async SQLAlchemy. All primary keys are UUIDs.</p>
        <div class="overflow-x-auto mt-4">
          <table class="table table-zebra text-sm">
            <thead><tr><th>Table</th><th>Key Columns</th><th>Notes</th></tr></thead>
            <tbody>
              <tr><td><code>users</code></td><td>id, username, email, hashed_password, role</td><td>role: admin | user</td></tr>
              <tr><td><code>quizzes</code></td><td>id, title, description, created_by FK</td><td>Index on created_by</td></tr>
              <tr><td><code>questions</code></td><td>id, quiz_id FK, category_id FK, type, text, options, answer</td><td>JSON columns, FK indexes</td></tr>
              <tr><td><code>categories</code></td><td>id, name</td><td>Unique name</td></tr>
              <tr><td><code>quiz_attempts</code></td><td>id, quiz_id FK, user_id FK, answers, score, total, time_spent</td><td>FK indexes</td></tr>
            </tbody>
          </table>
        </div>
        <h3 class="font-semibold mt-4">Migrations</h3>
        <div class="mockup-code mt-2"><pre><code>{migrationCode}</code></pre></div>
      </div>
    </section>

    <section id="api" class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">API Reference</h2>
        <p>Interactive docs at <a href="http://localhost:8000/docs" class="link link-primary" target="_blank">localhost:8000/docs</a></p>
        <div class="overflow-x-auto mt-4">
          <table class="table table-zebra text-sm">
            <thead><tr><th>Method</th><th>Endpoint</th><th>Auth</th><th>Description</th></tr></thead>
            <tbody>
              <tr><td class="badge badge-success badge-sm">POST</td><td>/api/auth/register</td><td>No</td><td>Create account</td></tr>
              <tr><td class="badge badge-success badge-sm">POST</td><td>/api/auth/login</td><td>No</td><td>Get JWT token</td></tr>
              <tr><td class="badge badge-info badge-sm">GET</td><td>/api/auth/me</td><td>Yes</td><td>Current user</td></tr>
              <tr><td class="badge badge-info badge-sm">GET</td><td>/api/quizzes</td><td>No</td><td>List quizzes</td></tr>
              <tr><td class="badge badge-success badge-sm">POST</td><td>/api/quizzes</td><td>Yes</td><td>Create quiz</td></tr>
              <tr><td class="badge badge-info badge-sm">GET</td><td>/api/quizzes/{'{id}'}</td><td>No</td><td>Quiz detail</td></tr>
              <tr><td class="badge badge-info badge-sm">GET</td><td>/api/quizzes/{'{id}'}/manage</td><td>Owner</td><td>Quiz with answers</td></tr>
              <tr><td class="badge badge-warning badge-sm">PUT</td><td>/api/quizzes/{'{id}'}</td><td>Owner</td><td>Update quiz</td></tr>
              <tr><td class="badge badge-error badge-sm">DELETE</td><td>/api/quizzes/{'{id}'}</td><td>Owner</td><td>Delete quiz</td></tr>
              <tr><td class="badge badge-success badge-sm">POST</td><td>/api/questions/{'{quizId}'}</td><td>Owner</td><td>Add question</td></tr>
              <tr><td class="badge badge-warning badge-sm">PUT</td><td>/api/questions/{'{id}'}</td><td>Owner</td><td>Update question</td></tr>
              <tr><td class="badge badge-error badge-sm">DELETE</td><td>/api/questions/{'{id}'}</td><td>Owner</td><td>Delete question</td></tr>
              <tr><td class="badge badge-info badge-sm">GET</td><td>/api/categories</td><td>No</td><td>List categories</td></tr>
              <tr><td class="badge badge-success badge-sm">POST</td><td>/api/categories</td><td>Admin</td><td>Create category</td></tr>
              <tr><td class="badge badge-success badge-sm">POST</td><td>/api/attempts</td><td>Yes</td><td>Submit attempt</td></tr>
              <tr><td class="badge badge-info badge-sm">GET</td><td>/api/attempts/mine</td><td>Yes</td><td>User's attempts</td></tr>
              <tr><td class="badge badge-info badge-sm">GET</td><td>/api/attempts/{'{id}'}</td><td>Yes</td><td>Get attempt by ID</td></tr>
              <tr><td class="badge badge-info badge-sm">GET</td><td>/api/attempts/quiz/{'{id}'}/stats</td><td>No</td><td>Quiz statistics</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <section id="auth" class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">Authentication</h2>
        <p>JWT-based. Tokens stored in <code>localStorage</code>, sent via <code>Authorization: Bearer &lt;token&gt;</code>.</p>
        <h3 class="font-semibold mt-4">Token Flow</h3>
        <ol class="list-decimal list-inside text-sm space-y-1">
          <li>Client POSTs credentials to <code>/api/auth/login</code>.</li>
          <li>Server returns <code>{'{ access_token, user }'}</code>.</li>
          <li>Client stores token in <code>localStorage</code> and Svelte <code>auth</code> store.</li>
          <li>Every API call attaches the token header; 401 triggers logout + redirect.</li>
        </ol>
        <h3 class="font-semibold mt-4">Roles &amp; Permissions</h3>
        <div class="overflow-x-auto mt-2">
          <table class="table table-zebra text-sm">
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
        <h3 class="font-semibold mt-4">Environment Variables</h3>
        <div class="mockup-code mt-2"><pre><code>{envCode}</code></pre></div>
        <div class="alert alert-warning mt-2">
          <span>Never commit <code>SECRET_KEY</code> to version control.</span>
        </div>
      </div>
    </section>

    <section id="frontend" class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">Frontend Architecture</h2>
        <h3 class="font-semibold mt-4">API Client Pattern</h3>
        <div class="mockup-code mt-2"><pre><code>{apiClientCode}</code></pre></div>
        <h3 class="font-semibold mt-4">Stores</h3>
        <div class="overflow-x-auto mt-2">
          <table class="table table-zebra text-sm">
            <thead><tr><th>Store</th><th>Purpose</th><th>Persistence</th></tr></thead>
            <tbody>
              <tr><td><code>auth</code></td><td>Token + user object</td><td>localStorage</td></tr>
              <tr><td><code>isLoggedIn</code></td><td>Derived boolean</td><td>—</td></tr>
              <tr><td><code>currentUser</code></td><td>Derived user object</td><td>—</td></tr>
              <tr><td><code>isAdmin</code></td><td>Derived role check</td><td>—</td></tr>
              <tr><td><code>theme</code></td><td>Dark/Light/Night</td><td>localStorage</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <section id="testing" class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">Testing</h2>
        <h3 class="font-semibold mt-4">Backend (pytest)</h3>
        <div class="mockup-code mt-2"><pre><code>{testCode}</code></pre></div>
        <ul class="list-disc list-inside text-sm mt-2 space-y-1">
          <li>Uses <code>aiosqlite</code> — no PostgreSQL needed for tests.</li>
          <li>Fixtures: <code>client</code>, <code>auth_headers</code>, <code>admin_headers</code>, <code>created_quiz</code>.</li>
        </ul>
        <h3 class="font-semibold mt-4">Frontend (vitest)</h3>
        <div class="mockup-code mt-2"><pre><code>{feTestCode}</code></pre></div>
      </div>
    </section>

    <section id="deployment" class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">Deployment</h2>
        <h3 class="font-semibold mt-4">Docker Compose</h3>
        <div class="mockup-code mt-2"><pre><code>{dockerComposeCode}</code></pre></div>
        <h3 class="font-semibold mt-4">Production Checklist</h3>
        <ul class="list-disc list-inside text-sm space-y-1">
          <li>Set a strong <code>SECRET_KEY</code>.</li>
          <li>Configure CORS origins for your domain.</li>
          <li>Run <code>alembic upgrade head</code> after deploys.</li>
          <li>Build frontend: <code>npm run build</code> and serve with Nginx.</li>
          <li>Enable HTTPS via reverse proxy.</li>
        </ul>
      </div>
    </section>

    <section id="contributing" class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">Contributing</h2>
        <h3 class="font-semibold mt-4">Code Style</h3>
        <ul class="list-disc list-inside text-sm space-y-1">
          <li>Python: PEP 8, type hints.</li>
          <li>TypeScript: strict mode, prefer <code>const</code>.</li>
          <li>Svelte: <code>&lt;script lang="ts"&gt;</code>.</li>
        </ul>
        <h3 class="font-semibold mt-4">Workflow</h3>
        <ol class="list-decimal list-inside text-sm space-y-1">
          <li>Branch from <code>main</code>.</li>
          <li>Write/update tests.</li>
          <li>Run <code>pytest</code> and <code>npm run test</code>.</li>
          <li>Run <code>npm run check</code>.</li>
          <li>Open a PR.</li>
        </ol>
        <h3 class="font-semibold mt-4">Commit Messages</h3>
        <div class="mockup-code mt-2"><pre><code>{commitCode}</code></pre></div>
      </div>
    </section>
  </main>
</div>
