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
  <h1 class="text-4xl font-bold mb-2">Admin Guide</h1>
  <p class="text-base-content/60">Manage users, quizzes, categories, and system settings.</p>
</div>

<div class="grid lg:grid-cols-[220px_1fr] gap-8">
  <aside class="hidden lg:block">
    <ul class="menu bg-base-100 rounded-box shadow w-52 sticky top-20">
      <li class="menu-title">Contents</li>
      <li><a href="#login">Admin Login</a></li>
      <li><a href="#dashboard">Dashboard</a></li>
      <li><a href="#manage-quizzes">Manage Quizzes</a></li>
      <li><a href="#categories">Categories</a></li>
      <li><a href="#users">User Management</a></li>
      <li><a href="#analytics">Analytics</a></li>
      <li><a href="#security">Security</a></li>
    </ul>
  </aside>

  <main class="space-y-12">

    <section id="login" class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">Admin Login</h2>
        <p>Admin accounts have full access to all features.</p>
        <div class="alert alert-info mt-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          <div>
            <h3 class="font-bold">Default Credentials</h3>
            <p class="text-sm">Username: <strong>admin</strong> | Password: <strong>admin123</strong></p>
            <p class="text-sm mt-1">Change the password immediately in production.</p>
          </div>
        </div>
      </div>
    </section>

    <section id="dashboard" class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">Dashboard</h2>
        <p>After logging in, the Dashboard shows your quizzes and attempt history.</p>
        <h3 class="font-semibold mt-4">Stats Overview</h3>
        <div class="grid sm:grid-cols-3 gap-4 mt-2">
          <div class="stat bg-base-200 rounded-box p-4">
            <div class="stat-title">My Quizzes</div>
            <div class="stat-value text-primary text-2xl">—</div>
            <p class="text-xs text-base-content/60">Admin sees all quizzes in the system</p>
          </div>
          <div class="stat bg-base-200 rounded-box p-4">
            <div class="stat-title">Attempts</div>
            <div class="stat-value text-secondary text-2xl">—</div>
          </div>
          <div class="stat bg-base-200 rounded-box p-4">
            <div class="stat-title">Avg Score</div>
            <div class="stat-value text-accent text-2xl">—</div>
          </div>
        </div>
      </div>
    </section>

    <section id="manage-quizzes" class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">Manage Quizzes</h2>
        <h3 class="font-semibold mt-4">Creating a New Quiz</h3>
        <ol class="list-decimal list-inside text-sm space-y-1">
          <li>Click <strong>"Create Quiz"</strong> in the navigation bar.</li>
          <li>Enter a title and optional description.</li>
          <li>Click <strong>"Create Quiz"</strong> — you'll be taken to the edit page.</li>
        </ol>
        <h3 class="font-semibold mt-4">Adding Questions</h3>
        <ol class="list-decimal list-inside text-sm space-y-1">
          <li>On the edit page, scroll to <strong>"Add New Question"</strong>.</li>
          <li>Enter the question text.</li>
          <li>Select a type: <strong>Single Select</strong>, <strong>Multi Select</strong>, or <strong>True/False</strong>.</li>
          <li>Optionally assign a category.</li>
          <li>Fill in options and click letter buttons to mark correct answers.</li>
          <li>Click <strong>"Add Question"</strong>.</li>
        </ol>
        <div class="alert alert-info mt-4">
          <span class="text-sm"><strong>True/False</strong> questions automatically set options to "True" and "False".</span>
        </div>
        <h3 class="font-semibold mt-4">Deleting Questions</h3>
        <p class="text-sm">Click "Delete" next to any question and confirm in the modal dialog.</p>
      </div>
    </section>

    <section id="categories" class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">Categories</h2>
        <p>Categories help organize questions by topic. Only admins can create categories.</p>
        <h3 class="font-semibold mt-4">Creating a Category</h3>
        <div class="mockup-code mt-2"><pre><code>{categoryCode}</code></pre></div>
        <h3 class="font-semibold mt-4">Assigning Categories</h3>
        <p class="text-sm">When adding a question via the edit page, select a category from the dropdown.</p>
      </div>
    </section>

    <section id="users" class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">User Management</h2>
        <h3 class="font-semibold mt-4">User Roles</h3>
        <div class="overflow-x-auto mt-2">
          <table class="table table-zebra text-sm">
            <thead><tr><th>Role</th><th>Capabilities</th><th>Assignment</th></tr></thead>
            <tbody>
              <tr>
                <td><span class="badge badge-primary">admin</span></td>
                <td>Full access: manage all quizzes, create categories, view all attempts</td>
                <td>Set via database or API</td>
              </tr>
              <tr>
                <td><span class="badge badge-secondary">user</span></td>
                <td>Create quizzes, take quizzes, view own attempts</td>
                <td>Default for new registrations</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <section id="analytics" class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">Analytics</h2>
        <h3 class="font-semibold mt-4">Quiz Statistics</h3>
        <div class="mockup-code mt-2"><pre><code>{statsCode}</code></pre></div>
        <p class="text-sm mt-2">Returns: total attempts, average score, average percentage, best score.</p>
        <h3 class="font-semibold mt-4">Attempt History</h3>
        <div class="mockup-code mt-2"><pre><code>{attemptsCode}</code></pre></div>
      </div>
    </section>

    <section id="security" class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">Security</h2>
        <h3 class="font-semibold mt-4">Production Hardening</h3>
        <ul class="list-disc list-inside text-sm space-y-1">
          <li>Change <code>SECRET_KEY</code> to a strong random value.</li>
          <li>Change default admin password.</li>
          <li>Configure CORS to only allow your domain.</li>
          <li>Enable HTTPS via reverse proxy.</li>
          <li>Use environment variables, not <code>.env</code> files.</li>
          <li>Regularly backup the database.</li>
        </ul>
        <h3 class="font-semibold mt-4">Known Limitations</h3>
        <ul class="list-disc list-inside text-sm space-y-1">
          <li>JWT tokens in <code>localStorage</code> (XSS risk).</li>
          <li>No rate limiting on auth endpoints.</li>
          <li>No email verification or password reset flow.</li>
        </ul>
        <div class="alert alert-error mt-4">
          <span class="text-sm"><strong>Never</strong> expose database credentials, API keys, or SECRET_KEY in client-side code.</span>
        </div>
      </div>
    </section>
  </main>
</div>
