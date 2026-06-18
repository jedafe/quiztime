<script lang="ts">
  import { api } from '$lib/api';
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();
</script>

<svelte:head>
  <title>Browse Quizzes — QuizTime</title>
</svelte:head>

<div class="page-enter">
  <div class="flex items-end justify-between">
    <div>
      <p class="eyebrow">Explore</p>
      <h1 class="text-3xl font-bold tracking-[-0.03em]">Browse Quizzes</h1>
    </div>
    <a href="/create" class="btn-pill btn-pill-primary btn-pill-sm">+ New Quiz</a>
  </div>

  {#if data.quizzes?.length === 0}
    <div class="mt-16 text-center">
      <p class="text-lg opacity-40">No quizzes yet.</p>
      <a href="/create" class="btn-pill btn-pill-primary mt-4">Create the First One</a>
    </div>
  {:else}
    <div class="stagger mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {#each data.quizzes as quiz}
        <a href="/quizzes/{quiz.id}" class="frame-lift block p-5">
          <h3 class="font-bold transition-colors group-hover:text-[var(--color-primary-500)]">{quiz.title}</h3>
          <p class="mt-1 line-clamp-2 text-sm opacity-50">{quiz.description || 'No description'}</p>
          <div class="mt-3 flex items-center justify-between">
            <span class="rounded-full bg-[var(--color-surface-200-800)] px-2.5 py-0.5 text-xs font-medium">{quiz.question_count} questions</span>
            <span class="btn-pill btn-pill-primary btn-pill-sm opacity-0 transition-opacity group-hover:opacity-100">Take Quiz →</span>
          </div>
        </a>
      {/each}
    </div>
  {/if}
</div>
