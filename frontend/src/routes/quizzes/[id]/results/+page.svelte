<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import { isLoggedIn } from '$lib/stores/auth';
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();
  let quiz = data.quiz;

  let attempt: any = $state(null);
  let loading = $state(true);
  let score = $state(0);
  let total = $state(quiz.questions?.length || 0);
  let shareCode = $state('');
  let shareUrl = $state('');
  let shareModal = $state(false);
  let challengeCode = $state('');
  let challengeCreated = $state(false);
  let rank: any = $state(null);
  let attemptId = $state('');
  let challengeParam = $state('');
  let percentage = $derived(total > 0 ? Math.round((score / total) * 100) : 0);
  let grade = $derived(
    percentage <= 40 ? 'Failed' : percentage <= 59 ? 'Pass' : percentage <= 69 ? 'Good' : 'Excellent'
  );
  let gradeColor = $derived(
    percentage <= 40 ? 'error' : percentage <= 59 ? 'warning' : percentage <= 69 ? 'primary' : 'success'
  );

  async function createShareLink() {
    try {
      const result = await api.createShareLink({ quiz_id: quiz.id, attempt_id: attemptId! });
      shareCode = result.code;
      shareUrl = `${window.location.origin}/quizzes/${quiz.id}?share=${result.code}`;
      shareModal = true;
    } catch (e: any) {
      alert(e.message);
    }
  }

  async function createChallenge() {
    try {
      const result = await api.createChallenge({
        quiz_id: quiz.id,
        score_to_beat: score,
        total_questions: total,
        challenger_attempt_id: attemptId!,
      });
      challengeCode = result.challenge_code;
      challengeCreated = true;
    } catch (e: any) {
      alert(e.message);
    }
  }

  async function copyShareUrl() {
    try {
      await navigator.clipboard.writeText(shareUrl);
    } catch {
      // fallback
    }
  }

  onMount(async () => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      attemptId = params.get('attemptId') || '';
      challengeParam = params.get('challenge') || '';
    }
    if (attemptId) {
      try {
        attempt = await api.getAttempt(attemptId);
        if (attempt) {
          score = attempt.score;
          total = attempt.total;
        }
      } catch (e) {
        // fallback
      }
    }

    // Fetch rank
    if (attemptId && $isLoggedIn) {
      try {
        const lb = await api.getLeaderboard(quiz.id, 20, 'all');
        const myEntry = lb.entries?.find((e: any) => e.attempt_id === attemptId);
        if (myEntry) rank = myEntry;
      } catch (e) {
        // rank not available
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
        {percentage >= 60 ? 'Congratulations!' : 'Keep trying!'}
      </h2>

      {#if rank}
        <div class="mt-2 text-lg font-semibold text-[var(--color-primary-500)]">
          Rank #{rank.rank}
        </div>
      {/if}

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

      <!-- Actions -->
      <div class="mt-8 flex flex-wrap justify-center gap-3">
        <a href="/quizzes/{quiz.id}/take" class="btn-pill btn-pill-outline">Retry Quiz</a>
        <a href="/quizzes" class="btn-pill btn-pill-primary">Browse More</a>
      </div>

      {#if $isLoggedIn && attemptId}
        <div class="mt-6 flex flex-wrap justify-center gap-3 border-t border-[var(--color-surface-300-700)] pt-6">
          <button class="btn-pill btn-pill-outline" onclick={createShareLink}>
            Share Result
          </button>
          <button class="btn-pill btn-pill-outline" onclick={createChallenge} disabled={challengeCreated}>
            {challengeCreated ? 'Challenge Created!' : 'Challenge Friend'}
          </button>
        </div>

        {#if challengeCreated}
          <div class="mt-3 frame p-3">
            <p class="text-sm opacity-60">Share this challenge link:</p>
            <div class="mt-1 flex items-center gap-2">
              <input
                class="flex-1 rounded-lg border border-[var(--color-surface-300-700)] bg-transparent px-3 py-2 text-sm outline-none"
                readonly
                value="{window.location.origin}/challenge/{challengeCode}"
              />
              <button class="btn-pill btn-pill-sm btn-pill-primary" onclick={copyShareUrl}>Copy</button>
            </div>
          </div>
        {/if}
      {/if}
    </div>
  {/if}
</div>

<!-- Share Modal -->
{#if shareModal}
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onclick={() => shareModal = false}>
    <div class="frame w-full max-w-sm p-6" onclick={(e) => e.stopPropagation()}>
      <h3 class="text-lg font-bold">Share Your Result</h3>
      <div class="mt-4">
        <label class="text-xs font-medium uppercase tracking-wider opacity-40">Share Link</label>
        <div class="mt-1 flex items-center gap-2">
          <input
            class="flex-1 rounded-lg border border-[var(--color-surface-300-700)] bg-transparent px-3 py-2 text-sm outline-none"
            readonly
            value={shareUrl}
          />
          <button class="btn-pill btn-pill-sm btn-pill-primary" onclick={copyShareUrl}>Copy</button>
        </div>
      </div>
      <div class="mt-4">
        <label class="text-xs font-medium uppercase tracking-wider opacity-40">OG URL</label>
        <p class="mt-1 text-sm opacity-50">/share/{shareCode}/og</p>
      </div>
      <button class="btn-pill btn-pill-outline mt-5 w-full" onclick={() => shareModal = false}>Close</button>
    </div>
  </div>
{/if}
