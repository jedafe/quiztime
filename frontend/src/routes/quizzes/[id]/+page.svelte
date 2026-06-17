<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import { isLoggedIn, currentUser } from '$lib/stores/auth';
  import { page } from '$app/stores';
  import type { PageData } from './$types';

  export let data: PageData;
  const quiz = data.quiz;

  let stats: any = null;

  onMount(async () => {
    try {
      stats = await api.quizStats(quiz.id);
    } catch (e) {
      // stats endpoint might fail if no attempts
    }
  });
</script>

<div class="mb-6">
  <a href="/quizzes" class="btn btn-ghost btn-sm">← Back to Quizzes</a>
</div>

<div class="card bg-base-100 shadow-xl">
  <div class="card-body">
    <h1 class="card-title text-3xl">{quiz.title}</h1>
    <p class="text-base-content/70">{quiz.description || 'No description'}</p>

    <div class="flex gap-4 mt-4">
      <div class="stat">
        <div class="stat-title">Questions</div>
        <div class="stat-value text-primary">{quiz.questions?.length || 0}</div>
      </div>
      {#if stats}
        <div class="stat">
          <div class="stat-title">Attempts</div>
          <div class="stat-value text-secondary">{stats.total_attempts}</div>
        </div>
        <div class="stat">
          <div class="stat-title">Avg Score</div>
          <div class="stat-value text-accent">{stats.avg_percentage}%</div>
        </div>
      {/if}
    </div>

    <div class="card-actions justify-end mt-6">
      {#if $isLoggedIn && ($currentUser?.id === quiz.created_by || $currentUser?.role === 'admin')}
        <a href="/quizzes/{quiz.id}/edit" class="btn btn-outline">Edit Quiz</a>
      {/if}
      <a href="/quizzes/{quiz.id}/take" class="btn btn-primary btn-lg">Start Quiz</a>
    </div>
  </div>
</div>
