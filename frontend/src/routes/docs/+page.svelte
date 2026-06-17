<script lang="ts">
  import { isLoggedIn, isAdmin } from '$lib/stores/auth';
</script>

<svelte:head>
  <title>Docs — QuizTime</title>
</svelte:head>

<div class="mb-8">
  <h1 class="text-4xl font-bold mb-2">Documentation</h1>
  <p class="text-base-content/60">Guides for developers, admins, and users.</p>
</div>

<div class="grid sm:grid-cols-3 gap-6">
  {#if $isLoggedIn && $isAdmin}
    <a href="/docs/developer" class="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow">
      <div class="card-body items-center text-center">
        <span class="text-4xl mb-2">💻</span>
        <h2 class="card-title">Developer Guide</h2>
        <p class="text-sm text-base-content/60">Architecture, setup, API reference, testing, and deployment.</p>
        <div class="card-actions mt-2">
          <span class="btn btn-primary btn-sm">Read Guide</span>
        </div>
      </div>
    </a>

    <a href="/docs/admin" class="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow">
      <div class="card-body items-center text-center">
        <span class="text-4xl mb-2">⚙️</span>
        <h2 class="card-title">Admin Guide</h2>
        <p class="text-sm text-base-content/60">Manage quizzes, categories, users, and system settings.</p>
        <div class="card-actions mt-2">
          <span class="btn btn-primary btn-sm">Read Guide</span>
        </div>
      </div>
    </a>
  {/if}

  <a href="/docs/user" class="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow"
    class:sm:col-span-3={!($isLoggedIn && $isAdmin)}
  >
    <div class="card-body items-center text-center">
      <span class="text-4xl mb-2">📖</span>
      <h2 class="card-title">User Guide</h2>
      <p class="text-sm text-base-content/60">Take quizzes, track progress, and create your own.</p>
      <div class="card-actions mt-2">
        <span class="btn btn-primary btn-sm">Read Guide</span>
      </div>
    </div>
  </a>
</div>
