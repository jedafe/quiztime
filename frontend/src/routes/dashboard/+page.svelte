<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import { currentUser, isLoggedIn } from '$lib/stores/auth';
  import { goto } from '$app/navigation';

  let quizzes: any[] = [];
  let attempts: any[] = [];
  let loading = true;
  let error = '';

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

<h1 class="text-3xl font-bold mb-6">Dashboard</h1>

{#if error}
  <div class="alert alert-error mb-4">
    <span>{error}</span>
  </div>
{/if}

{#if loading}
  <div class="flex justify-center py-16">
    <span class="loading loading-spinner loading-lg"></span>
  </div>
{:else}
  <!-- Stats -->
  <div class="grid gap-4 md:grid-cols-3 mb-8">
    <div class="stat bg-base-100 rounded-box shadow">
      <div class="stat-title">My Quizzes</div>
      <div class="stat-value text-primary">{quizzes.length}</div>
    </div>
    <div class="stat bg-base-100 rounded-box shadow">
      <div class="stat-title">Attempts</div>
      <div class="stat-value text-secondary">{attempts.length}</div>
    </div>
    <div class="stat bg-base-100 rounded-box shadow">
      <div class="stat-title">Avg Score</div>
      <div class="stat-value text-accent">
        {attempts.length > 0
          ? Math.round(attempts.reduce((sum, a) => sum + (a.total > 0 ? (a.score / a.total) * 100 : 0), 0) / attempts.length)
          : 0}%
      </div>
    </div>
  </div>

  <!-- My Quizzes -->
  <h2 class="text-2xl font-bold mb-4">My Quizzes</h2>
  {#if quizzes.length === 0}
    <div class="text-center py-8 bg-base-100 rounded-box">
      <p class="text-base-content/60">You haven't created any quizzes yet.</p>
      <a href="/create" class="btn btn-primary mt-4">Create Your First Quiz</a>
    </div>
  {:else}
    <div class="overflow-x-auto">
      <table class="table">
        <thead>
          <tr>
            <th>Title</th>
            <th>Questions</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each quizzes as quiz}
            <tr>
              <td>
                <a href="/quizzes/{quiz.id}" class="link link-primary">{quiz.title}</a>
              </td>
              <td>{quiz.question_count}</td>
              <td>{new Date(quiz.created_at).toLocaleDateString()}</td>
              <td>
                <div class="flex gap-2">
                  <a href="/quizzes/{quiz.id}/edit" class="btn btn-ghost btn-xs">Edit</a>
                  <button
                    class="btn btn-ghost btn-xs text-error"
                    on:click={() => deleteQuiz(quiz.id)}
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

  <!-- Recent Attempts -->
  <h2 class="text-2xl font-bold mb-4 mt-8">Recent Attempts</h2>
  {#if attempts.length === 0}
    <div class="text-center py-8 bg-base-100 rounded-box">
      <p class="text-base-content/60">No quiz attempts yet.</p>
      <a href="/quizzes" class="btn btn-primary mt-4">Take a Quiz</a>
    </div>
  {:else}
    <div class="overflow-x-auto">
      <table class="table">
        <thead>
          <tr>
            <th>Quiz</th>
            <th>Score</th>
            <th>Percentage</th>
            <th>Date</th>
          </tr>
        </thead>
        <tbody>
          {#each attempts.slice(0, 10) as attempt}
            <tr>
              <td>
                <a href="/quizzes/{attempt.quiz_id}" class="link link-primary">View Quiz</a>
              </td>
              <td>{attempt.score}/{attempt.total}</td>
              <td>{attempt.total > 0 ? Math.round((attempt.score / attempt.total) * 100) : 0}%</td>
              <td>{new Date(attempt.created_at).toLocaleDateString()}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
{/if}
