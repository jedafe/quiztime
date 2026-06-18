<script lang="ts">
  const categoryCode = `POST /api/categories
Authorization: Bearer <admin-token>

{ "name": "Science" }`;

  const statsCode = `GET /api/attempts/quiz/{quiz_id}/stats`;

  const attemptsCode = `GET /api/attempts/mine
GET /api/attempts/{attempt_id}`;
</script>

<svelte:head>
  <title>Admin Guide — QuizTime</title>
</svelte:head>

<div class="mb-8">
  <h1 class="mb-2 text-4xl font-bold heading-serif">Admin Guide</h1>
  <p class="opacity-60">Administration and management guide for QuizTime.</p>
</div>

<!-- Mobile TOC -->
<details class="mb-6 rounded-xl border border-[var(--color-surface-300-700)] bg-[var(--color-surface-100-900)] lg:hidden">
  <summary class="flex cursor-pointer items-center gap-2 px-4 py-3 text-sm font-semibold transition-colors hover:bg-[var(--color-surface-200-800)] rounded-xl">
    <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" /></svg>
    Contents
  </summary>
  <div class="space-y-0.5 border-t border-[var(--color-surface-300-700)] px-3 py-2">
    <a href="#quickstart" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Quick Start</a>
    <a href="#login" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Admin Login</a>
    <a href="#dashboard" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Dashboard</a>
    <a href="#manage-quizzes" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Manage Quizzes</a>
    <a href="#categories" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Categories</a>
    <a href="#users" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">User Management</a>
    <a href="#analytics" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Analytics</a>
    <a href="#security" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Security</a>
  </div>
</details>

<div class="grid gap-8 lg:grid-cols-[220px_1fr]">
  <aside class="hidden lg:block">
    <div class="sticky top-20 w-52 rounded-2xl border border-[var(--color-surface-300-700)] bg-[var(--color-surface-100-900)] shadow-lg">
      <div class="border-b border-[var(--color-surface-300-700)] px-4 py-3">
        <span class="text-sm font-semibold heading-serif">Contents</span>
      </div>
      <div class="space-y-0.5 px-2 py-2">
        <a href="#quickstart" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Quick Start</a>
        <a href="#login" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Admin Login</a>
        <a href="#dashboard" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Dashboard</a>
        <a href="#manage-quizzes" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Manage Quizzes</a>
        <a href="#categories" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Categories</a>
        <a href="#users" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">User Management</a>
        <a href="#analytics" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Analytics</a>
        <a href="#security" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">Security</a>
      </div>
    </div>
  </aside>

  <main class="min-w-0 space-y-10">

    <section id="quickstart" class="frame overflow-hidden p-6">
      <h2 class="mb-4 text-2xl font-bold">Quick Start</h2>
      <p class="text-sm">Start the development servers with one command:</p>
      <pre class="code mt-2 rounded-xl p-4"><code>./dev.sh</code></pre>
      <p class="mt-2 text-sm">This starts the backend on <code>localhost:8000</code> and frontend on <code>localhost:5173</code>.</p>
      <ul class="mt-2 space-y-1 text-sm">
        <li>• <code>./dev.sh stop</code> — stop dev servers</li>
        <li>• <code>./dev.sh restart</code> — restart dev servers</li>
        <li>• <code>./dev.sh status</code> — check if running</li>
      </ul>
      <p class="mt-2 text-sm">For production: <code>./start.sh</code> (builds frontend, 4 workers, port 4173).</p>
    </section>

    <section id="login" class="frame overflow-hidden p-6">
      <h2 class="mb-4 text-2xl font-bold">Admin Login</h2>
      <p>Admin accounts have full access to all features.</p>
      <div class="mt-4 rounded-lg bg-[var(--color-info-500)]/15 px-4 py-3 text-sm text-[var(--color-info-500)]">
        <h3 class="font-bold">Default Credentials</h3>
        <p class="mt-1">Username: <strong>admin</strong> | Password: <strong>admin123</strong></p>
        <p class="mt-1 opacity-70">Change the password immediately in production.</p>
      </div>
      <p class="mt-3 text-sm opacity-50">Passwords are hashed with bcrypt. Existing users from the seed script have bcrypt hashes.</p>
    </section>

    <section id="dashboard" class="frame overflow-hidden p-6">
      <h2 class="mb-4 text-2xl font-bold">Dashboard</h2>
      <p>After logging in, the Dashboard shows your quizzes and attempt history.</p>
      <h3 class="mt-4 font-semibold">Stats Overview</h3>
      <div class="mt-3 grid gap-3 sm:grid-cols-3">
        <div class="stat-pill">
          <span class="eyebrow">My Quizzes</span>
          <span class="text-2xl font-bold text-[var(--color-primary-500)]">—</span>
          <p class="text-xs opacity-40">Admin sees all quizzes</p>
        </div>
        <div class="stat-pill">
          <span class="eyebrow">Attempts</span>
          <span class="text-2xl font-bold text-[var(--color-secondary-500)]">—</span>
        </div>
        <div class="stat-pill">
          <span class="eyebrow">Avg Score</span>
          <span class="text-2xl font-bold text-[var(--color-tertiary-500)]">—</span>
        </div>
      </div>
      <p class="mt-3 text-sm opacity-50">Quiz list is fetched via <code>listQuizzes()</code> with default <code>page_size=100</code>. Admin sees all quizzes and can edit/delete any.</p>
    </section>

    <section id="manage-quizzes" class="frame overflow-hidden p-6">
      <h2 class="mb-4 text-2xl font-bold">Manage Quizzes</h2>
      <h3 class="mt-4 font-semibold">Creating a New Quiz</h3>
      <ol class="mt-2 space-y-1 text-sm">
        <li>1. Click <strong>"Create Quiz"</strong> in the navigation bar.</li>
        <li>2. Enter a title and optional description.</li>
        <li>3. Click <strong>"Create Quiz"</strong> — you'll be taken to the edit page.</li>
      </ol>
      <h3 class="mt-4 font-semibold">Adding Questions</h3>
      <ol class="mt-2 space-y-1 text-sm">
        <li>1. On the edit page, scroll to <strong>"Add New Question"</strong>.</li>
        <li>2. Enter the question text.</li>
        <li>3. Select a type: <strong>Single Select</strong>, <strong>Multi Select</strong>, or <strong>True/False</strong>.</li>
        <li>4. Optionally assign a category.</li>
        <li>5. Fill in options and click letter buttons to mark correct answers.</li>
        <li>6. Click <strong>"Add Question"</strong>.</li>
      </ol>
      <div class="mt-4 rounded-lg bg-[var(--color-info-500)]/15 px-4 py-3 text-sm text-[var(--color-info-500)]">
        <strong>True/False</strong> questions automatically set options to "True" and "False".
      </div>
      <h3 class="mt-4 font-semibold">Deleting Questions</h3>
      <p class="text-sm">Click "Delete" next to any question and confirm in the modal dialog.</p>
      <p class="mt-2 text-sm opacity-50">Quiz answers are hidden from the public endpoint — only the owner can see them via the manage endpoint.</p>
    </section>

    <section id="categories" class="frame overflow-hidden p-6">
      <h2 class="mb-4 text-2xl font-bold">Categories</h2>
      <p>Categories help organize questions by topic. Only admins can create categories.</p>
      <h3 class="mt-4 font-semibold">Creating a Category</h3>
      <pre class="code mt-2 rounded-xl p-4"><code>{categoryCode}</code></pre>
      <h3 class="mt-4 font-semibold">Assigning Categories</h3>
      <p class="text-sm">When adding a question via the edit page, select a category from the dropdown.</p>
    </section>

    <section id="users" class="frame overflow-hidden p-6">
      <h2 class="mb-4 text-2xl font-bold">User Management</h2>
      <h3 class="mt-4 font-semibold">User Roles</h3>
      <div class="frame overflow-hidden">
        <table class="table-frame text-sm">
          <thead><tr><th>Role</th><th>Capabilities</th><th>Assignment</th></tr></thead>
          <tbody>
            <tr>
              <td><span class="rounded-full bg-[var(--color-primary-500)]/15 px-2 py-0.5 text-xs font-semibold text-[var(--color-primary-500)]">admin</span></td>
              <td>Full access: manage all quizzes, create categories, view all attempts</td>
              <td class="text-sm opacity-50">Set via database or API</td>
            </tr>
            <tr>
              <td><span class="rounded-full bg-[var(--color-secondary-500)]/15 px-2 py-0.5 text-xs font-semibold text-[var(--color-secondary-500)]">user</span></td>
              <td>Create quizzes, take quizzes, view own attempts</td>
              <td class="text-sm opacity-50">Default for new registrations</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p class="mt-3 text-sm opacity-50">User passwords are bcrypt-hashed. The seed script creates admin (admin/admin123) and demo (demo/demo123) users.</p>
    </section>

    <section id="analytics" class="frame overflow-hidden p-6">
      <h2 class="mb-4 text-2xl font-bold">Analytics</h2>
      <h3 class="mt-4 font-semibold">Quiz Statistics</h3>
      <pre class="code mt-2 rounded-xl p-4"><code>{statsCode}</code></pre>
      <p class="mt-2 text-sm">Returns: total attempts, average score, average percentage, best score.</p>
      <h3 class="mt-4 font-semibold">Attempt History</h3>
      <pre class="code mt-2 rounded-xl p-4"><code>{attemptsCode}</code></pre>
      <p class="mt-2 text-sm opacity-50">Scoring is server-side only — client-side validation is never trusted for persistence.</p>
    </section>

    <section id="security" class="frame overflow-hidden p-6">
      <h2 class="mb-4 text-2xl font-bold">Security</h2>
      <h3 class="mt-4 font-semibold">Production Hardening</h3>
      <ul class="mt-2 space-y-1 text-sm">
        <li>• Set a strong <code>SECRET_KEY</code> — app fails hard in production if using default.</li>
        <li>• Change default admin password (bcrypt-hashed, not plaintext).</li>
        <li>• Configure CORS to only allow your domain.</li>
        <li>• Enable HTTPS via reverse proxy (Nginx/Caddy).</li>
        <li>• Use environment variables, not <code>.env</code> files in production.</li>
        <li>• Regularly backup the database.</li>
      </ul>
      <h3 class="mt-4 font-semibold">Known Limitations</h3>
      <ul class="mt-2 space-y-1 text-sm">
        <li>• JWT tokens in <code>localStorage</code> (XSS risk).</li>
        <li>• No rate limiting on auth endpoints.</li>
        <li>• No email verification or password reset flow.</li>
      </ul>
      <div class="mt-4 rounded-lg bg-[var(--color-error-500)]/15 px-4 py-3 text-sm text-[var(--color-error-500)]">
        <strong>Never</strong> expose database credentials, API keys, or SECRET_KEY in client-side code.
      </div>
    </section>
  </main>
</div>
