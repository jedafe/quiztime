<script lang="ts">
  import { translate } from '$lib/stores/i18n';
  import { onMount, onDestroy } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  import { isLoggedIn } from '$lib/stores/auth';
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();
  let quiz = data.quiz;
  let hasAnswers = quiz.questions?.[0]?.answer != null;

  let currentIndex = $state(0);
  let answers: Record<string, number[]> = {};
  let selectedOptions = $state<number[]>([]);
  let timeSpent = $state(0);
  let timerInterval: ReturnType<typeof setInterval>;
  let showFeedback = $state(false);
  let isCorrect = $state(false);
  let quizFinished = $state(false);
  let submitting = $state(false);

  let totalQuestions = quiz.questions?.length || 0;
  let timePerQuestion = 30;
  let totalTime = totalQuestions * timePerQuestion;
  let countdown = $state(totalTime);

  let currentQuestion = $derived(quiz.questions?.[currentIndex]);
  let progress = $derived(((currentIndex + 1) / totalQuestions) * 100);
  let minutes = $derived(Math.floor(countdown / 60));
  let seconds = $derived(countdown % 60);
  let formattedTime = $derived(`${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`);
  let timerUrgent = $derived(countdown < 60);

  onMount(() => {
    if (!$isLoggedIn) {
      goto('/login');
      return;
    }

    timerInterval = setInterval(() => {
      countdown--;
      timeSpent++;
      if (countdown <= 0) {
        finishQuiz();
      }
    }, 1000);
  });

  onDestroy(() => {
    if (timerInterval) clearInterval(timerInterval);
  });

  function toggleOption(index: number) {
    if (showFeedback) return;

    if (currentQuestion.type === 'multiple') {
      const idx = selectedOptions.indexOf(index);
      if (idx === -1) {
        selectedOptions = [...selectedOptions, index];
      } else {
        selectedOptions = selectedOptions.filter((i) => i !== index);
      }
    } else {
      selectedOptions = [index];
    }
  }

  function checkAnswer() {
    if (selectedOptions.length === 0) return;

    const qId = currentQuestion.id;
    const correct = currentQuestion.answer;

    isCorrect =
      selectedOptions.length === correct.length &&
      [...selectedOptions].sort().join(',') === [...correct].sort().join(',');

    answers[qId] = [...selectedOptions];
    showFeedback = true;
  }

  function nextQuestion() {
    showFeedback = false;
    selectedOptions = [];

    if (currentIndex < totalQuestions - 1) {
      currentIndex++;
    } else {
      finishQuiz();
    }
  }

  function skipQuestion() {
    showFeedback = false;
    selectedOptions = [];
    if (currentIndex < totalQuestions - 1) {
      currentIndex++;
    } else {
      finishQuiz();
    }
  }

  let challengeCode = $state('');

  onMount(() => {
    challengeCode = $page.url.searchParams.get('challenge') || '';
  });

  async function finishQuiz() {
    if (submitting || quizFinished) return;
    submitting = true;
    if (timerInterval) clearInterval(timerInterval);
    quizFinished = true;

    try {
      const result = await api.submitAttempt({
        quiz_id: quiz.id,
        answers,
        time_spent: timeSpent,
        challenge_code: challengeCode || undefined,
      });
      const params = new URLSearchParams({ attemptId: result.id });
      if (challengeCode) params.set('challenge', challengeCode);
      goto(`/quizzes/${quiz.id}/results?${params}`);
    } catch (e) {
      goto(`/quizzes/${quiz.id}/results`);
    }
  }
</script>

<svelte:head>
  <title>{$translate('quiz.takeQuiz')} — {quiz.title}</title>
</svelte:head>

<div class="page-enter mx-auto max-w-2xl">
  <a href="/quizzes/{quiz.id}" class="mb-4 inline-flex items-center gap-1 text-sm font-medium opacity-50 transition-opacity hover:opacity-100">
    ← {quiz.title}
  </a>

  {#if !hasAnswers}
    <div class="frame p-8 text-center">
      <h2 class="text-xl font-bold">{$translate('take.loginRequired')}</h2>
      <p class="mt-2 opacity-50">{$translate('take.loginToTake')}</p>
      <div class="mt-6 flex justify-center gap-2">
        <a href="/login" class="btn-pill btn-pill-primary">{$translate('auth.loginTitle')}</a>
        <a href="/register" class="btn-pill btn-pill-outline">{$translate('auth.registerTitle')}</a>
      </div>
    </div>
  {:else}
    <div class="frame p-6 sm:p-8">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <span class="text-sm font-medium opacity-50">
          {$translate('take.questionOf', {current: currentIndex + 1, total: totalQuestions})}
        </span>
        <span class="rounded-full px-3 py-1 text-sm font-bold
          {timerUrgent
            ? 'bg-[var(--color-error-500)]/15 text-[var(--color-error-500)]'
            : 'bg-[var(--color-surface-200-800)]'}">
          {formattedTime}
        </span>
      </div>

      <!-- Progress bar -->
      <div class="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-[var(--color-surface-200-800)]">
        <div
          class="h-full rounded-full bg-[var(--color-primary-500)] transition-all duration-300"
          style="width: {progress}%"
        ></div>
      </div>

      {#if currentQuestion}
        <!-- Question -->
        <div class="mt-8">
          <span class="mb-2 inline-block rounded-full bg-[var(--color-surface-200-800)] px-2.5 py-0.5 text-xs font-medium">{currentQuestion.type}</span>
          <h2 class="text-xl font-semibold leading-relaxed">{currentQuestion.text}</h2>
        </div>

        <!-- Options -->
        <div class="mt-6 space-y-3">
          {#each currentQuestion.options as option, i}
            <button
              class="block w-full rounded-xl border-2 p-4 text-left transition-all
                {selectedOptions.includes(i)
                  ? 'border-[var(--color-primary-500)] bg-[var(--color-primary-500)]/10'
                  : 'border-[var(--color-surface-300-700)] hover:border-[var(--color-primary-500)]/50 hover:bg-[var(--color-surface-200-800)]'}
                {showFeedback && currentQuestion.answer.includes(i)
                  ? '!border-[var(--color-success-500)] !bg-[var(--color-success-500)]/15'
                  : ''}
                {showFeedback && selectedOptions.includes(i) && !currentQuestion.answer.includes(i)
                  ? '!border-[var(--color-error-500)] !bg-[var(--color-error-500)]/15'
                  : ''}
              "
              onclick={() => toggleOption(i)}
              disabled={showFeedback}
            >
              <span class="mr-3 inline-flex h-7 w-7 items-center justify-center rounded-full bg-[var(--color-surface-200-800)] text-xs font-bold">{String.fromCharCode(65 + i)}</span>
              <span class="font-medium">{option}</span>
            </button>
          {/each}
        </div>

        <!-- Feedback -->
        {#if showFeedback}
          <div class="mt-5 rounded-xl px-5 py-3.5 text-sm font-semibold {isCorrect
            ? 'bg-[var(--color-success-500)]/15 text-[var(--color-success-500)]'
            : 'bg-[var(--color-error-500)]/15 text-[var(--color-error-500)]'}">
            {isCorrect ? $translate('take.correct') : $translate('take.wrong')}
          </div>
        {/if}

        <!-- Actions -->
        <div class="mt-8 flex justify-center gap-3">
          {#if !showFeedback}
            <button class="btn-pill btn-pill-outline" onclick={skipQuestion}>
              {$translate('quiz.skip')}
            </button>
            <button
              class="btn-pill btn-pill-primary"
              onclick={checkAnswer}
              disabled={selectedOptions.length === 0}
            >
              {$translate('take.check')}
            </button>
          {:else}
            <button class="btn-pill btn-pill-primary" onclick={nextQuestion}>
              {currentIndex < totalQuestions - 1 ? $translate('take.nextArrow') : $translate('quiz.finish')}
            </button>
          {/if}
        </div>
      {/if}
    </div>
  {/if}
</div>
