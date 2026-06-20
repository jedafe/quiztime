<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import { isLoggedIn } from '$lib/stores/auth';
  import { goto } from '$app/navigation';

  let { data } = $props();

  let badges = $state<any[]>(data.badges || []);
  let profile = $state<any>(data.profile || null);
  let xpHistory = $state<any[]>([]);
  let xpTotal = $state(0);
  let xpPage = $state(1);
  let xpLoading = $state(false);

  onMount(async () => {
    if (!$isLoggedIn) { goto('/login'); return; }
    // Fetch profile+history if not loaded server-side
    if (!profile) {
      try { profile = await api.getMyProfile(); } catch {}
    }
    await loadXpHistory();
  });

  async function loadXpHistory() {
    xpLoading = true;
    try {
      const r = await api.getXpHistory(xpPage, 20);
      xpHistory = r.items;
      xpTotal = r.total;
    } catch {}
    xpLoading = false;
  }
</script>

<svelte:head>
  <title>Achievements — QuizTime</title>
</svelte:head>

<div class="page-enter">
  <div class="flex items-end justify-between">
    <div>
      <p class="eyebrow">Gamification</p>
      <h1 class="text-3xl font-bold tracking-[-0.03em]">Achievements & Badges</h1>
    </div>
  </div>

  {#if profile}
    <div class="mt-6 flex flex-wrap gap-4">
      <div class="stat-pill text-center">
        <span class="text-2xl font-bold text-[var(--color-primary-500)]">Level {profile.level}</span>
        <span class="eyebrow justify-center">Level</span>
      </div>
      <div class="stat-pill text-center">
        <span class="text-2xl font-bold text-[var(--color-secondary-500)]">{profile.xp} XP</span>
        <span class="eyebrow justify-center">Total XP</span>
      </div>
      <div class="stat-pill text-center">
        <span class="text-2xl font-bold text-[var(--color-warning-500)]">{(profile.xp % 100)}/100</span>
        <span class="eyebrow justify-center">XP to Next Level</span>
      </div>
      <div class="stat-pill text-center">
        <span class="text-2xl font-bold text-[var(--color-error-500)]">{profile.streak_count || 0}🔥</span>
        <span class="eyebrow justify-center">Day Streak</span>
      </div>
    </div>

    <!-- XP Progress Bar -->
    <div class="mt-4 frame p-4">
      <div class="flex items-baseline justify-between mb-2">
        <span class="text-sm font-medium">Level {profile.level} Progress</span>
        <span class="text-xs opacity-50">{profile.xp % 100} / 100 XP</span>
      </div>
      <div class="h-3 w-full overflow-hidden rounded-full bg-[var(--color-surface-200-800)]">
        <div
          class="h-full rounded-full bg-gradient-to-r from-[var(--color-primary-500)] to-[var(--color-secondary-500)] transition-all"
          style="width: {profile.xp % 100}%"
        ></div>
      </div>
    </div>
  {/if}

  <!-- Badges Grid -->
  <section class="mt-8">
    <h2 class="text-xl font-bold tracking-[-0.02em] mb-4">Badges</h2>
    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {#each badges as badge}
        <div
          class="frame flex items-center gap-4 p-4 transition-all"
          class:opacity-40={!badge.earned_at}
        >
          <span class="flex h-14 w-14 items-center justify-center rounded-xl bg-[var(--color-surface-200-800)] text-2xl">
            {badge.icon}
          </span>
          <div class="flex-1 min-w-0">
            <p class="font-semibold">{badge.name}</p>
            <p class="text-xs opacity-60">{badge.description}</p>
            {#if badge.earned_at}
              <p class="mt-1 text-xs text-[var(--color-success-500)]">
                Earned {new Date(badge.earned_at).toLocaleDateString()}
              </p>
            {:else}
              <p class="mt-1 text-xs opacity-40">Not yet earned</p>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  </section>

  <!-- XP History -->
  <section class="mt-8 mb-12">
    <h2 class="text-xl font-bold tracking-[-0.02em] mb-4">XP History</h2>
    {#if xpLoading}
      <div class="frame py-8 text-center"><span class="opacity-40">Loading...</span></div>
    {:else if xpHistory.length === 0}
      <div class="frame py-8 text-center"><span class="opacity-40">No XP history yet. Complete quizzes to earn XP!</span></div>
    {:else}
      <div class="frame overflow-hidden">
        <table class="table-frame">
          <thead>
            <tr>
              <th>Source</th>
              <th class="text-center">XP</th>
              <th class="text-right">Date</th>
            </tr>
          </thead>
          <tbody>
            {#each xpHistory as event}
              <tr>
                <td class="capitalize">{event.source.replace('_', ' ')}</td>
                <td class="text-center font-medium text-[var(--color-success-500)]">+{event.amount}</td>
                <td class="text-right text-xs opacity-40">{new Date(event.created_at).toLocaleDateString()}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
      {#if xpTotal > 20}
        <div class="mt-3 flex justify-center gap-2">
          <button class="btn-pill btn-pill-ghost btn-pill-sm" disabled={xpPage <= 1} onclick={() => { xpPage--; loadXpHistory(); }}>Prev</button>
          <span class="flex items-center text-sm opacity-50">Page {xpPage}</span>
          <button class="btn-pill btn-pill-ghost btn-pill-sm" disabled={xpPage * 20 >= xpTotal} onclick={() => { xpPage++; loadXpHistory(); }}>Next</button>
        </div>
      {/if}
    {/if}
  </section>
</div>
