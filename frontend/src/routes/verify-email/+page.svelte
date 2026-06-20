<script lang="ts">
  import { translate } from '$lib/stores/i18n';
  import { api } from '$lib/api';

  let { data } = $props();

  let message = $state(data.message || '');
  let error = $state(data.error || '');
  let token = $state(data.token || '');
  let emailSent = $state(false);

  async function resend() {
    try {
      const r = await api.resendVerification();
      message = r.message || $translate('verify.emailSent');
      error = '';
    } catch (e: any) {
      error = e.message || 'Failed to resend.';
    }
  }
</script>

<svelte:head>
  <title>{$translate('verify.title')} — QuizTime</title>
</svelte:head>

<div class="page-enter mx-auto max-w-md pt-12">
  <div class="text-center">
    <span class="text-4xl">{message ? '✅' : '📧'}</span>
    <h1 class="mt-4 text-2xl font-bold tracking-[-0.02em]">{$translate('verify.title')}</h1>
  </div>

  <div class="frame mt-6 p-6">
    {#if message}
      <div class="rounded-xl bg-[var(--color-success-500)]/12 px-4 py-3 text-sm text-[var(--color-success-500)]">
        {message}
      </div>
      <a href="/dashboard" class="btn-pill btn-pill-primary mt-4 block w-full text-center">{$translate('verify.goToDashboard')}</a>
    {:else if error}
      <div class="rounded-xl bg-[var(--color-error-500)]/12 px-4 py-3 text-sm text-[var(--color-error-500)]">
        {error}
      </div>
      {#if token}
        <p class="mt-3 text-sm opacity-60">{$translate('verify.linkExpired')}</p>
      {/if}
    {:else}
      <p class="text-sm opacity-60">{$translate('verify.noToken')}</p>
    {/if}

    {#if !message}
      <button
        class="btn-pill btn-pill-primary mt-4 w-full text-center"
        onclick={resend}
        disabled={emailSent}
      >
        {emailSent ? $translate('verify.sent') : $translate('verify.resend')}
      </button>
    {/if}
  </div>
</div>
