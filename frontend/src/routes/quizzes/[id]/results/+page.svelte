<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import type { PageData } from './$types';

  export let data: PageData;
  const quiz = data.quiz;

  let attempt: any = null;
  let loading = true;
  let score = 0;
  let total = quiz.questions?.length || 0;

  $: attemptId = $page.url.searchParams.get('attemptId');

  $: percentage = total > 0 ? Math.round((score / total) * 100) : 0;
  $: grade =
    percentage <= 40 ? 'Failed' : percentage <= 59 ? 'Pass' : percentage <= 69 ? 'Good' : 'Excellent';
  $: gradeColor =
    percentage <= 40 ? 'error' : percentage <= 59 ? 'warning' : percentage <= 69 ? 'primary' : 'success';

  onMount(async () => {
    if (attemptId) {
      try {
        attempt = await api.getAttempt(attemptId);
        if (attempt) {
          score = attempt.score;
          total = attempt.total;
        }
      } catch (e) {
        // fallback to defaults
      }
    }
    loading = false;
  });
</script>

<div class="mb-6">
  <a href="/quizzes/{quiz.id}" class="btn btn-ghost btn-sm">← {quiz.title}</a>
</div>

{#if loading}
  <div class="flex justify-center py-16">
    <span class="loading loading-spinner loading-lg"></span>
  </div>
{:else}
  <div class="card bg-base-100 shadow-xl max-w-lg mx-auto">
    <div class="card-body items-center text-center">
      <h2 class="card-title text-3xl mb-2">
        {percentage >= 60 ? 'Congratulations!' : 'Try Again!'}
      </h2>

      <!-- Score Circle -->
      <div class="radial-progress text-4xl font-bold mt-4"
        style="--value:{percentage}; color: hsl(var(--{gradeColor}))">
        {percentage}%
      </div>

      <div class="stats mt-6 w-full">
        <div class="stat place-items-center">
          <div class="stat-title">Score</div>
          <div class="stat-value text-primary">{score}/{total}</div>
        </div>
        <div class="stat place-items-center">
          <div class="stat-title">Grade</div>
          <div class="stat-value text-{gradeColor}">{grade}</div>
        </div>
        {#if attempt?.time_spent}
          <div class="stat place-items-center">
            <div class="stat-title">Time</div>
            <div class="stat-value">
              {Math.floor(attempt.time_spent / 60)}:{String(attempt.time_spent % 60).padStart(2, '0')}
            </div>
          </div>
        {/if}
      </div>

      <p class="mt-4 text-base-content/70">
        You got <span class="font-bold text-primary">{score}</span> out of
        <span class="font-bold text-primary">{total}</span> questions correct
      </p>

      <div class="card-actions mt-6 gap-3">
        <a href="/quizzes/{quiz.id}/take" class="btn btn-outline">Retry Quiz</a>
        <a href="/quizzes" class="btn btn-primary">Browse More</a>
      </div>
    </div>
  </div>
{/if}
