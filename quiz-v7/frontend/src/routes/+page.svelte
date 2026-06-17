<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import { isLoggedIn } from '$lib/stores/auth';
  import type { PageData } from './$types';

  export let data: PageData;
</script>

<div class="hero py-16">
  <div class="hero-content text-center">
    <div class="max-w-2xl">
      <h1 class="text-5xl font-bold">QuizTime</h1>
      <p class="py-6 text-lg text-base-content/70">
        Test your knowledge with quizzes created by the community.
        Create, share, and compete!
      </p>
      <div class="flex gap-4 justify-center">
        <a href="/quizzes" class="btn btn-primary btn-lg">Browse Quizzes</a>
        {#if $isLoggedIn}
          <a href="/dashboard" class="btn btn-outline btn-lg">Dashboard</a>
        {:else}
          <a href="/register" class="btn btn-outline btn-lg">Get Started</a>
        {/if}
      </div>
    </div>
  </div>
</div>

{#if data.featured?.length > 0}
  <div class="mt-8">
    <h2 class="text-2xl font-bold mb-4">Featured Quizzes</h2>
    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {#each data.featured as quiz}
        <a href="/quizzes/{quiz.id}" class="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow">
          <div class="card-body">
            <h3 class="card-title">{quiz.title}</h3>
            <p class="text-base-content/60 text-sm">{quiz.question_count} questions</p>
            <div class="card-actions justify-end mt-2">
              <span class="btn btn-primary btn-sm">Take Quiz</span>
            </div>
          </div>
        </a>
      {/each}
    </div>
  </div>
{/if}
