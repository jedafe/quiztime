<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import type { PageData } from './$types';

  export let data: PageData;
</script>

<h1 class="text-3xl font-bold mb-6">Browse Quizzes</h1>

{#if data.quizzes?.length === 0}
  <div class="text-center py-16">
    <p class="text-lg text-base-content/60">No quizzes yet. Be the first to create one!</p>
    <a href="/create" class="btn btn-primary mt-4">Create Quiz</a>
  </div>
{:else}
  <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
    {#each data.quizzes as quiz}
      <a href="/quizzes/{quiz.id}" class="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow">
        <div class="card-body">
          <h3 class="card-title">{quiz.title}</h3>
          <p class="text-base-content/60 text-sm line-clamp-2">{quiz.description || 'No description'}</p>
          <div class="flex items-center gap-2 mt-2">
            <span class="badge badge-outline">{quiz.question_count} questions</span>
          </div>
          <div class="card-actions justify-end mt-2">
            <span class="btn btn-primary btn-sm">Take Quiz</span>
          </div>
        </div>
      </a>
    {/each}
  </div>
{/if}
