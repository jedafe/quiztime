<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import { currentUser, isLoggedIn } from '$lib/stores/auth';
  import { goto } from '$app/navigation';

  let quizzes: any[] = $state([]);
  let attempts: any[] = $state([]);
  let loading = $state(true);
  let error = $state('');

  onMount(async () => {
    if (!$isLoggedIn) {
      goto('/login');
      return;
    }

    try {
      const [quizPage, a] = await Promise.all([api.listQuizzes(), api.myAttempts()]);
      const allQuizzes = quizPage.items ?? quizPage;
      quizzes = allQuizzes.filter((quiz: any) => quiz.created_by === $currentUser?.id || $currentUser?.role === 'admin');
      attempts = a;
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
  <title>Dashboard — QuizTime</title>
</svelte:head>

<div class="page-enter">
  <div class="flex items-end justify-between">
    <div>
      <p class="eyebrow">Overview</p>
      <h1 class="text-3xl font-bold tracking-[-0.03em]">Dashboard</h1>
    </div>
    <a href="/create" class="btn-pill btn-pill-primary btn-pill-sm">+ New Quiz</a>
  </div>

  {#if error}
    <div class="mt-4 rounded-xl bg-[var(--color-error-500)]/12 px-4 py-3 text-sm text-[var(--color-error-500)]">
      {error}
    </div>
  {/if}

  {#if loading}
    <div class="flex justify-center py-20">
      <span class="text-sm opacity-40">Loading...</span>
    </div>
  {:else}
    <!-- Stats -->
    <div class="stagger mt-6 grid gap-4 sm:grid-cols-3">
      <div class="stat-pill">
        <span class="eyebrow">My Quizzes</span>
        <span class="text-3xl font-bold text-[var(--color-primary-500)]">{quizzes.length}</span>
      </div>
      <div class="stat-pill">
        <span class="eyebrow">Attempts</span>
        <span class="text-3xl font-bold text-[var(--color-secondary-500)]">{attempts.length}</span>
      </div>
      <div class="stat-pill">
        <span class="eyebrow">Avg Score</span>
        <span class="text-3xl font-bold text-[var(--color-tertiary-500)]">
          {attempts.length > 0
            ? Math.round(attempts.reduce((sum, a) => sum + (a.total > 0 ? (a.score / a.total) * 100 : 0), 0) / attempts.length)
            : 0}%
        </span>
      </div>
    </div>

    <!-- My Quizzes -->
    <section class="mt-10">
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-bold tracking-[-0.02em]">My Quizzes</h2>
        <a href="/create" class="btn-pill btn-pill-primary btn-pill-sm">+ New Quiz</a>
      </div>
      {#if quizzes.length === 0}
        <div class="mt-4 frame py-12 text-center">
          <p class="opacity-40">You haven't created any quizzes yet.</p>
          <a href="/create" class="btn-pill btn-pill-primary btn-pill-sm mt-3">Create Your First Quiz</a>
        </div>
      {:else}
        <div class="mt-4 frame overflow-hidden">
          <table class="table-frame">
            <thead>
              <tr>
                <th>Title</th>
                <th class="text-center">Questions</th>
                <th class="hidden sm:table-cell text-center">Created</th>
                <th class="text-right">Actions</th>
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
                      <a href="/quizzes/{quiz.id}/edit" class="btn-pill btn-pill-ghost btn-pill-sm">Edit</a>
                      <button
                        class="btn-pill btn-pill-sm text-[var(--color-error-500)] hover:bg-[var(--color-error-500)]/10"
                        onclick={() => deleteQuiz(quiz.id)}
                      >
                        Delete
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
      <h2 class="text-xl font-bold tracking-[-0.02em]">Recent Attempts</h2>
      {#if attempts.length === 0}
        <div class="mt-4 frame py-12 text-center">
          <p class="opacity-40">No quiz attempts yet.</p>
          <a href="/quizzes" class="btn-pill btn-pill-primary btn-pill-sm mt-3">Take a Quiz</a>
        </div>
      {:else}
        <div class="mt-4 frame overflow-hidden">
          <table class="table-frame">
            <thead>
              <tr>
                <th>Quiz</th>
                <th class="text-center">Score</th>
                <th class="text-center">Percentage</th>
                <th class="hidden sm:table-cell text-center">Date</th>
              </tr>
            </thead>
            <tbody>
              {#each attempts.slice(0, 10) as attempt}
                <tr>
                  <td>
                    <a href="/quizzes/{attempt.quiz_id}" class="text-[var(--color-primary-500)] hover:underline">View Quiz</a>
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
