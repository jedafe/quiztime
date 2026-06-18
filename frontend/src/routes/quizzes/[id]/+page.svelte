<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import { isLoggedIn, currentUser } from '$lib/stores/auth';
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();
  let quiz = data.quiz;
  let stats: any = $state(null);

  onMount(async () => {
    try {
      stats = await api.quizStats(quiz.id);
    } catch (e) {
      // stats endpoint might fail if no attempts
    }
  });
</script>

<svelte:head>
  <title>{quiz.title} — QuizTime</title>
</svelte:head>

<div class="page-enter">
  <a href="/quizzes" class="mb-6 inline-flex items-center gap-1 text-sm font-medium opacity-50 transition-opacity hover:opacity-100">
    ← Back to Quizzes
  </a>

  <div class="frame p-8">
    <h1 class="text-3xl font-bold tracking-[-0.03em]">{quiz.title}</h1>
    <p class="mt-2 opacity-50">{quiz.description || 'No description'}</p>

    <div class="stagger mt-8 grid grid-cols-3 gap-4 sm:gap-6">
      <div class="stat-pill text-center">
        <span class="text-2xl font-bold text-[var(--color-primary-500)]">{quiz.questions?.length || 0}</span>
        <span class="eyebrow justify-center">Questions</span>
      </div>
      {#if stats}
        <div class="stat-pill text-center">
          <span class="text-2xl font-bold text-[var(--color-secondary-500)]">{stats.total_attempts}</span>
          <span class="eyebrow justify-center">Attempts</span>
        </div>
        <div class="stat-pill text-center">
          <span class="text-2xl font-bold text-[var(--color-tertiary-500)]">{stats.avg_percentage}%</span>
          <span class="eyebrow justify-center">Avg Score</span>
        </div>
      {/if}
    </div>

    <div class="mt-8 flex justify-end gap-2">
      {#if $isLoggedIn && ($currentUser?.id === quiz.created_by || $currentUser?.role === 'admin')}
        <a href="/quizzes/{quiz.id}/edit" class="btn-pill btn-pill-outline">Edit Quiz</a>
      {/if}
      <a href="/quizzes/{quiz.id}/take" class="btn-pill btn-pill-primary">Start Quiz</a>
    </div>
  </div>
</div>
