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

  // ── Import ──
  let importTab = $state<'create' | 'import'>('create');
  let importFile = $state<File | null>(null);
  let importLoading = $state(false);
  let importError = $state('');
  let importSuccess = $state('');

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

  async function handleImport() {
    importError = '';
    importSuccess = '';
    if (!importFile) {
      importError = 'Please select a JSON file';
      return;
    }
    importLoading = true;
    try {
      const text = await importFile.text();
      const data = JSON.parse(text);
      if (!data.title || !data.questions || !Array.isArray(data.questions)) {
        throw new Error('Invalid quiz JSON: missing "title" or "questions" array');
      }
      const quiz = await api.importQuiz({
        title: data.title,
        description: data.description || '',
        category_name: data.category_name || null,
        questions: data.questions,
      });
      importSuccess = `Imported "${quiz.title}" with ${quiz.question_count} questions!`;
      importFile = null;
      setTimeout(() => goto(`/quizzes/${quiz.id}/edit`), 1500);
    } catch (e: any) {
      importError = e.message || 'Failed to import quiz';
    }
    importLoading = false;
  }
</script>

<svelte:head>
  <title>Create Quiz — QuizTime</title>
</svelte:head>

<div class="page-enter mx-auto max-w-xl">
  <p class="eyebrow">Creation</p>
  <h1 class="text-3xl font-bold tracking-[-0.03em]">Create New Quiz</h1>
  <p class="mt-1 text-sm opacity-50">Give it a title, category, and optional description</p>

  <!-- Tab bar -->
  <div class="mt-6 flex gap-1 border-b border-[var(--color-surface-300-700)] pb-2">
    <button
      class="btn-pill btn-pill-ghost btn-pill-sm"
      style={importTab === 'create' ? 'background-color:var(--color-primary-500);color:#fff' : ''}
      onclick={() => importTab = 'create'}
    >Create</button>
    <button
      class="btn-pill btn-pill-ghost btn-pill-sm"
      style={importTab === 'import' ? 'background-color:var(--color-primary-500);color:#fff' : ''}
      onclick={() => importTab = 'import'}
    >Import JSON</button>
  </div>

  {#if importTab === 'create'}
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
  {:else}
    {#if importError}
      <div class="mt-4 rounded-xl bg-[var(--color-error-500)]/12 px-4 py-3 text-sm text-[var(--color-error-500)]">
        {importError}
      </div>
    {/if}
    {#if importSuccess}
      <div class="mt-4 rounded-xl bg-[var(--color-success-500)]/12 px-4 py-3 text-sm text-[var(--color-success-500)]">
        {importSuccess}
      </div>
    {/if}

    <div class="frame mt-6 p-6">
      <div class="space-y-5">
        <div>
          <label class="mb-1.5 block text-sm font-medium">Quiz JSON File</label>
          <input
            type="file"
            accept=".json,application/json"
            onchange={(e) => { const el = e.currentTarget as HTMLInputElement; importFile = el.files?.[0] || null; }}
            class="block w-full text-sm file:mr-3 file:rounded-lg file:border-0 file:bg-[var(--color-primary-500)] file:px-3 file:py-2 file:text-sm file:font-medium file:text-white hover:file:brightness-110"
          />
          <p class="mt-1 text-xs opacity-50">
            Upload a quiz JSON file exported from QuizTime or matching the export format.
          </p>
        </div>

        <div class="rounded-xl bg-[var(--color-surface-100-900)] p-4">
          <p class="mb-2 text-xs font-semibold uppercase tracking-wider opacity-50">Expected Format</p>
          <pre class="text-xs leading-relaxed opacity-70">{`{
  "title": "My Quiz",
  "description": "...",
  "category_name": "Science",
  "questions": [
    {
      "type": "single",
      "text": "Question text",
      "options": ["A", "B", "C"],
      "answer": [0]
    }
  ]
}`}</pre>
        </div>

        <div class="flex justify-end gap-2 pt-2">
          <button
            onclick={handleImport}
            class="btn-pill btn-pill-primary"
            disabled={importLoading}
          >
            {importLoading ? 'Importing...' : 'Import Quiz'}
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>
