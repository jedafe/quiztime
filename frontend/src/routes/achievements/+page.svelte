<script lang="ts">
  import { onMount } from 'svelte';
  import { translate } from '$lib/stores/i18n';
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
  <title>{$translate('achievements.title')} — QuizTime</title>
</svelte:head>

<div class="page-enter">
  <div class="flex items-end justify-between">
    <div>
      <p class="eyebrow">{$translate('achievements.title')}</p>
      <h1 class="text-3xl font-bold tracking-[-0.03em]">{$translate('achievements.achievements')}</h1>
    </div>
  </div>

  {#if profile}
    <div class="mt-6 flex flex-wrap gap-4">
      <div class="stat-pill text-center">
        <span class="text-2xl font-bold text-[var(--color-primary-500)]">{$translate('dashboard.level')} {profile.level}</span>
        <span class="eyebrow justify-center">{$translate('dashboard.level')}</span>
      </div>
      <div class="stat-pill text-center">
        <span class="text-2xl font-bold text-[var(--color-secondary-500)]">{profile.xp} {$translate('achievements.xp')}</span>
        <span class="eyebrow justify-center">{$translate('achievements.totalXp')}</span>
      </div>
      <div class="stat-pill text-center">
        <span class="text-2xl font-bold text-[var(--color-warning-500)]">{(profile.xp % 100)}/100</span>
        <span class="eyebrow justify-center">{$translate('achievements.xpToNext')}</span>
      </div>
      <div class="stat-pill text-center">
        <span class="text-2xl font-bold text-[var(--color-error-500)]">{profile.streak_count || 0}🔥</span>
        <span class="eyebrow justify-center">{$translate('achievements.dayStreak')}</span>
      </div>
    </div>

    <!-- XP Progress Bar -->
    <div class="mt-4 frame p-4">
      <div class="flex items-baseline justify-between mb-2">
        <span class="text-sm font-medium">{$translate('achievements.levelProgress', {level: profile.level})}</span>
        <span class="text-xs opacity-50">{profile.xp % 100} / 100 {$translate('achievements.xp')}</span>
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
    <h2 class="text-xl font-bold tracking-[-0.02em] mb-4">{$translate('achievements.badges')}</h2>
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
                {$translate('achievements.earned')} {new Date(badge.earned_at).toLocaleDateString()}
              </p>
            {:else}
              <p class="mt-1 text-xs opacity-40">{$translate('achievements.notYetEarned')}</p>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  </section>

  <!-- XP History -->
  <section class="mt-8 mb-12">
    <h2 class="text-xl font-bold tracking-[-0.02em] mb-4">{$translate('achievements.xpHistory')}</h2>
    {#if xpLoading}
      <div class="frame py-8 text-center"><span class="opacity-40">{$translate('general.loading')}</span></div>
    {:else if xpHistory.length === 0}
      <div class="frame py-8 text-center"><span class="opacity-40">{$translate('achievements.noHistory')}</span></div>
    {:else}
      <div class="frame overflow-hidden">
        <table class="table-frame">
          <thead>
            <tr>
              <th>{$translate('achievements.source')}</th>
              <th class="text-center">{$translate('achievements.xp')}</th>
              <th class="text-right">{$translate('achievements.date')}</th>
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
          <button class="btn-pill btn-pill-ghost btn-pill-sm" disabled={xpPage <= 1} onclick={() => { xpPage--; loadXpHistory(); }}>{$translate('achievements.prev')}</button>
          <span class="flex items-center text-sm opacity-50">{$translate('general.page')} {xpPage}</span>
          <button class="btn-pill btn-pill-ghost btn-pill-sm" disabled={xpPage * 20 >= xpTotal} onclick={() => { xpPage++; loadXpHistory(); }}>{$translate('achievements.next')}</button>
        </div>
      {/if}
    {/if}
  </section>
</div>
