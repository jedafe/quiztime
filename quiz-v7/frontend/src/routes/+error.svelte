<script lang="ts">
  import { page } from '$app/stores';
</script>

<div class="flex flex-col items-center justify-center py-16">
  <h1 class="text-6xl font-bold text-error mb-4">{$page.status}</h1>
  <p class="text-xl text-base-content/70 mb-6">
    {$page.error?.message || 'Something went wrong'}
  </p>
  <div class="flex gap-3">
    <a href="/" class="btn btn-primary">Go Home</a>
    <a href="/quizzes" class="btn btn-outline">Browse Quizzes</a>
  </div>
</div>
