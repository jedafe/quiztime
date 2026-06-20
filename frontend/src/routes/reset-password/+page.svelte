<script lang="ts">
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
      message = r.message || 'Password reset successfully!';
    } catch (e: any) {
      error = e.message || 'Reset failed. The link may have expired.';
    }
  }
</script>

<svelte:head>
  <title>Reset Password — QuizTime</title>
</svelte:head>

<div class="page-enter mx-auto max-w-md pt-12">
  <div class="text-center">
    <span class="text-4xl">{message ? '✅' : '🔐'}</span>
    <h1 class="mt-4 text-2xl font-bold tracking-[-0.02em]">Reset Password</h1>
  </div>

  <div class="frame mt-6 p-6">
    {#if message}
      <div class="rounded-xl bg-[var(--color-success-500)]/12 px-4 py-3 text-sm text-[var(--color-success-500)]">
        {message}
      </div>
      <a href="/login" class="btn-pill btn-pill-primary mt-4 block w-full text-center">Go to Login</a>
    {:else}
      {#if error}
        <div class="mb-4 rounded-xl bg-[var(--color-error-500)]/12 px-4 py-3 text-sm text-[var(--color-error-500)]">{error}</div>
      {/if}
      <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
        <label class="text-sm font-medium">New Password</label>
        <input
          class="input mt-1 w-full"
          type="password"
          bind:value={newPassword}
          placeholder="At least 6 characters"
          required
          minlength={6}
        />
        <button type="submit" class="btn-pill btn-pill-primary mt-4 w-full">Reset Password</button>
      </form>
    {/if}
  </div>
</div>
