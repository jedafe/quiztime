<script lang="ts">
  import { api } from '$lib/api';
  import { auth } from '$lib/stores/auth';
  import { goto } from '$app/navigation';

  let username = $state('');
  let email = $state('');
  let password = $state('');
  let error = $state('');
  let loading = $state(false);

  async function handleRegister() {
    loading = true;
    error = '';
    try {
      const res = await api.register({ username, email, password });
      auth.login(res.access_token, res.user);
      goto('/quizzes');
    } catch (e: any) {
      error = e.message || 'Registration failed';
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>Register — QuizTime</title>
</svelte:head>

<div class="relative -mx-4 sm:-mx-6">
  <div class="mx-auto grid max-w-6xl overflow-hidden rounded-none sm:mx-6 sm:rounded-2xl lg:grid-cols-2">
    <!-- Left — Dark hero panel -->
    <div class="relative flex flex-col justify-center bg-[#142033] px-8 py-16 sm:px-12 lg:px-14">
      <div class="pointer-events-none absolute inset-0 opacity-[0.04]" style="background-image: radial-gradient(circle at 1px 1px, rgba(255,255,255,0.4) 1px, transparent 0); background-size: 24px 24px;"></div>
      <div class="relative z-10">
        <div class="eyebrow mb-4 inline-flex items-center gap-1.5 rounded-full border border-white/15 bg-white/[0.07] px-3 py-1 text-[0.625rem] font-semibold uppercase tracking-[0.18em] text-white/70 backdrop-blur-sm">
          <span class="h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
          QuizTime Cloud
        </div>
        <h1 class="text-3xl font-bold tracking-[-0.04em] text-white sm:text-4xl">
          Join the<br />
          <span class="text-[var(--color-primary-400)]">community.</span>
        </h1>
        <p class="mt-4 max-w-sm text-sm leading-relaxed text-white/60">
          Create your free account and start challenging yourself with quizzes from around the world.
        </p>
        <div class="mt-6 flex flex-wrap gap-3">
          <a href="/login" class="btn-pill bg-white/10 text-white text-xs hover:bg-white/20">
            Already registered? Sign in
          </a>
        </div>
      </div>
    </div>

    <!-- Right — Register form panel -->
    <div class="flex flex-col justify-center bg-[var(--color-surface-50-950)] px-8 py-16 sm:px-12 lg:px-14">
      <div class="w-full max-w-sm">
        <p class="eyebrow">Get started</p>
        <h2 class="mt-1 text-2xl font-bold tracking-[-0.03em]">Create account</h2>

        {#if error}
          <div class="mt-4 rounded-xl bg-[var(--color-error-500)]/12 px-4 py-3 text-sm text-[var(--color-error-500)]">
            {error}
          </div>
        {/if}

        <form onsubmit={(e) => { e.preventDefault(); handleRegister(); }} class="mt-6 space-y-4">
          <div>
            <label class="mb-1.5 block text-sm font-medium">Username</label>
            <input type="text" bind:value={username} class="input-pill" placeholder="Choose a username" minlength="3" required />
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium">Email</label>
            <input type="email" bind:value={email} class="input-pill" placeholder="you@example.com" required />
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium">Password</label>
            <input type="password" bind:value={password} class="input-pill" placeholder="At least 6 characters" minlength="6" required />
          </div>
          <button type="submit" class="btn-pill btn-pill-primary w-full" disabled={loading}>
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <p class="divider-text mt-6">or</p>

        <p class="mt-6 text-center text-sm opacity-50">
          Already have an account? <a href="/login" class="font-semibold text-[var(--color-primary-500)] hover:underline">Sign in</a>
        </p>
      </div>
    </div>
  </div>
</div>
