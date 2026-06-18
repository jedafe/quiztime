<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import { isLoggedIn, currentUser } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();
  let quiz = $state(data.quiz);

  interface ManagedQuestion {
    id: string;
    type: string;
    text: string;
    options: string[];
    answer: number[];
    category_id?: string;
  }

  let title = $state(quiz.title);
  let description = $state(quiz.description || '');
  let categories: any[] = $state([]);
  let questions: ManagedQuestion[] = $state([]);
  let loading = $state(true);
  let saving = $state(false);
  let error = $state('');
  let toast = $state('');

  let showDeleteModal = $state(false);
  let questionToDelete: string | null = $state(null);

  let newQuestion = $state({
    text: '',
    type: 'single',
    category_id: '',
    options: ['', '', '', ''],
    answer: [] as number[],
  });

  onMount(async () => {
    if (!$isLoggedIn) {
      goto('/login');
      return;
    }
    if (quiz.created_by !== $currentUser?.id && $currentUser?.role !== 'admin') {
      goto('/quizzes');
      return;
    }

    try {
      const [managedQuiz, cats] = await Promise.all([
        api.getQuizManage(quiz.id),
        api.listCategories(),
      ]);
      quiz = managedQuiz;
      title = quiz.title;
      description = quiz.description || '';
      questions = quiz.questions || [];
      categories = cats;
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  });

  async function saveQuiz() {
    saving = true;
    error = '';
    try {
      await api.updateQuiz(quiz.id, { title, description });
      toast = 'Quiz saved!';
      setTimeout(() => (toast = ''), 3000);
    } catch (e: any) {
      error = e.message;
    } finally {
      saving = false;
    }
  }

  async function addQuestion() {
    if (!newQuestion.text.trim()) {
      error = 'Question text is required';
      return;
    }

    const validOptions = newQuestion.options.filter((o) => o.trim());
    if (validOptions.length < 2) {
      error = 'At least 2 options are required';
      return;
    }

    if (newQuestion.answer.length === 0) {
      error = 'Select at least one correct answer';
      return;
    }

    saving = true;
    error = '';
    try {
      const q = await api.createQuestion(quiz.id, {
        text: newQuestion.text,
        type: newQuestion.type,
        category_id: newQuestion.category_id || null,
        options: validOptions,
        answer: newQuestion.answer.map((i) => Math.min(i, validOptions.length - 1)),
      });
      questions = [...questions, q];
      newQuestion = { text: '', type: 'single', category_id: '', options: ['', '', '', ''], answer: [] };
    } catch (e: any) {
      error = e.message;
    } finally {
      saving = false;
    }
  }

  function confirmDeleteQuestion(id: string) {
    questionToDelete = id;
    showDeleteModal = true;
  }

  async function deleteQuestion() {
    if (!questionToDelete) return;
    try {
      await api.deleteQuestion(questionToDelete);
      questions = questions.filter((q) => q.id !== questionToDelete);
    } catch (e: any) {
      error = e.message;
    } finally {
      showDeleteModal = false;
      questionToDelete = null;
    }
  }

  function updateOption(index: number, value: string) {
    newQuestion.options[index] = value;
  }

  function toggleAnswer(index: number) {
    if (newQuestion.type === 'multiple') {
      const idx = newQuestion.answer.indexOf(index);
      if (idx === -1) {
        newQuestion.answer = [...newQuestion.answer, index];
      } else {
        newQuestion.answer = newQuestion.answer.filter((i) => i !== index);
      }
    } else {
      newQuestion.answer = [index];
    }
  }

  function adjustOptions() {
    if (newQuestion.type === 'true-false') {
      newQuestion.options = ['True', 'False'];
      newQuestion.answer = newQuestion.answer.filter((i) => i < 2);
    } else {
      const len = 4;
      while (newQuestion.options.length < len) newQuestion.options.push('');
      newQuestion.options = newQuestion.options.slice(0, len);
      newQuestion.answer = newQuestion.answer.filter((i) => i < len);
    }
  }

  let prevType = $state(newQuestion.type);
  $effect(() => {
    if (newQuestion.type !== prevType) {
      adjustOptions();
      prevType = newQuestion.type;
    }
  });
</script>

<svelte:head>
  <title>Edit: {quiz.title} — QuizTime</title>
</svelte:head>

<div class="page-enter mx-auto max-w-3xl">
  <a href="/quizzes/{quiz.id}" class="mb-6 inline-flex items-center gap-1 text-sm font-medium opacity-50 transition-opacity hover:opacity-100">
    ← {quiz.title}
  </a>

  {#if loading}
    <div class="flex justify-center py-20">
      <span class="text-sm opacity-40">Loading...</span>
    </div>
  {:else}
    {#if error}
      <div class="mb-4 rounded-xl bg-[var(--color-error-500)]/12 px-4 py-3 text-sm text-[var(--color-error-500)]">
        {error}
      </div>
    {/if}

    <!-- Quiz Info -->
    <div class="frame p-6">
      <h2 class="mb-4 text-lg font-bold">Quiz Details</h2>
      <div class="space-y-4">
        <div>
          <label class="mb-1.5 block text-sm font-medium">Title</label>
          <input type="text" bind:value={title} class="input-pill" />
        </div>
        <div>
          <label class="mb-1.5 block text-sm font-medium">Description</label>
          <textarea bind:value={description} class="input-pill h-20 resize-none"></textarea>
        </div>
        <div class="flex justify-end">
          <button class="btn-pill btn-pill-primary" onclick={saveQuiz} disabled={saving}>
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>

    <!-- Existing Questions -->
    <div class="frame mt-6 p-6">
      <h2 class="mb-4 text-lg font-bold">Questions ({questions.length})</h2>
      {#if questions.length === 0}
        <p class="text-sm opacity-40">No questions yet. Add one below.</p>
      {:else}
        <div class="space-y-3">
          {#each questions as q}
            <div class="flex items-start justify-between rounded-xl border border-[var(--color-surface-300-700)] p-4 transition-colors hover:border-[var(--color-primary-500)]/30">
              <div class="flex-1">
                <span class="mb-1 inline-block rounded-full bg-[var(--color-surface-200-800)] px-2 py-0.5 text-xs font-medium">{q.type}</span>
                <p class="mt-1 font-medium">{q.text}</p>
                <p class="mt-1 text-sm opacity-50">
                  Options: {q.options.join(' → ')}
                </p>
                <p class="mt-1 text-sm text-[var(--color-success-500)]">
                  ✓ {q.answer.map((i) => q.options[i]).join(', ')}
                </p>
              </div>
              <button class="ml-4 shrink-0 rounded-lg px-3 py-1.5 text-xs font-medium text-[var(--color-error-500)] transition-colors hover:bg-[var(--color-error-500)]/10" onclick={() => confirmDeleteQuestion(q.id)}>
                Delete
              </button>
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Add Question Form -->
    <div class="frame mt-6 p-6">
      <h2 class="mb-4 text-lg font-bold">Add New Question</h2>

      <div class="space-y-4">
        <div>
          <label class="mb-1.5 block text-sm font-medium">Question Text *</label>
          <textarea
            bind:value={newQuestion.text}
            class="input-pill h-20 resize-none"
            placeholder="Enter your question..."
          ></textarea>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="mb-1.5 block text-sm font-medium">Type</label>
            <select bind:value={newQuestion.type} class="input-pill">
              <option value="single">Single Select</option>
              <option value="multiple">Multi Select</option>
              <option value="true-false">True/False</option>
            </select>
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-medium">Category</label>
            <select bind:value={newQuestion.category_id} class="input-pill">
              <option value="">None</option>
              {#each categories as cat}
                <option value={cat.id}>{cat.name}</option>
              {/each}
            </select>
          </div>
        </div>

        <!-- Options -->
        <div>
          <label class="mb-1.5 block text-sm font-medium">Options</label>
          <div class="space-y-2">
            {#each newQuestion.options as _, i}
              <div class="flex items-center gap-2">
                <input
                  type="text"
                  value={newQuestion.options[i]}
                  oninput={(e) => updateOption(i, (e.target as HTMLInputElement).value)}
                  class="input-pill flex-1"
                  placeholder="Option {String.fromCharCode(65 + i)}"
                  disabled={newQuestion.type === 'true-false'}
                />
                <button
                  class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl text-sm font-bold transition-all
                    {newQuestion.answer.includes(i)
                      ? 'bg-[var(--color-primary-500)] text-white'
                      : 'border border-[var(--color-surface-300-700)] hover:border-[var(--color-primary-500)]'}"
                  onclick={() => toggleAnswer(i)}
                >
                  {newQuestion.answer.includes(i) ? '✓' : String.fromCharCode(65 + i)}
                </button>
              </div>
            {/each}
          </div>
          <p class="mt-1.5 text-xs opacity-40">Click the letter buttons to mark correct answers</p>
        </div>

        <button
          class="btn-pill btn-pill-primary"
          onclick={addQuestion}
          disabled={saving}
        >
          {saving ? 'Adding...' : 'Add Question'}
        </button>
      </div>
    </div>
  {/if}
</div>

<!-- Toast -->
{#if toast}
  <div class="fixed bottom-4 right-4 z-50 animate-[pageEnter_0.3s_ease-out]">
    <div class="rounded-xl bg-[var(--color-success-500)] px-5 py-3 text-sm font-semibold text-white shadow-xl">
      {toast}
    </div>
  </div>
{/if}

<!-- Delete Confirmation Modal -->
{#if showDeleteModal}
  <dialog class="modal modal-open">
    <div class="modal-box rounded-2xl bg-[var(--color-surface-100-900)]">
      <h3 class="text-lg font-bold">Delete Question</h3>
      <p class="py-4 text-sm opacity-60">Are you sure you want to delete this question? This action cannot be undone.</p>
      <div class="modal-action gap-2">
        <button class="btn-pill btn-pill-ghost" onclick={() => { showDeleteModal = false; questionToDelete = null; }}>Cancel</button>
        <button class="btn-pill bg-[var(--color-error-500)] text-white hover:opacity-90" onclick={deleteQuestion}>Delete</button>
      </div>
    </div>
    <form method="dialog" class="modal-backdrop">
      <button onclick={() => { showDeleteModal = false; questionToDelete = null; }}>close</button>
    </form>
  </dialog>
{/if}
