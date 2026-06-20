<script lang="ts">
  import { api } from '$lib/api';

  let email = $state('');
  let message = $state('');
  let error = $state('');
  let sent = $state(false);

  async function handleSubmit() {
    message = '';
    error = '';
    if (!email) { error = 'Email is required.'; return; }
    try {
      const r = await api.forgotPassword(email);
      message = r.message || 'If that email is registered, a reset link was sent.';
      sent = true;
    } catch (e: any) {
      error = e.message || 'Something went wrong.';
    }
  }
</script>

<svelte:head>
  <title>Forgot Password — QuizTime</title>
</svelte:head>

<div class="page-enter mx-auto max-w-md pt-12">
  <div class="text-center">
    <span class="text-4xl">🔑</span>
    <h1 class="mt-4 text-2xl font-bold tracking-[-0.02em]">Forgot Password</h1>
    <p class="mt-2 text-sm opacity-60">Enter your email and we'll send a reset link.</p>
  </div>

  <div class="frame mt-6 p-6">
    {#if sent}
      <div class="rounded-xl bg-[var(--color-success-500)]/12 px-4 py-3 text-sm text-[var(--color-success-500)]">
        {message}
      </div>
      <a href="/login" class="btn-pill btn-pill-primary mt-4 block w-full text-center">Back to Login</a>
    {:else}
      {#if error}
        <div class="mb-4 rounded-xl bg-[var(--color-error-500)]/12 px-4 py-3 text-sm text-[var(--color-error-500)]">{error}</div>
      {/if}
      <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
        <label class="text-sm font-medium">Email</label>
        <input
          class="input mt-1 w-full"
          type="email"
          bind:value={email}
          placeholder="you@example.com"
          required
        />
        <button type="submit" class="btn-pill btn-pill-primary mt-4 w-full">Send Reset Link</button>
      </form>
    {/if}
  </div>
</div>
