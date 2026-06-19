<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import { isLoggedIn, currentUser } from '$lib/stores/auth';
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();
  let quiz = data.quiz;
  let stats: any = $state(null);
  let tab = $state<'stats' | 'leaderboard'>('stats');

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

  <!-- Tab bar -->
  <div class="mt-8 flex gap-1 border-b border-[var(--color-surface-300-700)] pb-2">
    <button
      class="btn-pill btn-pill-ghost btn-pill-sm"
      style={tab === 'stats' ? 'background-color:var(--color-primary-500);color:#fff' : ''}
      onclick={() => tab = 'stats'}
    >Statistics</button>
    <button
      class="btn-pill btn-pill-ghost btn-pill-sm"
      style={tab === 'leaderboard' ? 'background-color:var(--color-primary-500);color:#fff' : ''}
      onclick={() => tab = 'leaderboard'}
    >Leaderboard</button>
  </div>

  {#if tab === 'stats'}
    <div class="mt-6 frame p-6 text-center">
      {#if stats}
        <div class="grid grid-cols-3 gap-4">
          <div>
            <div class="text-2xl font-bold text-[var(--color-primary-500)]">{stats.total_attempts}</div>
            <div class="text-xs uppercase tracking-wider opacity-40 mt-1">Total Attempts</div>
          </div>
          <div>
            <div class="text-2xl font-bold text-[var(--color-secondary-500)]">{stats.avg_percentage}%</div>
            <div class="text-xs uppercase tracking-wider opacity-40 mt-1">Avg Score</div>
          </div>
          <div>
            <div class="text-2xl font-bold text-[var(--color-tertiary-500)]">{stats.avg_time_spent || 0}s</div>
            <div class="text-xs uppercase tracking-wider opacity-40 mt-1">Avg Time</div>
          </div>
        </div>
      {:else}
        <p class="py-8 text-sm opacity-40">No statistics yet.</p>
      {/if}
    </div>
  {:else}
    <!-- Leaderboard -->
    <div class="mt-6">
      <div class="mb-4 flex gap-1">
        {#each ['all', 'month', 'week', 'today'] as p}
          <button
            class="btn-pill btn-pill-ghost btn-pill-sm"
            style={lbPeriod === p ? 'background-color:var(--color-primary-500);color:#fff' : ''}
            onclick={() => switchPeriod(p)}
          >
            {p === 'all' ? 'All Time' : p === 'month' ? 'This Month' : p === 'week' ? 'This Week' : 'Today'}
          </button>
        {/each}
      </div>

      {#if lbLoading}
        <div class="flex justify-center py-10"><span class="text-sm opacity-40">Loading...</span></div>
      {:else if !leaderboard || leaderboard.entries.length === 0}
        <div class="py-10 text-center">
          <p class="text-sm opacity-50">No attempts yet. Be the first!</p>
        </div>
      {:else}
        <div class="frame overflow-hidden">
          <table class="table-frame">
            <thead>
              <tr>
                <th class="w-12">Rank</th>
                <th>User</th>
                <th class="text-right">Score</th>
                <th class="text-right">%</th>
                <th class="hidden sm:table-cell text-right">Time</th>
                <th class="hidden md:table-cell text-right">Date</th>
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
                      <span class="ml-1.5 text-xs font-semibold text-[var(--color-primary-500)]">(you)</span>
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
                <span class="ml-1 text-xs opacity-40">(you)</span>
              </span>
              <span class="font-semibold">{leaderboard.current_user_entry.score}/{leaderboard.current_user_entry.total}</span>
              <span class="font-semibold">{leaderboard.current_user_entry.percentage}%</span>
              <span class="hidden sm:inline opacity-60">{formatTime(leaderboard.current_user_entry.time_spent)}</span>
            </div>
          </div>
        {/if}

        <p class="mt-3 text-center text-xs opacity-40">
          {leaderboard.total_entries} participant{leaderboard.total_entries !== 1 ? 's' : ''}
        </p>
      {/if}
    </div>
  {/if}
</div>
