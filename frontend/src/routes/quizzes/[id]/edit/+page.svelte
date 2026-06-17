<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import { isLoggedIn, currentUser } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import type { PageData } from './$types';

  export let data: PageData;
  let quiz = data.quiz;

  interface ManagedQuestion {
    id: string;
    type: string;
    text: string;
    options: string[];
    answer: number[];
    category_id?: string;
  }

  let title = quiz.title;
  let description = quiz.description || '';
  let categories: any[] = [];
  let questions: ManagedQuestion[] = [];
  let loading = true;
  let saving = false;
  let error = '';
  let toast = '';

  let showDeleteModal = false;
  let questionToDelete: string | null = null;

  // New question form
  let newQuestion = {
    text: '',
    type: 'single',
    category_id: '',
    options: ['', '', '', ''],
    answer: [] as number[],
  };

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

  $: prevType = newQuestion.type;
  $: if (newQuestion.type !== prevType) {
    adjustOptions();
  }
</script>

<div class="mb-6">
  <a href="/quizzes/{quiz.id}" class="btn btn-ghost btn-sm">← {quiz.title}</a>
</div>

{#if loading}
  <div class="flex justify-center py-16">
    <span class="loading loading-spinner loading-lg"></span>
  </div>
{:else}
  {#if error}
    <div class="alert alert-error mb-4">
      <span>{error}</span>
    </div>
  {/if}

  <!-- Quiz Info -->
  <div class="card bg-base-100 shadow-xl mb-6">
    <div class="card-body">
      <h2 class="card-title">Quiz Details</h2>
      <div class="form-control mb-3">
        <label class="label"><span class="label-text">Title</span></label>
        <input type="text" bind:value={title} class="input input-bordered w-full" />
      </div>
      <div class="form-control mb-3">
        <label class="label"><span class="label-text">Description</span></label>
        <textarea bind:value={description} class="textarea textarea-bordered w-full h-20"></textarea>
      </div>
      <button class="btn btn-primary btn-sm self-end" on:click={saveQuiz} disabled={saving}>
        {saving ? 'Saving...' : 'Save Changes'}
      </button>
    </div>
  </div>

  <!-- Existing Questions -->
  <div class="card bg-base-100 shadow-xl mb-6">
    <div class="card-body">
      <h2 class="card-title">Questions ({questions.length})</h2>
      {#if questions.length === 0}
        <p class="text-base-content/60">No questions yet. Add one below.</p>
      {:else}
        <div class="space-y-3">
          {#each questions as q}
            <div class="border rounded-lg p-4 flex justify-between items-start">
              <div>
                <span class="badge badge-sm">{q.type}</span>
                <p class="font-medium mt-1">{q.text}</p>
                <p class="text-sm text-base-content/60 mt-1">
                  Options: {q.options.join(' | ')}
                </p>
                <p class="text-sm text-success">
                  Correct: {q.answer.map((i) => q.options[i]).join(', ')}
                </p>
              </div>
              <button class="btn btn-ghost btn-sm text-error" on:click={() => confirmDeleteQuestion(q.id)}>
                Delete
              </button>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </div>

  <!-- Add Question Form -->
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title">Add New Question</h2>

      <div class="form-control mb-3">
        <label class="label"><span class="label-text">Question Text *</span></label>
        <textarea
          bind:value={newQuestion.text}
          class="textarea textarea-bordered w-full h-20"
          placeholder="Enter your question..."
        ></textarea>
      </div>

      <div class="grid grid-cols-2 gap-4 mb-3">
        <div class="form-control">
          <label class="label"><span class="label-text">Type</span></label>
          <select bind:value={newQuestion.type} class="select select-bordered w-full">
            <option value="single">Single Select</option>
            <option value="multiple">Multi Select</option>
            <option value="true-false">True/False</option>
          </select>
        </div>

        <div class="form-control">
          <label class="label"><span class="label-text">Category</span></label>
          <select bind:value={newQuestion.category_id} class="select select-bordered w-full">
            <option value="">None</option>
            {#each categories as cat}
              <option value={cat.id}>{cat.name}</option>
            {/each}
          </select>
        </div>
      </div>

      <!-- Options -->
      <div class="mb-3">
        <label class="label"><span class="label-text">Options</span></label>
        <div class="space-y-2">
          {#each newQuestion.options as _, i}
            <div class="flex gap-2 items-center">
              <input
                type="text"
                value={newQuestion.options[i]}
                on:input={(e) => updateOption(i, e.currentTarget.value)}
                class="input input-bordered flex-1"
                placeholder="Option {String.fromCharCode(65 + i)}"
                disabled={newQuestion.type === 'true-false'}
              />
              <button
                class="btn btn-sm"
                class:btn-primary={newQuestion.answer.includes(i)}
                class:btn-outline={!newQuestion.answer.includes(i)}
                on:click={() => toggleAnswer(i)}
              >
                {newQuestion.answer.includes(i) ? '✓' : String.fromCharCode(65 + i)}
              </button>
            </div>
          {/each}
        </div>
        <p class="text-xs text-base-content/60 mt-1">Click the letter buttons to mark correct answers</p>
      </div>

      <button class="btn btn-primary" on:click={addQuestion} disabled={saving}>
        {saving ? 'Adding...' : 'Add Question'}
      </button>
    </div>
  </div>
{/if}

{#if toast}
  <div class="toast toast-end">
    <div class="alert alert-success">
      <span>{toast}</span>
    </div>
  </div>
{/if}

<!-- Delete Confirmation Modal -->
<dialog class="modal" class:modal-open={showDeleteModal}>
  <div class="modal-box">
    <h3 class="font-bold text-lg">Delete Question</h3>
    <p class="py-4">Are you sure you want to delete this question?</p>
    <div class="modal-action">
      <button class="btn btn-ghost" on:click={() => { showDeleteModal = false; questionToDelete = null; }}>Cancel</button>
      <button class="btn btn-error" on:click={deleteQuestion}>Delete</button>
    </div>
  </div>
  <form method="dialog" class="modal-backdrop">
    <button on:click={() => { showDeleteModal = false; questionToDelete = null; }}>close</button>
  </form>
</dialog>
