<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import { isLoggedIn } from '$lib/stores/auth';
  import { goto } from '$app/navigation';

  let title = $state('');
  let description = $state('');
  let categoryId = $state('');
  let categories: any[] = $state([]);
  let error = $state('');
  let loading = $state(false);

  onMount(() => {
    if (!$isLoggedIn) {
      goto('/login');
      return;
    }
    loadCategories();
  });

  async function loadCategories() {
    try {
      categories = await api.listCategories();
    } catch (e) {
      // categories might fail
    }
  }

  async function handleCreate() {
    if (!title.trim()) {
      error = 'Title is required';
      return;
    }

    loading = true;
    error = '';
    try {
      const quiz = await api.createQuiz({
        title, description,
        category_id: categoryId || null,
      });
      goto(`/quizzes/${quiz.id}/edit`);
    } catch (e: any) {
      error = e.message || 'Failed to create quiz';
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>Create Quiz — QuizTime</title>
</svelte:head>

<div class="page-enter mx-auto max-w-xl">
  <p class="eyebrow">Creation</p>
  <h1 class="text-3xl font-bold tracking-[-0.03em]">Create New Quiz</h1>
  <p class="mt-1 text-sm opacity-50">Give it a title, category, and optional description</p>

  {#if error}
    <div class="mt-4 rounded-xl bg-[var(--color-error-500)]/12 px-4 py-3 text-sm text-[var(--color-error-500)]">
      {error}
    </div>
  {/if}

  <div class="frame mt-6 p-6">
    <form onsubmit={(e) => { e.preventDefault(); handleCreate(); }} class="space-y-5">
      <div>
        <label class="mb-1.5 block text-sm font-medium">Quiz Title *</label>
        <input type="text" bind:value={title} class="input-pill" placeholder="e.g. JavaScript Fundamentals" required />
      </div>

      <div>
        <label class="mb-1.5 block text-sm font-medium">Category</label>
        <select bind:value={categoryId} class="input-pill">
          <option value="">None</option>
          {#each categories as cat}
            <option value={cat.id}>{cat.name}</option>
          {/each}
        </select>
      </div>

      <div>
        <label class="mb-1.5 block text-sm font-medium">Description</label>
        <textarea bind:value={description} class="input-pill h-24 resize-none" placeholder="A brief description of this quiz..."></textarea>
      </div>

      <div class="flex justify-end gap-2 pt-2">
        <a href="/dashboard" class="btn-pill btn-pill-ghost">Cancel</a>
        <button type="submit" class="btn-pill btn-pill-primary" disabled={loading}>
          {loading ? 'Creating...' : 'Create Quiz'}
        </button>
      </div>
    </form>
  </div>
</div>
