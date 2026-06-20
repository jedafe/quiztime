<script lang="ts">
  import { onMount } from 'svelte';
  import { auth, isLoggedIn, currentUser, isAdmin } from '$lib/stores/auth';
  import { locale, translate, locales, setHtmlLang } from '$lib/stores/i18n';
  import { theme } from '$lib/stores/theme';
  import { goto } from '$app/navigation';
  import '../app.css';

  let { children } = $props();

  onMount(() => {
    theme.init();
    setHtmlLang($locale);
  });

  $effect(() => {
    setHtmlLang($locale);
  });

  function logout() {
    auth.logout();
    goto('/');
    dropdownOpen = false;
  }

  function cycleTheme() {
    theme.toggle();
  }

  let isDark = $derived($theme === 'cerberus');
  let themeIcon = $derived(isDark ? '🌙' : '☀️');
  let themeLabel = $derived($translate(isDark ? 'nav.dark' : 'nav.light'));
  let themeTitle = $derived(isDark ? $translate('nav.switchToLight') : $translate('nav.switchToDark'));
  let dropdownOpen = $state(false);
  let langOpen = $state(false);

  function handleOutsideClick(e: MouseEvent) {
    const target = e.target as HTMLElement;
    if (!target.closest('.avatar-dropdown') && !target.closest('.lang-dropdown')) {
      dropdownOpen = false;
      langOpen = false;
    }
  }
</script>

<sveltewindow onclick={handleOutsideClick} />

<div class="page-enter flex min-h-screen flex-col bg-[var(--color-surface-50-950)]">
  <div class="bg-atmos fixed inset-0 z-0 pointer-events-none"></div>

  <nav class="sticky top-0 z-50 border-b border-[var(--color-surface-200-800)] bg-[var(--color-surface-100-900)]/80 backdrop-blur-xl">
    <div class="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
      <a href="/" class="flex items-center gap-2.5 text-xl font-bold tracking-tight transition-opacity hover:opacity-80">
        <span class="flex h-8 w-8 items-center justify-center rounded-xl bg-[var(--color-primary-500)] text-sm font-bold text-white">Q</span>
        <span>QuizTime</span>
      </a>

      <div class="hidden items-center gap-1 sm:flex">
        <a href="/quizzes" class="btn-pill btn-pill-ghost text-sm">{$translate('nav.browse')}</a>
        <a href="/docs" class="btn-pill btn-pill-ghost text-sm">{$translate('nav.docs')}</a>

        <button
          class="btn-pill btn-pill-ghost flex items-center gap-1.5 text-sm"
          onclick={cycleTheme}
          title={themeTitle}
        >
          <span class="text-base">{themeIcon}</span>
          <span class="hidden md:inline">{themeLabel}</span>
        </button>

        {#if $isLoggedIn}
          <a href="/dashboard" class="btn-pill btn-pill-ghost text-sm">{$translate('nav.dashboard')}</a>
          <a href="/achievements" class="btn-pill btn-pill-ghost text-sm">{$translate('nav.achievements')}</a>
          <a href="/create" class="btn-pill btn-pill-primary ml-1 text-sm">{$translate('nav.createQuiz')}</a>

          {#if $isAdmin}
            <a href="/admin" class="btn-pill btn-pill-ghost text-sm">{$translate('nav.admin')}</a>
          {/if}

          <div class="avatar-dropdown relative ml-2">
            <button
              class="flex h-9 w-9 items-center justify-center rounded-full bg-[var(--color-primary-500)]/20 text-sm font-bold text-[var(--color-primary-500)] ring-2 ring-transparent transition-all hover:ring-[var(--color-primary-500)]/30"
              onclick={() => dropdownOpen = !dropdownOpen}
            >
              {$currentUser?.username?.[0]?.toUpperCase() || '?'}
            </button>
            {#if dropdownOpen}
              <div class="absolute right-0 z-50 mt-2 w-56 overflow-hidden rounded-xl border border-[var(--color-surface-300-700)] bg-[var(--color-surface-100-900)] shadow-2xl">
                <div class="border-b border-[var(--color-surface-200-800)] px-4 py-3">
                  <div class="font-semibold">{$currentUser?.username}</div>
                  <div class="text-xs opacity-50">{$currentUser?.role}</div>
                </div>
                <button
                  class="w-full px-4 py-2.5 text-left text-sm transition-colors hover:bg-[var(--color-surface-200-800)]"
                  onclick={logout}
                >
                  {$translate('nav.signOut')}
                </button>
              </div>
            {/if}
          </div>
        {:else}
          <a href="/login" class="btn-pill btn-pill-ghost text-sm">{$translate('nav.login')}</a>
          <a href="/register" class="btn-pill btn-pill-primary ml-1 text-sm">{$translate('nav.register')}</a>
        {/if}

        <div class="lang-dropdown relative ml-1">
          <button
            class="btn-pill btn-pill-ghost flex items-center gap-1 text-sm"
            onclick={() => langOpen = !langOpen}
          >
            <span>{$locale === 'en' ? '🇬🇧' : $locale === 'es' ? '🇪🇸' : '🇫🇷'}</span>
            <span class="hidden lg:inline">{$locale.toUpperCase()}</span>
          </button>
          {#if langOpen}
            <div class="absolute right-0 z-50 mt-2 w-36 overflow-hidden rounded-xl border border-[var(--color-surface-300-700)] bg-[var(--color-surface-100-900)] shadow-2xl">
              {#each locales as l}
                <button
                  class="flex w-full items-center gap-2 px-4 py-2 text-sm transition-colors hover:bg-[var(--color-surface-200-800)] {$locale === l.code ? 'font-semibold' : ''}"
                  onclick={() => { locale.set(l.code); langOpen = false; }}
                >
                  <span>{l.code === 'en' ? '🇬🇧' : l.code === 'es' ? '🇪🇸' : '🇫🇷'}</span>
                  {l.native}
                </button>
              {/each}
            </div>
          {/if}
        </div>
      </div>

      <div class="flex items-center gap-1 sm:hidden">
        <button
          class="flex h-9 w-9 items-center justify-center rounded-lg text-lg transition-colors hover:bg-[var(--color-surface-200-800)]"
          onclick={cycleTheme}
          title={themeTitle}
        >
          {themeIcon}
        </button>
        {#if $isLoggedIn}
          <div class="avatar-dropdown relative">
            <button
              class="flex h-9 w-9 items-center justify-center rounded-full bg-[var(--color-primary-500)]/20 text-sm font-bold text-[var(--color-primary-500)]"
              onclick={() => dropdownOpen = !dropdownOpen}
            >
              {$currentUser?.username?.[0]?.toUpperCase() || '?'}
            </button>
            {#if dropdownOpen}
              <div class="absolute right-0 z-50 mt-2 w-56 overflow-hidden rounded-xl border border-[var(--color-surface-300-700)] bg-[var(--color-surface-100-900)] shadow-2xl">
                <div class="border-b border-[var(--color-surface-200-800)] px-4 py-3">
                  <div class="font-semibold">{$currentUser?.username}</div>
                  <div class="text-xs opacity-50">{$currentUser?.role}</div>
                </div>
                <a href="/dashboard" class="block px-4 py-2.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]" onclick={() => dropdownOpen = false}>{$translate('nav.dashboard')}</a>
                <a href="/achievements" class="block px-4 py-2.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]" onclick={() => dropdownOpen = false}>{$translate('nav.achievements')}</a>
                <a href="/create" class="block px-4 py-2.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]" onclick={() => dropdownOpen = false}>{$translate('nav.createQuiz')}</a>
                {#if $isAdmin}
                  <a href="/admin" class="block px-4 py-2.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]" onclick={() => dropdownOpen = false}>{$translate('nav.admin')}</a>
                {/if}
                <button
                  class="w-full border-t border-[var(--color-surface-200-800)] px-4 py-2.5 text-left text-sm transition-colors hover:bg-[var(--color-surface-200-800)]"
                  onclick={logout}
                >
                  {$translate('nav.signOut')}
                </button>
              </div>
            {/if}
          </div>
        {:else}
          <a href="/login" class="btn-pill btn-pill-ghost text-sm">{$translate('nav.login')}</a>
        {/if}
      </div>
    </div>
  </nav>

  <main class="relative z-10 mx-auto w-full max-w-6xl flex-1 px-4 py-8 sm:px-6">
    {@render children()}
  </main>

  <footer class="relative z-10 border-t border-[var(--color-surface-200-800)] py-6">
    <div class="mx-auto max-w-6xl px-4 text-center text-xs opacity-40 sm:px-6">
      {$translate('general.footer')}
    </div>
  </footer>
</div>
