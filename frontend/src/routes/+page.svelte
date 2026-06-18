<script lang="ts">
  import { api } from '$lib/api';
  import { isLoggedIn } from '$lib/stores/auth';
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();
</script>

<svelte:head>
  <title>QuizTime — Test Your Knowledge</title>
</svelte:head>

<!-- Hero: 2-column split (OpenWork-inspired) -->
<section class="page-enter relative -mx-4 sm:-mx-6">
  <div class="mx-auto grid max-w-6xl overflow-hidden rounded-none sm:mx-6 sm:rounded-2xl lg:grid-cols-2">
    <!-- Left — Dark hero panel (OpenWork sign-in style) -->
    <div class="relative flex flex-col justify-center bg-[#142033] px-8 py-16 sm:px-12 lg:px-14">
      <!-- Paper shader canvas effect -->
      <div class="pointer-events-none absolute inset-0 opacity-[0.04]" style="background-image: radial-gradient(circle at 1px 1px, rgba(255,255,255,0.4) 1px, transparent 0); background-size: 24px 24px;"></div>
      <div class="relative z-10">
        <!-- Eyebrow badge -->
        <div class="eyebrow mb-4 inline-flex items-center gap-1.5 rounded-full border border-white/15 bg-white/[0.07] px-3 py-1 text-[0.625rem] font-semibold uppercase tracking-[0.18em] text-white/70 backdrop-blur-sm">
          <span class="h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
          Quiz Platform v7
        </div>
        <!-- Heading -->
        <h1 class="text-4xl font-bold tracking-[-0.04em] text-white sm:text-5xl">
          One quiz,<br />
          <span class="text-[var(--color-primary-400)]">every seat.</span>
        </h1>
        <p class="mt-4 max-w-md text-base leading-relaxed text-white/60">
          Challenge yourself with community-created quizzes. Create, share, and compete — all in one place.
        </p>
        <!-- CTA buttons -->
        <div class="mt-8 flex flex-wrap gap-3">
          <a href="/quizzes" class="btn-pill bg-white !text-[var(--color-surface-950)] font-semibold shadow-lg hover:shadow-xl hover:opacity-90">
            Browse Quizzes
          </a>
          {#if $isLoggedIn}
            <a href="/dashboard" class="btn-pill bg-white/10 text-white hover:bg-white/20">
              Dashboard
            </a>
          {:else}
            <a href="/register" class="btn-pill bg-white/10 text-white hover:bg-white/20">
              Get Started
            </a>
          {/if}
        </div>
      </div>
    </div>

    <!-- Right — Feature cards panel -->
    <div class="flex flex-col justify-center gap-4 bg-[var(--color-surface-50-950)] px-8 py-16 sm:px-12 lg:px-14">
      <div class="space-y-1">
        <p class="eyebrow">Features</p>
        <h2 class="text-2xl font-bold tracking-[-0.03em]">Why QuizTime?</h2>
      </div>
      <div class="grid gap-3">
        {#each [
          { icon: '⚡', title: 'Instant Feedback', desc: 'Get results and explanations the moment you finish a quiz.' },
          { icon: '🎯', title: 'Multiple Formats', desc: 'Single choice, multiple choice, true/false — every style supported.' },
          { icon: '📊', title: 'Track Progress', desc: 'View your attempt history, scores, and personal stats over time.' },
        ] as feature}
          <div class="frame-lift flex items-start gap-4 p-4">
            <span class="mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-[14px] bg-[var(--color-primary-500)]/10 text-lg" role="img" aria-hidden="true">{feature.icon}</span>
            <div>
              <h3 class="font-semibold">{feature.title}</h3>
              <p class="mt-0.5 text-sm opacity-50">{feature.desc}</p>
            </div>
          </div>
        {/each}
      </div>
    </div>
  </div>
</section>

<!-- Featured Quizzes -->
{#if data.featured?.length > 0}
  <section class="page-enter mt-12">
    <div class="mb-6 flex items-center justify-between">
      <div>
        <p class="eyebrow">Explore</p>
        <h2 class="text-2xl font-bold tracking-[-0.03em]">Featured Quizzes</h2>
      </div>
      <a href="/quizzes" class="btn-pill btn-pill-ghost btn-pill-sm">View all →</a>
    </div>
    <div class="stagger grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {#each data.featured as quiz}
        <a href="/quizzes/{quiz.id}" class="frame-lift block p-5">
          <h3 class="font-bold transition-colors group-hover:text-[var(--color-primary-500)]">{quiz.title}</h3>
          <p class="mt-1 text-sm opacity-50">{quiz.question_count} questions</p>
          <div class="mt-4 flex items-center justify-end">
            <span class="btn-pill btn-pill-primary btn-pill-sm">
              Take Quiz →
            </span>
          </div>
        </a>
      {/each}
    </div>
  </section>
{/if}

<!-- CTA Banner -->
<section class="page-enter mt-12">
  <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-[#142033] to-[#1e2a45] px-8 py-12 text-center sm:px-14">
    <div class="pointer-events-none absolute inset-0 opacity-[0.03]" style="background-image: radial-gradient(circle at 1px 1px, rgba(255,255,255,0.4) 1px, transparent 0); background-size: 20px 20px;"></div>
    <div class="relative z-10">
      <p class="eyebrow justify-center text-white/50">Get Started</p>
      <h2 class="mt-2 text-3xl font-bold text-white">Ready to challenge yourself?</h2>
      <p class="mt-3 text-white/50">Join the community and start testing your knowledge today.</p>
      <div class="mt-6 flex justify-center gap-3">
        {#if $isLoggedIn}
          <a href="/create" class="btn-pill bg-white !text-[var(--color-surface-950)] font-semibold">Create a Quiz</a>
        {:else}
          <a href="/register" class="btn-pill bg-white !text-[var(--color-surface-950)] font-semibold">Join Free</a>
          <a href="/login" class="btn-pill bg-white/10 text-white hover:bg-white/20">Sign In</a>
        {/if}
      </div>
    </div>
  </div>
</section>
