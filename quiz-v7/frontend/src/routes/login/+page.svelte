<script lang="ts">
  import { api } from '$lib/api';
  import { auth } from '$lib/stores/auth';
  import { goto } from '$app/navigation';

  let username = '';
  let password = '';
  let error = '';
  let loading = false;

  async function handleLogin() {
    loading = true;
    error = '';
    try {
      const res = await api.login({ username, password });
      auth.login(res.access_token, res.user);
      goto('/quizzes');
    } catch (e: any) {
      error = e.message || 'Login failed';
    } finally {
      loading = false;
    }
  }
</script>

<div class="flex justify-center items-center min-h-[60vh]">
  <div class="card w-full max-w-md bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title text-2xl mb-4">Login</h2>

      {#if error}
        <div class="alert alert-error mb-4">
          <span>{error}</span>
        </div>
      {/if}

      <form on:submit|preventDefault={handleLogin}>
        <div class="form-control mb-3">
          <label class="label"><span class="label-text">Username</span></label>
          <input
            type="text"
            bind:value={username}
            class="input input-bordered w-full"
            required
          />
        </div>

        <div class="form-control mb-6">
          <label class="label"><span class="label-text">Password</span></label>
          <input
            type="password"
            bind:value={password}
            class="input input-bordered w-full"
            required
          />
        </div>

        <button type="submit" class="btn btn-primary w-full" disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>

      <p class="text-center mt-4 text-sm">
        Don't have an account? <a href="/register" class="link link-primary">Register</a>
      </p>
    </div>
  </div>
</div>
