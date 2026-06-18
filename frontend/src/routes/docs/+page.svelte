<script lang="ts">
  import { isLoggedIn, isAdmin } from '$lib/stores/auth';
</script>

<svelte:head>
  <title>Docs — QuizTime</title>
</svelte:head>

<div class="page-enter mb-8">
  <h1 class="text-4xl font-bold">Documentation</h1>
  <p class="mt-2 opacity-50">Guides for developers, admins, and users.</p>
</div>

<div class="stagger grid gap-5 sm:grid-cols-3">
  {#if $isLoggedIn && $isAdmin}
    <a href="/docs/developer" class="frame-lift flex flex-col items-center p-6 text-center">
      <span class="mb-3 text-4xl">💻</span>
      <h2 class="font-bold">Developer Guide</h2>
      <p class="mt-1 text-sm opacity-50">Architecture, setup, API reference, testing.</p>
      <span class="btn-pill btn-pill-primary btn-pill-sm mt-3">Read Guide</span>
    </a>

    <a href="/docs/admin" class="frame-lift flex flex-col items-center p-6 text-center">
      <span class="mb-3 text-4xl">⚙️</span>
      <h2 class="font-bold">Admin Guide</h2>
      <p class="mt-1 text-sm opacity-50">Manage quizzes, categories, users, security.</p>
      <span class="btn-pill btn-pill-primary btn-pill-sm mt-3">Read Guide</span>
    </a>
  {/if}

  <a href="/docs/user" class="frame-lift flex flex-col items-center p-6 text-center"
    class:sm:col-span-3={!($isLoggedIn && $isAdmin)}
  >
    <span class="mb-3 text-4xl">📖</span>
    <h2 class="font-bold">User Guide</h2>
    <p class="mt-1 text-sm opacity-50">Take quizzes, track progress, create your own.</p>
    <span class="btn-pill btn-pill-primary btn-pill-sm mt-3">Read Guide</span>
  </a>
</div>
