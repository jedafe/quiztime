<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import { isLoggedIn, currentUser } from '$lib/stores/auth';
  import { translate } from '$lib/stores/i18n';
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();
  let quiz = data.quiz;
  let stats: any = $state(null);
  let tab = $state<'stats' | 'leaderboard' | 'reviews'>('stats');

  // ── Leaderboard state ──
  let leaderboard: any = $state(null);
  let lbLoading = $state(false);
  let lbPeriod = $state('all');

  async function loadLeaderboard() {
    lbLoading = true;
    try {
      leaderboard = await api.getLeaderboard(quiz.id, 20, lbPeriod);
    } catch (e) {
      leaderboard = null;
    }
    lbLoading = false;
  }

  function switchPeriod(p: string) {
    lbPeriod = p;
    loadLeaderboard();
  }

  function formatTime(seconds: number): string {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${String(s).padStart(2, '0')}`;
  }

  function rankDisplay(rank: number): string {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return `#${rank}`;
  }

  // ── Reviews state ──
  let reviews: any[] = $state([]);
  let reviewStats: any = $state(null);
  let myRating: any = $state(null);
  let rvLoading = $state(false);
  let rvScore = $state(0);
  let rvReview = $state('');
  let rvSubmitting = $state(false);
  let rvError = $state('');
  let rvSuccess = $state('');

  async function loadReviews() {
    rvLoading = true;
    try {
      const [rResult, sResult] = await Promise.all([
        api.listRatings(quiz.id),
        api.ratingStats(quiz.id),
      ]);
      reviews = rResult.items;
      reviewStats = sResult;
    } catch {}
    try {
      myRating = await api.myRating(quiz.id);
      rvScore = myRating.score;
      rvReview = myRating.review || '';
    } catch {
      myRating = null;
    }
    rvLoading = false;
  }

  async function submitRating() {
    if (rvScore < 1) { rvError = 'Please select a score'; return; }
    rvSubmitting = true;
    rvError = '';
    rvSuccess = '';
    try {
      myRating = await api.createRating({ quiz_id: quiz.id, score: rvScore, review: rvReview || undefined });
      rvSuccess = 'Rating saved!';
      await loadReviews();
    } catch (e: any) {
      rvError = e.message;
    }
    rvSubmitting = false;
  }

  function starLabel(score: number): string {
    return '★'.repeat(score) + '☆'.repeat(5 - score);
  }

  // ── Export ──
  let exportLoading = $state(false);
  let exportError = $state('');

  async function handleExport() {
    exportLoading = true;
    exportError = '';
    try {
      const data = await api.exportQuiz(quiz.id);
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${quiz.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e: any) {
      exportError = e.message;
    }
    exportLoading = false;
  }

  // ── Embed ──
  let embedSnippet = $state('');
  let showEmbed = $state(false);
  let embedCopied = $state(false);

  async function loadEmbedSnippet() {
    try {
      const result = await api.getEmbedSnippet(quiz.id);
      embedSnippet = result.html;
      showEmbed = true;
      embedCopied = false;
    } catch (e: any) {
      exportError = e.message;
    }
  }

  async function copyEmbed() {
    try {
      await navigator.clipboard.writeText(embedSnippet);
      embedCopied = true;
      setTimeout(() => embedCopied = false, 2000);
    } catch {}
  }

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
    {$translate('quizDetail.backToQuizzes')}
  </a>

  <div class="frame p-8">
    <div class="flex items-center gap-3">
      <h1 class="text-3xl font-bold tracking-[-0.03em]">{quiz.title}</h1>
      {#if quiz.language && quiz.language !== 'en'}
        <span class="rounded-full bg-[var(--color-primary-500)]/10 px-2.5 py-0.5 text-xs font-medium text-[var(--color-primary-500)]">{quiz.language === 'es' ? 'Español' : 'Français'}</span>
      {/if}
    </div>
    <p class="mt-2 opacity-50">{quiz.description || $translate('quizDetail.noDescription')}</p>

    <div class="stagger mt-8 grid grid-cols-3 gap-4 sm:gap-6">
      <div class="stat-pill text-center">
        <span class="text-2xl font-bold text-[var(--color-primary-500)]">{quiz.questions?.length || 0}</span>
        <span class="eyebrow justify-center">{$translate('quizDetail.questions')}</span>
      </div>
      <div class="stat-pill text-center">
        <span class="text-2xl font-bold text-[var(--color-secondary-500)]">{quiz.attempt_count || 0}</span>
        <span class="eyebrow justify-center">{$translate('quizDetail.attempts')}</span>
      </div>
      <div class="stat-pill text-center">
        <span class="text-2xl font-bold text-[var(--color-warning-500)]">{quiz.avg_rating > 0 ? quiz.avg_rating : '—'}</span>
        <span class="eyebrow justify-center">{$translate('quizDetail.rating')}</span>
      </div>
    </div>

    <div class="mt-8 flex justify-end gap-2">
      {#if $isLoggedIn && ($currentUser?.id === quiz.created_by || $currentUser?.role === 'admin')}
        <a href="/quizzes/{quiz.id}/edit" class="btn-pill btn-pill-outline">{$translate('quizDetail.editQuiz')}</a>
        <button onclick={handleExport} class="btn-pill btn-pill-outline" disabled={exportLoading}>
          {exportLoading ? $translate('quizDetail.exporting') : $translate('quizDetail.exportJson')}
        </button>
        <button onclick={loadEmbedSnippet} class="btn-pill btn-pill-outline">{$translate('quizDetail.embed')}</button>
      {/if}
      <a href="/quizzes/{quiz.id}/take" class="btn-pill btn-pill-primary">{$translate('quizDetail.startQuiz')}</a>
    </div>
    {#if exportError}
      <p class="mt-2 text-right text-xs text-[var(--color-error-500)]">{exportError}</p>
    {/if}
  </div>

  {#if showEmbed}
    <div class="frame mt-4 p-4">
      <div class="flex items-center justify-between">
        <h3 class="font-semibold text-sm">{$translate('quizDetail.embedThisQuiz')}</h3>
        <button class="text-xs opacity-50 hover:opacity-100" onclick={() => showEmbed = false}>{$translate('quizDetail.close')}</button>
      </div>
      <p class="mt-1 text-xs opacity-50">{$translate('quizDetail.embedInstructions')}</p>
      <pre class="mt-2 overflow-x-auto rounded-lg bg-[var(--color-surface-100-900)] p-3 text-xs">{embedSnippet}</pre>
      <button onclick={copyEmbed} class="btn-pill btn-pill-primary btn-pill-sm mt-2">
        {embedCopied ? $translate('quizDetail.copied') : $translate('quizDetail.copyHtml')}
      </button>
    </div>
  {/if}

  <!-- Tab bar -->
  <div class="mt-8 flex gap-1 border-b border-[var(--color-surface-300-700)] pb-2">
    <button
      class="btn-pill btn-pill-ghost btn-pill-sm"
      style={tab === 'stats' ? 'background-color:var(--color-primary-500);color:#fff' : ''}
      onclick={() => tab = 'stats'}
    >{$translate('quizDetail.statistics')}</button>
    <button
      class="btn-pill btn-pill-ghost btn-pill-sm"
      style={tab === 'leaderboard' ? 'background-color:var(--color-primary-500);color:#fff' : ''}
      onclick={() => tab = 'leaderboard'}
    >{$translate('quizDetail.leaderboard')}</button>
    <button
      class="btn-pill btn-pill-ghost btn-pill-sm"
      style={tab === 'reviews' ? 'background-color:var(--color-primary-500);color:#fff' : ''}
      onclick={() => { tab = 'reviews'; loadReviews(); }}
    >{$translate('quizDetail.reviews')}</button>
  </div>

  {#if tab === 'stats'}
    <div class="mt-6 frame p-6 text-center">
      {#if stats}
        <div class="grid grid-cols-3 gap-4">
          <div>
            <div class="text-2xl font-bold text-[var(--color-primary-500)]">{stats.total_attempts}</div>
            <div class="text-xs uppercase tracking-wider opacity-40 mt-1">{$translate('quizDetail.totalAttempts')}</div>
          </div>
          <div>
            <div class="text-2xl font-bold text-[var(--color-secondary-500)]">{stats.avg_percentage}%</div>
            <div class="text-xs uppercase tracking-wider opacity-40 mt-1">{$translate('quizDetail.avgScore')}</div>
          </div>
          <div>
            <div class="text-2xl font-bold text-[var(--color-tertiary-500)]">{stats.avg_time_spent || 0}s</div>
            <div class="text-xs uppercase tracking-wider opacity-40 mt-1">{$translate('quizDetail.avgTime')}</div>
          </div>
        </div>
      {:else}
        <p class="py-8 text-sm opacity-40">{$translate('quizDetail.noStatsYet')}</p>
      {/if}
    </div>
  {:else if tab === 'leaderboard'}
    <div class="mt-6">
      <div class="mb-4 flex gap-1">
        {#each ['all', 'month', 'week', 'today'] as p}
          <button
            class="btn-pill btn-pill-ghost btn-pill-sm"
            style={lbPeriod === p ? 'background-color:var(--color-primary-500);color:#fff' : ''}
            onclick={() => switchPeriod(p)}
          >
            {p === 'all' ? $translate('quizDetail.allTime') : p === 'month' ? $translate('quizDetail.thisMonth') : p === 'week' ? $translate('quizDetail.thisWeek') : $translate('quizDetail.today')}
          </button>
        {/each}
      </div>

      {#if lbLoading}
        <div class="flex justify-center py-10"><span class="text-sm opacity-40">{$translate('quizDetail.loading')}</span></div>
      {:else if !leaderboard || leaderboard.entries.length === 0}
        <div class="py-10 text-center">
          <p class="text-sm opacity-50">{$translate('quizDetail.noAttemptsYet')}</p>
        </div>
      {:else}
        <div class="frame overflow-hidden">
          <table class="table-frame">
            <thead>
              <tr>
                <th class="w-12">{$translate('quizDetail.rank')}</th>
                <th>{$translate('quizDetail.user')}</th>
                <th class="text-right">{$translate('quizDetail.score')}</th>
                <th class="text-right">{$translate('quizDetail.percent')}</th>
                <th class="hidden sm:table-cell text-right">{$translate('quizDetail.time')}</th>
                <th class="hidden md:table-cell text-right">{$translate('quizDetail.date')}</th>
              </tr>
            </thead>
            <tbody>
              {#each leaderboard.entries as entry}
                <tr
                  class="transition-colors"
                  style={entry.user_id === $currentUser?.id ? 'background-color: color-mix(in srgb, var(--color-primary-500) 10%, transparent)' : ''}
                >
                  <td class="text-lg font-bold">{@html rankDisplay(entry.rank)}</td>
                  <td class="font-medium">
                    {entry.username}
                    {#if entry.user_id === $currentUser?.id}
                      <span class="ml-1.5 text-xs font-semibold text-[var(--color-primary-500)]">{$translate('quizDetail.you')}</span>
                    {/if}
                  </td>
                  <td class="text-right font-semibold">{entry.score}/{entry.total}</td>
                  <td class="text-right font-semibold">{entry.percentage}%</td>
                  <td class="hidden sm:table-cell text-right opacity-60">{formatTime(entry.time_spent)}</td>
                  <td class="hidden md:table-cell text-right text-xs opacity-40">
                    {new Date(entry.created_at).toLocaleDateString()}
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>

        {#if leaderboard.current_user_entry && leaderboard.current_user_rank > leaderboard.entries.length}
          <div class="mt-3 frame p-3" style="border: 2px solid color-mix(in srgb, var(--color-primary-500) 30%, transparent);">
            <div class="flex items-center justify-between text-sm">
              <span>
                <span class="font-bold">#{leaderboard.current_user_rank}</span>
                <span class="ml-1 opacity-60">{leaderboard.current_user_entry.username}</span>
                <span class="ml-1 text-xs opacity-40">{$translate('quizDetail.you')}</span>
              </span>
              <span class="font-semibold">{leaderboard.current_user_entry.score}/{leaderboard.current_user_entry.total}</span>
              <span class="font-semibold">{leaderboard.current_user_entry.percentage}%</span>
              <span class="hidden sm:inline opacity-60">{formatTime(leaderboard.current_user_entry.time_spent)}</span>
            </div>
          </div>
        {/if}

        <p class="mt-3 text-center text-xs opacity-40">
          {$translate('quizDetail.participants_plural', {count: leaderboard.total_entries})}
        </p>
      {/if}
    </div>
  {:else if tab === 'reviews'}
    <!-- Reviews -->
    <div class="mt-6">
      {#if reviewStats}
        <div class="frame mb-4 p-4">
          <div class="flex items-center gap-4">
            <div class="text-center">
              <div class="text-3xl font-bold text-[var(--color-warning-500)]">{reviewStats.avg_rating}</div>
              <div class="text-xs opacity-40">{$translate('quizDetail.outOf5')}</div>
            </div>
            <div class="flex-1">
              <div class="flex gap-0.5 text-lg text-[var(--color-warning-500)]">{starLabel(Math.round(reviewStats.avg_rating))}</div>
              <div class="mt-1 text-sm opacity-50">{$translate('quizDetail.ratings_plural', {count: reviewStats.total_ratings})}</div>
              <div class="mt-2 space-y-0.5">
                {#each [5, 4, 3, 2, 1] as s}
                  <div class="flex items-center gap-2 text-xs">
                    <span class="w-4 text-right">{s}</span>
                    <div class="h-2 flex-1 rounded-full bg-[var(--color-surface-200-800)]">
                      <div
                        class="h-full rounded-full bg-[var(--color-warning-500)] transition-all"
                        style="width: {reviewStats.total_ratings > 0 ? (reviewStats.distribution[s] || 0) / reviewStats.total_ratings * 100 : 0}%"
                      ></div>
                    </div>
                    <span class="w-6 text-right opacity-40">{reviewStats.distribution[s] || 0}</span>
                  </div>
                {/each}
              </div>
            </div>
          </div>
        </div>
      {/if}

      {#if $isLoggedIn}
        <div class="frame mb-4 p-4">
          <h3 class="mb-3 font-semibold">{myRating ? $translate('quizDetail.yourRating') : $translate('quizDetail.rateThisQuiz')}</h3>
          <div class="flex gap-1 text-2xl">
            {#each [1, 2, 3, 4, 5] as s}
              <button
                class="transition-colors"
                style="color: {s <= rvScore ? 'var(--color-warning-500)' : 'var(--color-surface-400-600)'}"
                onclick={() => rvScore = s}
              >★</button>
            {/each}
          </div>
          <textarea
            bind:value={rvReview}
            placeholder={$translate('quizDetail.optionalReview')}
            class="mt-3 w-full rounded-xl border border-[var(--color-surface-300-700)] bg-[var(--color-surface-50-950)] p-3 text-sm outline-none transition-colors focus:border-[var(--color-primary-500)]"
            rows="3"
          ></textarea>
          {#if rvError}<p class="mt-1 text-xs text-[var(--color-error-500)]">{rvError}</p>{/if}
          {#if rvSuccess}<p class="mt-1 text-xs text-[var(--color-success-500)]">{rvSuccess}</p>{/if}
          <button
            onclick={submitRating}
            disabled={rvSubmitting}
            class="btn-pill btn-pill-primary mt-3"
          >{rvSubmitting ? $translate('quizDetail.saving') : $translate('quizDetail.saveRating')}</button>
        </div>
      {:else}
        <div class="frame mb-4 p-4 text-center">
          <p class="text-sm opacity-50">{$translate('quizDetail.pleaseLogIn', {loginLink: '<a href="/login" class="text-[var(--color-primary-500)]">' + $translate('quizDetail.logIn') + '</a>'})}</p>
        </div>
      {/if}

      {#if rvLoading}
        <div class="flex justify-center py-6"><span class="text-sm opacity-40">{$translate('quizDetail.loading')}</span></div>
      {:else if reviews.length === 0}
        <div class="py-10 text-center">
          <p class="text-sm opacity-50">{$translate('quizDetail.noReviewsYet')}</p>
        </div>
      {:else}
        <div class="space-y-3">
          {#each reviews as r}
            <div class="frame p-4">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <span class="font-medium text-sm">{r.username}</span>
                  <span class="text-sm text-[var(--color-warning-500)]">{starLabel(r.score)}</span>
                </div>
                <span class="text-xs opacity-40">{new Date(r.created_at).toLocaleDateString()}</span>
              </div>
              {#if r.review}
                <p class="mt-1 text-sm opacity-60">{r.review}</p>
              {/if}
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {/if}
</div>
