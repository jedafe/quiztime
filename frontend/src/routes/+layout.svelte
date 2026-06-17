<script lang="ts">
  import { onMount } from 'svelte';
  import { auth, isLoggedIn, currentUser, isAdmin } from '$lib/stores/auth';
  import { theme } from '$lib/stores/theme';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import '../app.css';

  onMount(() => {
    theme.init();
  });

  function logout() {
    auth.logout();
    goto('/');
  }

  function cycleTheme() {
    theme.toggle();
  }

  $: themeIcon = $theme === 'dark' ? '🌙' : $theme === 'light' ? '☀️' : '🌟';
  $: themeLabel = $theme === 'dark' ? 'Dark' : $theme === 'light' ? 'Light' : 'Night';
</script>

<div class="min-h-screen bg-base-200">
  <nav class="navbar bg-base-100 shadow-lg">
    <div class="flex-1">
      <a href="/" class="btn btn-ghost text-xl normal-case">QuizTime</a>
    </div>
    <div class="flex-none gap-2">
      <a href="/quizzes" class="btn btn-ghost btn-sm">Browse</a>
      <a href="/docs" class="btn btn-ghost btn-sm">Docs</a>

      <!-- Theme Toggle -->
      <button
        class="btn btn-ghost btn-sm gap-1"
        on:click={cycleTheme}
        title="Switch theme (current: {themeLabel})"
      >
        <span class="text-lg">{themeIcon}</span>
        <span class="hidden sm:inline">{themeLabel}</span>
      </button>

      {#if $isLoggedIn}
        <a href="/dashboard" class="btn btn-ghost btn-sm">Dashboard</a>
        <a href="/create" class="btn btn-primary btn-sm">Create Quiz</a>
        <div class="dropdown dropdown-end">
          <button tabindex="0" class="btn btn-ghost btn-circle avatar">
            <div class="w-10 rounded-full bg-primary text-primary-content flex items-center justify-center">
              {$currentUser?.username?.[0]?.toUpperCase() || '?'}
            </div>
          </button>
          <ul class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
            <li class="menu-title"><span>{$currentUser?.username}</span></li>
            <li><span class="text-xs opacity-60">{$currentUser?.role}</span></li>
            <li><button on:click={logout}>Logout</button></li>
          </ul>
        </div>
      {:else}
        <a href="/login" class="btn btn-ghost btn-sm">Login</a>
        <a href="/register" class="btn btn-primary btn-sm">Register</a>
      {/if}
    </div>
  </nav>

  <main class="container mx-auto px-4 py-8 max-w-5xl">
    <slot />
  </main>
</div>
