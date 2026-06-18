<script lang="ts">
  import { page } from '$app/stores';
</script>

<svelte:head>
  <title>{$page.status} — QuizTime</title>
</svelte:head>

<div class="page-enter flex flex-col items-center justify-center py-24 text-center">
  <h1 class="text-7xl font-extrabold tracking-tighter text-[var(--color-error-500)]">{$page.status}</h1>
  <p class="mt-4 text-lg opacity-50">
    {$page.error?.message || 'Something went wrong'}
  </p>
  <div class="mt-8 flex gap-3">
    <a href="/" class="btn-pill btn-pill-primary">Go Home</a>
    <a href="/quizzes" class="btn-pill btn-pill-outline">Browse Quizzes</a>
  </div>
</div>
