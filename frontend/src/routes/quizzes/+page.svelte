<script lang="ts">
  import { api } from '$lib/api';
  import { page } from '$app/stores';
  import { browser } from '$app/environment';
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();

  let quizzes = $state(data.quizzes);
  let total = $state(data.total);
  let totalPages = $state(data.totalPages);

  let search = $state('');
  let categoryId = $state('');
  let sortBy = $state('newest');
  let currentPage = $state(1);
  let categories = $state<{ id: string; name: string }[]>([]);
  let loading = $state(false);
  let debounceTimer: ReturnType<typeof setTimeout> | undefined;

  async function loadCategories() {
    try {
      categories = await api.listCategories();
    } catch {}
  }

  async function fetchQuizzes() {
    loading = true;
    try {
      const result = await api.listQuizzes({
        page: currentPage,
        pageSize: 20,
        search: search || undefined,
        category_id: categoryId || undefined,
        sort_by: sortBy,
      });
      quizzes = result.items;
      total = result.total;
      totalPages = result.total_pages;
    } catch {}
    loading = false;
  }

  function onSearchInput() {
    currentPage = 1;
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(fetchQuizzes, 300);
  }

  function onFilterChange() {
    currentPage = 1;
    fetchQuizzes();
  }

  function goPage(p: number) {
    if (p < 1 || p > totalPages) return;
    currentPage = p;
    fetchQuizzes();
  }

  function starDisplay(rating: number): string {
    const full = Math.floor(rating);
    const half = rating - full >= 0.5;
    return '★'.repeat(full) + (half ? '½' : '') + '☆'.repeat(5 - full - (half ? 1 : 0));
  }

  if (browser) {
    loadCategories();
  }
</script>

<svelte:head>
  <title>Browse Quizzes — QuizTime</title>
</svelte:head>

<div class="page-enter">
  <div class="flex items-end justify-between">
    <div>
      <p class="eyebrow">Explore</p>
      <h1 class="text-3xl font-bold tracking-[-0.03em]">Browse Quizzes</h1>
    </div>
    <a href="/create" class="btn-pill btn-pill-primary btn-pill-sm">+ New Quiz</a>
  </div>

  <div class="mt-4 flex flex-wrap items-center gap-3">
    <div class="relative min-w-0 flex-1 sm:max-w-xs">
      <svg class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-4.35-4.35M11 19a8 8 0 100-16 8 8 0 000 16z" /></svg>
      <input
        type="text"
        placeholder="Search quizzes..."
        bind:value={search}
        oninput={onSearchInput}
        class="w-full rounded-xl border border-[var(--color-surface-300-700)] bg-[var(--color-surface-50-950)] py-2 pl-10 pr-3 text-sm outline-none transition-colors focus:border-[var(--color-primary-500)]"
      />
    </div>
    <select
      bind:value={categoryId}
      onchange={onFilterChange}
      class="rounded-xl border border-[var(--color-surface-300-700)] bg-[var(--color-surface-50-950)] px-3 py-2 text-sm outline-none transition-colors focus:border-[var(--color-primary-500)]"
    >
      <option value="">All Categories</option>
      {#each categories as cat}
        <option value={cat.id}>{cat.name}</option>
      {/each}
    </select>
    <select
      bind:value={sortBy}
      onchange={onFilterChange}
      class="rounded-xl border border-[var(--color-surface-300-700)] bg-[var(--color-surface-50-950)] px-3 py-2 text-sm outline-none transition-colors focus:border-[var(--color-primary-500)]"
    >
      <option value="newest">Newest</option>
      <option value="popular">Most Popular</option>
      <option value="rating">Highest Rated</option>
    </select>
  </div>

  {#if loading}
    <div class="mt-16 text-center">
      <p class="text-sm opacity-40">Loading...</p>
    </div>
  {:else if quizzes.length === 0}
    <div class="mt-16 text-center">
      <p class="text-lg opacity-40">No quizzes found.</p>
    </div>
  {:else}
    <div class="stagger mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {#each quizzes as quiz}
        <a href="/quizzes/{quiz.id}" class="frame-lift block p-5">
          <h3 class="font-bold transition-colors group-hover:text-[var(--color-primary-500)]">{quiz.title}</h3>
          <p class="mt-1 line-clamp-2 text-sm opacity-50">{quiz.description || 'No description'}</p>
          <div class="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs">
            <span class="rounded-full bg-[var(--color-surface-200-800)] px-2.5 py-0.5 font-medium">{quiz.question_count} questions</span>
            {#if quiz.attempt_count > 0}
              <span class="opacity-50">{quiz.attempt_count} attempt{quiz.attempt_count !== 1 ? 's' : ''}</span>
            {/if}
            {#if quiz.avg_rating > 0}
              <span class="text-[var(--color-warning-500)]">{starDisplay(quiz.avg_rating)} {quiz.avg_rating}</span>
            {/if}
          </div>
        </a>
      {/each}
    </div>

    {#if totalPages > 1}
      <div class="mt-8 flex items-center justify-center gap-2">
        <button onclick={() => goPage(currentPage - 1)} disabled={currentPage <= 1} class="rounded-xl border border-[var(--color-surface-300-700)] px-3 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)] disabled:opacity-30">Prev</button>
        {#each Array.from({ length: totalPages }, (_, i) => i + 1) as p}
          {#if p === 1 || p === totalPages || (p >= currentPage - 1 && p <= currentPage + 1)}
            <button onclick={() => goPage(p)} class="rounded-xl border border-[var(--color-surface-300-700)] px-3 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)] {p === currentPage ? 'bg-[var(--color-primary-500)] text-white' : ''}">{p}</button>
          {:else if p === currentPage - 2 || p === currentPage + 2}
            <span class="px-1 text-sm opacity-30">...</span>
          {/if}
        {/each}
        <button onclick={() => goPage(currentPage + 1)} disabled={currentPage >= totalPages} class="rounded-xl border border-[var(--color-surface-300-700)] px-3 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)] disabled:opacity-30">Next</button>
      </div>
    {/if}
  {/if}
</div>
