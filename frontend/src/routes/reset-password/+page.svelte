<script lang="ts">
  import { translate } from '$lib/stores/i18n';
  import { api } from '$lib/api';

  let { data } = $props();

  let token = $state(data.token);
  let newPassword = $state('');
  let message = $state('');
  let error = $state('');

  async function handleSubmit() {
    error = '';
    message = '';
    if (!token) { error = 'Missing reset token.'; return; }
    if (newPassword.length < 6) { error = 'Password must be at least 6 characters.'; return; }
    try {
      const r = await api.resetPassword(token, newPassword);
      message = r.message || $translate('password.resetSuccess');
    } catch (e: any) {
      error = e.message || 'Reset failed. The link may have expired.';
    }
  }
</script>

<svelte:head>
  <title>{$translate('password.resetTitle')} — QuizTime</title>
</svelte:head>

<div class="page-enter mx-auto max-w-md pt-12">
  <div class="text-center">
    <span class="text-4xl">{message ? '✅' : '🔐'}</span>
    <h1 class="mt-4 text-2xl font-bold tracking-[-0.02em]">{$translate('password.resetTitle')}</h1>
  </div>

  <div class="frame mt-6 p-6">
    {#if message}
      <div class="rounded-xl bg-[var(--color-success-500)]/12 px-4 py-3 text-sm text-[var(--color-success-500)]">
        {message}
      </div>
      <a href="/login" class="btn-pill btn-pill-primary mt-4 block w-full text-center">{$translate('password.goToLogin')}</a>
    {:else}
      {#if error}
        <div class="mb-4 rounded-xl bg-[var(--color-error-500)]/12 px-4 py-3 text-sm text-[var(--color-error-500)]">{error}</div>
      {/if}
      <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
        <label class="text-sm font-medium">{$translate('password.newPassword')}</label>
        <input
          class="input mt-1 w-full"
          type="password"
          bind:value={newPassword}
          placeholder={$translate('password.passwordPlaceholder')}
          required
          minlength={6}
        />
        <button type="submit" class="btn-pill btn-pill-primary mt-4 w-full">{$translate('password.resetButton')}</button>
      </form>
    {/if}
  </div>
</div>
