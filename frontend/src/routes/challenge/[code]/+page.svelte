<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  import { isLoggedIn } from '$lib/stores/auth';

  let challenge: any = $state(null);
  let loading = $state(true);
  let accepting = $state(false);
  let error = $state('');
  let code = $state('');

  onMount(async () => {
    code = $page.params.code || '';
    if (!code) {
      error = 'Challenge not found';
      loading = false;
      return;
    }
    try {
      challenge = await api.getChallenge(code);
    } catch (e: any) {
      error = e.message || 'Challenge not found';
    }
    loading = false;
  });

  async function acceptAndPlay() {
    if (accepting || !code) return;
    accepting = true;
    try {
      await api.acceptChallenge(code);
      goto(`/quizzes/${challenge.quiz_id}/take?challenge=${code}`);
    } catch (e: any) {
      error = e.message || 'Failed to accept challenge';
      accepting = false;
    }
  }
</script>

<svelte:head>
  <title>Challenge — {challenge?.quiz_title || 'QuizTime'}</title>
</svelte:head>

<div class="page-enter mx-auto max-w-lg">
  {#if loading}
    <div class="flex justify-center py-20"><span class="text-sm opacity-40">Loading...</span></div>
  {:else if error}
    <div class="frame p-8 text-center">
      <h2 class="text-xl font-bold">Challenge Not Found</h2>
      <p class="mt-2 opacity-50">{error}</p>
      <a href="/quizzes" class="btn-pill btn-pill-primary mt-6">Browse Quizzes</a>
    </div>
  {:else}
    <div class="frame p-8 text-center">
      <div class="text-5xl">⚔️</div>
      <h1 class="mt-4 text-2xl font-bold">You've Been Challenged!</h1>
      <p class="mt-2 opacity-50">
        <span class="font-semibold text-[var(--color-primary-500)]">{challenge.challenger_username}</span>
        scored <span class="font-semibold">{challenge.score_to_beat}/{challenge.total_questions}</span>
        on <span class="font-semibold">{challenge.quiz_title}</span>
      </p>

      <div class="mt-8">
        <div class="stat-pill text-center">
          <span class="text-3xl font-bold text-[var(--color-secondary-500)]">{challenge.score_to_beat}/{challenge.total_questions}</span>
          <span class="eyebrow justify-center">Score to Beat</span>
        </div>
      </div>

      {#if !$isLoggedIn}
        <div class="mt-6">
          <p class="mb-3 text-sm opacity-50">Login or register to accept this challenge</p>
          <a href="/login?redirect=/challenge/{code}" class="btn-pill btn-pill-primary">Login</a>
          <a href="/register?redirect=/challenge/{code}" class="btn-pill btn-pill-outline ml-2">Register</a>
        </div>
      {:else}
        <div class="mt-8 flex justify-center gap-3">
          <button class="btn-pill btn-pill-primary" onclick={acceptAndPlay} disabled={accepting}>
            {accepting ? 'Accepting...' : 'Accept Challenge'}
          </button>
          <a href="/quizzes" class="btn-pill btn-pill-outline">Maybe Later</a>
        </div>
      {/if}
    </div>
  {/if}
</div>
