<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import { isLoggedIn } from '$lib/stores/auth';
  import { goto } from '$app/navigation';

  let title = '';
  let description = '';
  let categories: any[] = [];
  let error = '';
  let loading = false;

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
      const quiz = await api.createQuiz({ title, description });
      goto(`/quizzes/${quiz.id}/edit`);
    } catch (e: any) {
      error = e.message || 'Failed to create quiz';
    } finally {
      loading = false;
    }
  }
</script>

<div class="max-w-2xl mx-auto">
  <h1 class="text-3xl font-bold mb-6">Create New Quiz</h1>

  {#if error}
    <div class="alert alert-error mb-4">
      <span>{error}</span>
    </div>
  {/if}

  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <form on:submit|preventDefault={handleCreate}>
        <div class="form-control mb-4">
          <label class="label"><span class="label-text">Quiz Title *</span></label>
          <input
            type="text"
            bind:value={title}
            class="input input-bordered w-full"
            placeholder="e.g. JavaScript Fundamentals"
            required
          />
        </div>

        <div class="form-control mb-6">
          <label class="label"><span class="label-text">Description</span></label>
          <textarea
            bind:value={description}
            class="textarea textarea-bordered w-full h-24"
            placeholder="A brief description of this quiz..."
          ></textarea>
        </div>

        <div class="card-actions justify-end">
          <a href="/dashboard" class="btn btn-ghost">Cancel</a>
          <button type="submit" class="btn btn-primary" disabled={loading}>
            {loading ? 'Creating...' : 'Create Quiz'}
          </button>
        </div>
      </form>
    </div>
  </div>
</div>
