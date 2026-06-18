<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();
  let quiz = data.quiz;

  let attempt: any = $state(null);
  let loading = $state(true);
  let score = $state(0);
  let total = $state(quiz.questions?.length || 0);

  let attemptId = $derived($page.url.searchParams.get('attemptId'));
  let percentage = $derived(total > 0 ? Math.round((score / total) * 100) : 0);
  let grade = $derived(
    percentage <= 40 ? 'Failed' : percentage <= 59 ? 'Pass' : percentage <= 69 ? 'Good' : 'Excellent'
  );
  let gradeColor = $derived(
    percentage <= 40 ? 'error' : percentage <= 59 ? 'warning' : percentage <= 69 ? 'primary' : 'success'
  );

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

<svelte:head>
  <title>Results — {quiz.title}</title>
</svelte:head>

<div class="page-enter mx-auto max-w-lg">
  <a href="/quizzes/{quiz.id}" class="mb-6 inline-flex items-center gap-1 text-sm font-medium opacity-50 transition-opacity hover:opacity-100">
    ← {quiz.title}
  </a>

  {#if loading}
    <div class="flex justify-center py-20">
      <span class="text-sm opacity-40">Loading...</span>
    </div>
  {:else}
    <div class="frame p-8 text-center">
      <h2 class="text-3xl font-bold">
        {percentage >= 60 ? '🎉 Congratulations!' : 'Keep trying!'}
      </h2>

      <!-- Score circle -->
      <div class="mx-auto mt-6 flex h-32 w-32 items-center justify-center rounded-full border-4 border-[var(--color-{gradeColor}-500)]">
        <div>
          <div class="text-3xl font-extrabold text-[var(--color-{gradeColor}-500)]">{percentage}%</div>
        </div>
      </div>

      <div class="mt-8 grid grid-cols-3 gap-4">
        <div>
          <div class="text-xs font-medium uppercase tracking-wider opacity-40">Score</div>
          <div class="mt-1 text-xl font-bold">{score}/{total}</div>
        </div>
        <div>
          <div class="text-xs font-medium uppercase tracking-wider opacity-40">Grade</div>
          <div class="mt-1 text-xl font-bold text-[var(--color-{gradeColor}-500)]">{grade}</div>
        </div>
        {#if attempt?.time_spent}
          <div>
            <div class="text-xs font-medium uppercase tracking-wider opacity-40">Time</div>
            <div class="mt-1 text-xl font-bold">
              {Math.floor(attempt.time_spent / 60)}:{String(attempt.time_spent % 60).padStart(2, '0')}
            </div>
          </div>
        {/if}
      </div>

      <p class="mt-6 text-sm opacity-50">
        You got <span class="font-semibold text-[var(--color-primary-500)]">{score}</span> out of
        <span class="font-semibold text-[var(--color-primary-500)]">{total}</span> questions correct
      </p>

      <div class="mt-8 flex justify-center gap-3">
        <a href="/quizzes/{quiz.id}/take" class="btn-pill btn-pill-outline">Retry Quiz</a>
        <a href="/quizzes" class="btn-pill btn-pill-primary">Browse More</a>
      </div>
    </div>
  {/if}
</div>
