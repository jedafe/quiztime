<script lang="ts">
  import { onMount } from 'svelte';
  import { translate } from '$lib/stores/i18n';
  import { api } from '$lib/api';
  import { currentUser, isLoggedIn } from '$lib/stores/auth';
  import { goto } from '$app/navigation';

  let quizzes: any[] = $state([]);
  let attempts: any[] = $state([]);
  let profile: any = $state(null);
  let badges: any[] = $state([]);
  let loading = $state(true);
  let error = $state('');

  onMount(async () => {
    if (!$isLoggedIn) {
      goto('/login');
      return;
    }

    try {
      const [quizPage, a, prof, b] = await Promise.all([
        api.listQuizzes(),
        api.myAttempts(),
        api.getMyProfile().catch(() => null),
        api.getAllBadges().catch(() => []),
      ]);
      const allQuizzes = quizPage.items ?? quizPage;
      quizzes = allQuizzes.filter((quiz: any) => quiz.created_by === $currentUser?.id || $currentUser?.role === 'admin');
      attempts = a;
      profile = prof;
      badges = b.filter((bdg: any) => bdg.earned_at);
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  });

  async function deleteQuiz(quizId: string) {
    if (!confirm('Delete this quiz?')) return;
    try {
      await api.deleteQuiz(quizId);
      quizzes = quizzes.filter((q) => q.id !== quizId);
    } catch (e: any) {
      error = e.message;
    }
  }
</script>

<svelte:head>
  <title>{$translate('dashboard.title')} — QuizTime</title>
</svelte:head>

<div class="page-enter">
  <div class="flex items-end justify-between">
    <div>
      <p class="eyebrow">{$translate('dashboard.overview')}</p>
      <h1 class="text-3xl font-bold tracking-[-0.03em]">{$translate('dashboard.title')}</h1>
    </div>
    <a href="/create" class="btn-pill btn-pill-primary btn-pill-sm">{$translate('dashboard.newQuiz')}</a>
  </div>

  {#if error}
    <div class="mt-4 rounded-xl bg-[var(--color-error-500)]/12 px-4 py-3 text-sm text-[var(--color-error-500)]">
      {error}
    </div>
  {/if}

  {#if loading}
    <div class="flex justify-center py-20">
      <span class="text-sm opacity-40">{$translate('general.loading')}</span>
    </div>
  {:else}
    <!-- Stats -->
    <div class="stagger mt-6 grid gap-4 sm:grid-cols-3">
      <div class="stat-pill">
        <span class="eyebrow">{$translate('dashboard.myQuizzesStat')}</span>
        <span class="text-3xl font-bold text-[var(--color-primary-500)]">{quizzes.length}</span>
      </div>
      <div class="stat-pill">
        <span class="eyebrow">{$translate('dashboard.attemptsStat')}</span>
        <span class="text-3xl font-bold text-[var(--color-secondary-500)]">{attempts.length}</span>
      </div>
      <div class="stat-pill">
        <span class="eyebrow">{$translate('dashboard.avgScoreStat')}</span>
        <span class="text-3xl font-bold text-[var(--color-tertiary-500)]">
          {attempts.length > 0
            ? Math.round(attempts.reduce((sum, a) => sum + (a.total > 0 ? (a.score / a.total) * 100 : 0), 0) / attempts.length)
            : 0}%
        </span>
      </div>
    </div>

    <!-- Gamification Profile Card -->
    {#if profile}
      <section class="mt-8">
        <a href="/achievements" class="frame flex items-center gap-4 p-4 hover:ring-1 hover:ring-[var(--color-primary-500)]/30 transition-all">
          <div class="flex h-14 w-14 items-center justify-center rounded-xl bg-[var(--color-surface-200-800)]">
            <span class="text-2xl font-bold text-[var(--color-primary-500)]">{profile.level}</span>
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-baseline gap-3">
              <span class="font-semibold">{profile.xp} {$translate('achievements.xp')}</span>
              <span class="text-xs opacity-40">{$translate('dashboard.level')} {profile.level}</span>
              {#if profile.streak_count}
                <span class="text-xs text-[var(--color-warning-500)]">{profile.streak_count}🔥 {$translate('dashboard.streak')}</span>
              {/if}
            </div>
            <div class="mt-1 h-2 w-full max-w-xs overflow-hidden rounded-full bg-[var(--color-surface-200-800)]">
              <div
                class="h-full rounded-full bg-gradient-to-r from-[var(--color-primary-500)] to-[var(--color-secondary-500)] transition-all"
                style="width: {profile.xp % 100}%"
              ></div>
            </div>
          </div>
          {#if badges.length > 0}
            <div class="hidden sm:flex items-center gap-1">
              {#each badges.slice(0, 3) as badge}
                <span class="text-lg" title={badge.name}>{badge.icon}</span>
              {/each}
              {#if badges.length > 3}
                <span class="text-xs opacity-40">+{badges.length - 3}</span>
              {/if}
            </div>
          {/if}
          <span class="text-sm opacity-40">{$translate('dashboard.viewProfile')} →</span>
        </a>
      </section>
    {/if}

    <!-- My Quizzes -->
    <section class="mt-10">
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-bold tracking-[-0.02em]">{$translate('dashboard.myQuizzes')}</h2>
        <a href="/create" class="btn-pill btn-pill-primary btn-pill-sm">{$translate('dashboard.newQuiz')}</a>
      </div>
      {#if quizzes.length === 0}
        <div class="mt-4 frame py-12 text-center">
          <p class="opacity-40">{$translate('dashboard.noQuizzes')}</p>
          <a href="/create" class="btn-pill btn-pill-primary btn-pill-sm mt-3">{$translate('dashboard.createFirstQuiz')}</a>
        </div>
      {:else}
        <div class="mt-4 frame overflow-hidden">
          <table class="table-frame">
            <thead>
              <tr>
                <th>{$translate('quiz.title')}</th>
                <th class="text-center">{$translate('quiz.questions')}</th>
                <th class="hidden sm:table-cell text-center">{$translate('admin.created')}</th>
                <th class="text-right">{$translate('admin.actions')}</th>
              </tr>
            </thead>
            <tbody>
              {#each quizzes as quiz}
                <tr>
                  <td>
                    <a href="/quizzes/{quiz.id}" class="font-medium text-[var(--color-primary-500)] hover:underline">{quiz.title}</a>
                  </td>
                  <td class="text-center text-sm opacity-60">{quiz.question_count}</td>
                  <td class="hidden sm:table-cell text-center text-sm opacity-40">{new Date(quiz.created_at).toLocaleDateString()}</td>
                  <td class="text-right">
                    <div class="flex justify-end gap-1">
                      <a href="/quizzes/{quiz.id}/edit" class="btn-pill btn-pill-ghost btn-pill-sm">{$translate('general.edit')}</a>
                      <button
                        class="btn-pill btn-pill-sm text-[var(--color-error-500)] hover:bg-[var(--color-error-500)]/10"
                        onclick={() => deleteQuiz(quiz.id)}
                      >
                        {$translate('general.delete')}
                      </button>
                    </div>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    </section>

    <!-- Recent Attempts -->
    <section class="mt-10">
      <h2 class="text-xl font-bold tracking-[-0.02em]">{$translate('dashboard.recentAttempts')}</h2>
      {#if attempts.length === 0}
        <div class="mt-4 frame py-12 text-center">
          <p class="opacity-40">{$translate('dashboard.noAttempts')}</p>
          <a href="/quizzes" class="btn-pill btn-pill-primary btn-pill-sm mt-3">{$translate('dashboard.takeQuiz')}</a>
        </div>
      {:else}
        <div class="mt-4 frame overflow-hidden">
          <table class="table-frame">
            <thead>
              <tr>
                <th>{$translate('quiz.title')}</th>
                <th class="text-center">{$translate('dashboard.score')}</th>
                <th class="text-center">{$translate('dashboard.percentage')}</th>
                <th class="hidden sm:table-cell text-center">{$translate('dashboard.date')}</th>
              </tr>
            </thead>
            <tbody>
              {#each attempts.slice(0, 10) as attempt}
                <tr>
                  <td>
                    <a href="/quizzes/{attempt.quiz_id}" class="text-[var(--color-primary-500)] hover:underline">{$translate('dashboard.viewQuiz')}</a>
                  </td>
                  <td class="text-center text-sm font-medium">{attempt.score}/{attempt.total}</td>
                  <td class="text-center text-sm font-medium">
                    <span class="rounded-full px-2 py-0.5 text-xs
                      {attempt.total > 0 && (attempt.score / attempt.total) >= 0.6
                        ? 'bg-[var(--color-success-500)]/15 text-[var(--color-success-500)]'
                        : 'bg-[var(--color-error-500)]/15 text-[var(--color-error-500)]'}">
                      {attempt.total > 0 ? Math.round((attempt.score / attempt.total) * 100) : 0}%
                    </span>
                  </td>
                  <td class="hidden sm:table-cell text-center text-sm opacity-40">{new Date(attempt.created_at).toLocaleDateString()}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    </section>
  {/if}
</div>
