<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  import { isLoggedIn } from '$lib/stores/auth';
  import type { PageData } from './$types';

  export let data: PageData;
  const quiz = data.quiz;
  const hasAnswers = quiz.questions?.[0]?.answer != null;

  let currentIndex = 0;
  let answers: Record<string, number[]> = {};
  let selectedOptions: number[] = [];
  let timeSpent = 0;
  let timerInterval: ReturnType<typeof setInterval>;
  let showFeedback = false;
  let isCorrect = false;
  let quizFinished = false;
  let submitting = false;

  const totalQuestions = quiz.questions?.length || 0;
  const timePerQuestion = 30;
  const totalTime = totalQuestions * timePerQuestion;
  let countdown = totalTime;

  $: currentQuestion = quiz.questions?.[currentIndex];
  $: progress = ((currentIndex + 1) / totalQuestions) * 100;
  $: minutes = Math.floor(countdown / 60);
  $: seconds = countdown % 60;
  $: formattedTime = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

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
      });
      goto(`/quizzes/${quiz.id}/results?attemptId=${result.id}`);
    } catch (e) {
      goto(`/quizzes/${quiz.id}/results`);
    }
  }
</script>

<div class="mb-4">
  <a href="/quizzes/{quiz.id}" class="btn btn-ghost btn-sm">← {quiz.title}</a>
</div>

{#if !hasAnswers}
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body items-center text-center">
      <h2 class="card-title">Login Required</h2>
      <p class="text-base-content/70">You need to be logged in to take this quiz.</p>
      <div class="card-actions mt-4">
        <a href="/login" class="btn btn-primary">Login</a>
        <a href="/register" class="btn btn-outline">Register</a>
      </div>
    </div>
  </div>
{:else}
<div class="card bg-base-100 shadow-xl">
  <div class="card-body">
    <!-- Header -->
    <div class="flex justify-between items-center mb-4">
      <div>
        <span class="text-sm text-base-content/60">
          Question {currentIndex + 1} of {totalQuestions}
        </span>
      </div>
      <div class="badge badge-lg" class:badge-error={countdown < 60}>
        {formattedTime}
      </div>
    </div>

    <!-- Progress -->
    <progress class="progress progress-primary w-full" value={currentIndex + 1} max={totalQuestions}></progress>

    {#if currentQuestion}
      <!-- Question -->
      <div class="mt-6 mb-4">
        <span class="badge badge-outline mb-2">{currentQuestion.type}</span>
        <h2 class="text-xl font-semibold">{currentQuestion.text}</h2>
      </div>

      <!-- Options -->
      <div class="space-y-3">
        {#each currentQuestion.options as option, i}
          <button
            class="block w-full text-left rounded-lg border-2 p-4 transition-all
              {selectedOptions.includes(i)
                ? 'border-primary bg-primary/10'
                : 'border-base-300 hover:border-primary/50'}
              {showFeedback && currentQuestion.answer.includes(i)
                ? 'border-success bg-success/20'
                : ''}
              {showFeedback && selectedOptions.includes(i) && !currentQuestion.answer.includes(i)
                ? 'border-error bg-error/20'
                : ''}
            "
            on:click={() => toggleOption(i)}
            disabled={showFeedback}
          >
            <span class="font-medium">{String.fromCharCode(65 + i)}.</span>
            {option}
          </button>
        {/each}
      </div>

      <!-- Feedback -->
      {#if showFeedback}
        <div class="alert mt-4" class:alert-success={isCorrect} class:alert-error={!isCorrect}>
          <span>{isCorrect ? 'Correct!' : 'Wrong!'}</span>
        </div>
      {/if}

      <!-- Actions -->
      <div class="flex justify-center gap-3 mt-6">
        {#if !showFeedback}
          <button class="btn btn-outline" on:click={skipQuestion}>Skip</button>
          <button
            class="btn btn-primary"
            on:click={checkAnswer}
            disabled={selectedOptions.length === 0}
          >
            Check
          </button>
        {:else}
          <button class="btn btn-primary" on:click={nextQuestion}>
            {currentIndex < totalQuestions - 1 ? 'Next' : 'Finish'}
          </button>
        {/if}
      </div>
    {/if}
  </div>
</div>
{/if}
