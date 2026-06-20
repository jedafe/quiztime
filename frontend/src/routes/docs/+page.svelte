<script lang="ts">
  import { translate } from '$lib/stores/i18n';
  import { isLoggedIn, isAdmin } from '$lib/stores/auth';
</script>

<svelte:head>
  <title>{$translate('docs.title')} — QuizTime</title>
</svelte:head>

<div class="page-enter mb-8">
  <h1 class="text-4xl font-bold">{$translate('docs.title')}</h1>
  <p class="mt-2 opacity-50">{$translate('docs.subtitle')}</p>
</div>

<div class="stagger grid gap-5 sm:grid-cols-3">
  {#if $isLoggedIn && $isAdmin}
    <a href="/docs/developer" class="frame-lift flex flex-col items-center p-6 text-center">
      <span class="mb-3 text-4xl">💻</span>
      <h2 class="font-bold">{$translate('docs.developerGuide')}</h2>
      <p class="mt-1 text-sm opacity-50">{$translate('docs.developerDesc')}</p>
      <span class="btn-pill btn-pill-primary btn-pill-sm mt-3">{$translate('docs.readGuide')}</span>
    </a>

    <a href="/docs/admin" class="frame-lift flex flex-col items-center p-6 text-center">
      <span class="mb-3 text-4xl">⚙️</span>
      <h2 class="font-bold">{$translate('docs.adminGuide')}</h2>
      <p class="mt-1 text-sm opacity-50">{$translate('docs.adminDesc')}</p>
      <span class="btn-pill btn-pill-primary btn-pill-sm mt-3">{$translate('docs.readGuide')}</span>
    </a>
  {/if}

  <a href="/docs/user" class="frame-lift flex flex-col items-center p-6 text-center"
    class:sm:col-span-3={!($isLoggedIn && $isAdmin)}
  >
    <span class="mb-3 text-4xl">📖</span>
    <h2 class="font-bold">{$translate('docs.userGuide')}</h2>
    <p class="mt-1 text-sm opacity-50">{$translate('docs.userDesc')}</p>
    <span class="btn-pill btn-pill-primary btn-pill-sm mt-3">{$translate('docs.readGuide')}</span>
  </a>
</div>
