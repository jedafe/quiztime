<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import { isLoggedIn } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import { translate } from '$lib/stores/i18n';

  let title = $state('');
  let description = $state('');
  let categoryId = $state('');
  let language = $state('en');
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
        language,
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
      importSuccess = $translate('create.importSuccess', {title: quiz.title, count: quiz.question_count});
      importFile = null;
      setTimeout(() => goto(`/quizzes/${quiz.id}/edit`), 1500);
    } catch (e: any) {
      importError = e.message || 'Failed to import quiz';
    }
    importLoading = false;
  }
</script>

<svelte:head>
  <title>{$translate('create.title')} — QuizTime</title>
</svelte:head>

<div class="page-enter mx-auto max-w-xl">
  <p class="eyebrow">{$translate('create.eyebrow')}</p>
  <h1 class="text-3xl font-bold tracking-[-0.03em]">{$translate('create.title')}</h1>
  <p class="mt-1 text-sm opacity-50">{$translate('create.subtitle')}</p>

  <!-- Tab bar -->
  <div class="mt-6 flex gap-1 border-b border-[var(--color-surface-300-700)] pb-2">
    <button
      class="btn-pill btn-pill-ghost btn-pill-sm"
      style={importTab === 'create' ? 'background-color:var(--color-primary-500);color:#fff' : ''}
      onclick={() => importTab = 'create'}
    >{$translate('create.createTab')}</button>
    <button
      class="btn-pill btn-pill-ghost btn-pill-sm"
      style={importTab === 'import' ? 'background-color:var(--color-primary-500);color:#fff' : ''}
      onclick={() => importTab = 'import'}
    >{$translate('create.importTab')}</button>
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
          <label class="mb-1.5 block text-sm font-medium">{$translate('create.titleLabel')}</label>
          <input type="text" bind:value={title} class="input-pill" placeholder={$translate('create.titlePlaceholder')} required />
        </div>

        <div>
          <label class="mb-1.5 block text-sm font-medium">{$translate('create.categoryLabel')}</label>
          <select bind:value={categoryId} class="input-pill">
            <option value="">{$translate('create.none')}</option>
            {#each categories as cat}
              <option value={cat.id}>{cat.name}</option>
            {/each}
          </select>
        </div>

        <div>
          <label class="mb-1.5 block text-sm font-medium">{$translate('create.languageLabel')}</label>
          <select bind:value={language} class="input-pill">
            <option value="en">English</option>
            <option value="es">Español</option>
            <option value="fr">Français</option>
          </select>
        </div>

        <div>
          <label class="mb-1.5 block text-sm font-medium">{$translate('create.descriptionLabel')}</label>
          <textarea bind:value={description} class="input-pill h-24 resize-none" placeholder={$translate('create.descriptionPlaceholder')}></textarea>
        </div>

        <div class="flex justify-end gap-2 pt-2">
          <a href="/dashboard" class="btn-pill btn-pill-ghost">{$translate('general.cancel')}</a>
          <button type="submit" class="btn-pill btn-pill-primary" disabled={loading}>
            {loading ? $translate('create.creating') : $translate('create.createButton')}
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
          <label class="mb-1.5 block text-sm font-medium">{$translate('create.jsonFile')}</label>
          <input
            type="file"
            accept=".json,application/json"
            onchange={(e) => { const el = e.currentTarget as HTMLInputElement; importFile = el.files?.[0] || null; }}
            class="block w-full text-sm file:mr-3 file:rounded-lg file:border-0 file:bg-[var(--color-primary-500)] file:px-3 file:py-2 file:text-sm file:font-medium file:text-white hover:file:brightness-110"
          />
          <p class="mt-1 text-xs opacity-50">
            {$translate('create.jsonDescription')}
          </p>
        </div>

        <div class="rounded-xl bg-[var(--color-surface-100-900)] p-4">
          <p class="mb-2 text-xs font-semibold uppercase tracking-wider opacity-50">{$translate('create.expectedFormat')}</p>
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
            {importLoading ? $translate('create.importing') : $translate('create.importButton')}
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>
