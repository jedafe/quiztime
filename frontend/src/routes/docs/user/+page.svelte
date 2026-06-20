<script lang="ts">
  import { page } from '$app/stores';
  import { translate } from '$lib/stores/i18n';

  const faqItems = [
    { q: 'Can I take a quiz without an account?', a: 'No. You must be logged in so your scores are saved.' },
    { q: 'Can I retake a quiz?', a: 'Yes! Click "Retry Quiz" after viewing results. Each attempt is saved separately.' },
    { q: 'What happens if the timer runs out?', a: 'The quiz auto-submits with your selected answers. Unanswered questions count as wrong.' },
    { q: 'How is my score calculated?', a: 'Scoring happens server-side. Each correct answer earns points. Your score is displayed as a percentage.' },
    { q: 'What do the grade labels mean?', a: 'Fail (≤40%), Pass (41-59%), Good (60-69%), Excellent (≥70%).' },
    { q: 'Can I edit a quiz after creating it?', a: 'Yes. Go to Dashboard, click "Edit", and modify title, description, or questions.' },
    { q: 'How do I switch between dark and light mode?', a: 'Click the sun/moon icon in the top navigation bar to toggle between dark and light themes. Your choice persists across sessions.' },
  ];

  let currentSection = $state('');
  function updateSection() {
    const hash = window.location.hash.slice(1);
    currentSection = hash;
  }
  $effect(() => {
    if (typeof window !== 'undefined') {
      window.addEventListener('hashchange', updateSection);
      updateSection();
      return () => window.removeEventListener('hashchange', updateSection);
    }
  });
</script>

<svelte:head>
  <title>{$translate('docs.userGuide')} — QuizTime</title>
</svelte:head>

<div class="mb-8">
  <h1 class="mb-2 text-4xl font-bold heading-serif">{$translate('docs.userGuide')}</h1>
  <p class="opacity-60">{$translate('docs.userGuideSubtitle')}</p>
</div>

<!-- Mobile TOC -->
<details class="mb-6 rounded-xl border border-[var(--color-surface-300-700)] bg-[var(--color-surface-100-900)] lg:hidden">
  <summary class="flex cursor-pointer items-center gap-2 px-4 py-3 text-sm font-semibold transition-colors hover:bg-[var(--color-surface-200-800)] rounded-xl">
    <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" /></svg>
    {$translate('docs.contents')}
  </summary>
  <div class="space-y-0.5 border-t border-[var(--color-surface-300-700)] px-3 py-2">
    <a href="#getting-started" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">{$translate('docs.gettingStarted')}</a>
    <a href="#browse" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">{$translate('docs.browsingQuizzes')}</a>
    <a href="#taking" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">{$translate('docs.takingQuiz')}</a>
    <a href="#results" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">{$translate('docs.viewingResults')}</a>
    <a href="#dashboard" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">{$translate('docs.yourDashboard')}</a>
    <a href="#creating" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">{$translate('docs.creatingQuiz')}</a>
    <a href="#editing" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">{$translate('docs.editingQuiz')}</a>
    <a href="#import-export" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">{$translate('docs.importExport')}</a>
    <a href="#embed" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">{$translate('docs.embedQuizzes')}</a>
    <a href="#themes" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">{$translate('docs.themes')}</a>
    <a href="#faq" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">{$translate('docs.faq')}</a>
  </div>
</details>

<div class="grid gap-8 lg:grid-cols-[220px_1fr]">
  <aside class="hidden lg:block">
    <div class="sticky top-20 w-52 rounded-2xl border border-[var(--color-surface-300-700)] bg-[var(--color-surface-100-900)] shadow-lg">
      <div class="border-b border-[var(--color-surface-300-700)] px-4 py-3">
        <span class="text-sm font-semibold heading-serif">{$translate('docs.contents')}</span>
      </div>
      <div class="space-y-0.5 px-2 py-2">
        <a href="#getting-started" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">{$translate('docs.gettingStarted')}</a>
        <a href="#browse" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">{$translate('docs.browsingQuizzes')}</a>
        <a href="#taking" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">{$translate('docs.takingQuiz')}</a>
        <a href="#results" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">{$translate('docs.viewingResults')}</a>
        <a href="#dashboard" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">{$translate('docs.yourDashboard')}</a>
        <a href="#creating" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">{$translate('docs.creatingQuiz')}</a>
        <a href="#editing" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">{$translate('docs.editingQuiz')}</a>
        <a href="#import-export" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">{$translate('docs.importExport')}</a>
        <a href="#embed" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">{$translate('docs.embedQuizzes')}</a>
        <a href="#themes" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">{$translate('docs.themes')}</a>
        <a href="#faq" class="block rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-[var(--color-surface-200-800)]">{$translate('docs.faq')}</a>
      </div>
    </div>
  </aside>

  <main class="min-w-0 space-y-10">

    <section id="getting-started" class="frame overflow-hidden p-6">
      <h2 class="mb-4 text-2xl font-bold">{$translate('docs.gettingStarted')}</h2>
      <h3 class="mt-4 font-semibold">What is QuizTime?</h3>
      <p>QuizTime is a quiz platform where you can take quizzes on various topics, track your scores, and create your own quizzes for others to play.</p>
      <h3 class="mt-4 font-semibold">Create an Account</h3>
      <ol class="mt-2 space-y-1 text-sm">
        <li>1. Click <strong>"Register"</strong> in the top navigation bar.</li>
        <li>2. Enter a username, email, and password.</li>
        <li>3. Click <strong>"Create Account"</strong>.</li>
        <li>4. You'll be automatically logged in and redirected to the home page.</li>
      </ol>
      <div class="mt-4 rounded-lg bg-[var(--color-info-500)]/15 px-4 py-3 text-sm text-[var(--color-info-500)]">
        You can browse quizzes without an account, but you need to log in to take or create one.
      </div>
    </section>

    <section id="browse" class="frame overflow-hidden p-6">
      <h2 class="mb-4 text-2xl font-bold">{$translate('docs.browsingQuizzes')}</h2>
      <ol class="mt-2 space-y-1 text-sm">
        <li>1. Click <strong>"Browse"</strong> in the navigation bar.</li>
        <li>2. Scroll through the list of available quizzes.</li>
        <li>3. Each quiz card shows: title, description, and number of questions.</li>
      </ol>
      <h3 class="mt-4 font-semibold">Quiz Detail</h3>
      <p class="text-sm">Click a quiz card to see its detail page with full description, question count, attempts, and average score.</p>
    </section>

    <section id="taking" class="frame overflow-hidden p-6">
      <h2 class="mb-4 text-2xl font-bold">{$translate('docs.takingQuiz')}</h2>
      <div class="mt-4 grid gap-3 sm:grid-cols-2">
        <div class="rounded-lg bg-[var(--color-surface-200-800)] p-4">
          <h4 class="font-medium">Timer</h4>
          <p class="mt-1 text-sm opacity-50">30 seconds per question. Quiz auto-submits when time runs out.</p>
        </div>
        <div class="rounded-lg bg-[var(--color-surface-200-800)] p-4">
          <h4 class="font-medium">Progress Bar</h4>
          <p class="mt-1 text-sm opacity-50">Shows current question number out of total.</p>
        </div>
      </div>
      <h3 class="mt-4 font-semibold">Answering Questions</h3>
      <ol class="mt-2 space-y-1 text-sm">
        <li>1. <strong>Select your answer</strong> — Click options depending on type:
          <ul class="ml-6 mt-1 space-y-1">
            <li>• <strong>Single Select:</strong> Click one option.</li>
            <li>• <strong>Multi Select:</strong> Click multiple options.</li>
            <li>• <strong>True/False:</strong> Click True or False.</li>
          </ul>
        </li>
        <li>2. <strong>Check</strong> — Click "Check" to see if you're correct (green = correct, red = wrong).</li>
        <li>3. <strong>Move on</strong> — Click "Next" or "Finish" on the last question.</li>
      </ol>
      <h3 class="mt-4 font-semibold">Skipping</h3>
      <p class="text-sm">Click "Skip" to skip a question. The timer keeps running.</p>
    </section>

    <section id="results" class="frame overflow-hidden p-6">
      <h2 class="mb-4 text-2xl font-bold">{$translate('docs.viewingResults')}</h2>
      <div class="mt-4 grid gap-3 sm:grid-cols-2">
        <div class="rounded-lg bg-[var(--color-surface-200-800)] p-4">
          <h4 class="font-medium">Score</h4>
          <p class="mt-1 text-sm opacity-50">Your score out of total, plus percentage and grade.</p>
        </div>
        <div class="rounded-lg bg-[var(--color-surface-200-800)] p-4">
          <h4 class="font-medium">Grade</h4>
          <p class="mt-1 text-sm opacity-50">
            <span class="text-[var(--color-error-500)]">Fail</span> (≤40%),
            <span class="text-[var(--color-warning-500)]">Pass</span> (≤59%),
            <span class="text-[var(--color-primary-500)]">Good</span> (≤69%),
            <span class="text-[var(--color-success-500)]">Excellent</span> (&gt;69%)
          </p>
        </div>
      </div>
      <h3 class="mt-4 font-semibold">Actions</h3>
      <ul class="mt-2 space-y-1 text-sm">
        <li>• <strong>"Retry Quiz"</strong> — Take the same quiz again.</li>
        <li>• <strong>"Browse More"</strong> — Go back to the quiz list.</li>
        <li>• <strong>"Share Result"</strong> — Creates a shareable link with an OG image card you can post on social media.</li>
        <li>• <strong>"Challenge Friend"</strong> — Generate a challenge link with your score. Friends can accept and try to beat it.</li>
      </ul>
      <p class="mt-2 text-sm opacity-50">Scores are calculated server-side — tamper-proof.</p>
      <h3 class="mt-4 font-semibold">Leaderboard</h3>
      <p class="text-sm">Every quiz has a leaderboard tab showing top scores. Filter by period (Today, This Week, This Month, All Time). Only your best attempt counts.</p>
      <h3 class="mt-4 font-semibold">Challenges</h3>
      <p class="text-sm">After taking a quiz, click "Challenge Friend" to generate a challenge link. Share it with anyone — they accept and take the same quiz. Results compare both scores side-by-side.</p>
    </section>

    <section id="dashboard" class="frame overflow-hidden p-6">
      <h2 class="mb-4 text-2xl font-bold">{$translate('docs.yourDashboard')}</h2>
      <p>Click <strong>"Dashboard"</strong> to access your personal hub.</p>
      <h3 class="mt-4 font-semibold">Stats Cards</h3>
      <div class="mt-3 grid gap-3 sm:grid-cols-3">
        <div class="stat-pill">
          <span class="eyebrow">My Quizzes</span>
          <span class="text-2xl font-bold text-[var(--color-primary-500)]">—</span>
        </div>
        <div class="stat-pill">
          <span class="eyebrow">Attempts</span>
          <span class="text-2xl font-bold text-[var(--color-secondary-500)]">—</span>
        </div>
        <div class="stat-pill">
          <span class="eyebrow">Avg Score</span>
          <span class="text-2xl font-bold text-[var(--color-tertiary-500)]">—</span>
        </div>
      </div>
      <h3 class="mt-4 font-semibold">My Quizzes Table</h3>
      <p class="text-sm">Click "Edit" to modify, "Delete" to remove, or the title to view. Admins see all quizzes; regular users see only their own.</p>
    </section>

    <section id="creating" class="frame overflow-hidden p-6">
      <h2 class="mb-4 text-2xl font-bold">{$translate('docs.creatingQuiz')}</h2>
      <h3 class="mt-4 font-semibold">Step 1: Create the Quiz</h3>
      <ol class="mt-2 space-y-1 text-sm">
        <li>1. Click <strong>"Create Quiz"</strong> in the navigation bar.</li>
        <li>2. Enter a title (required) and description (optional).</li>
        <li>3. Click <strong>"Create Quiz"</strong>.</li>
      </ol>
      <h3 class="mt-4 font-semibold">Step 2: Add Questions</h3>
      <ol class="mt-2 space-y-1 text-sm">
        <li>1. Enter the question text.</li>
        <li>2. Select the type (Single, Multi, or True/False).</li>
        <li>3. Optionally select a category (categories are created by admins).</li>
        <li>4. Fill in options and click letter buttons to mark correct answers.</li>
        <li>5. Click <strong>"Add Question"</strong>.</li>
      </ol>
      <div class="mt-4 rounded-lg bg-[var(--color-info-500)]/15 px-4 py-3 text-sm text-[var(--color-info-500)]">
        For Multi Select, click multiple letter buttons to mark several correct answers. True/False questions automatically set the options.
      </div>
    </section>

    <section id="editing" class="frame overflow-hidden p-6">
      <h2 class="mb-4 text-2xl font-bold">{$translate('docs.editingQuiz')}</h2>
      <h3 class="mt-4 font-semibold">Accessing the Edit Page</h3>
      <ul class="mt-2 space-y-1 text-sm">
        <li>• From Dashboard, click <strong>"Edit"</strong> next to your quiz.</li>
        <li>• Or navigate to <code>/quizzes/{'{id}'}/edit</code> directly.</li>
      </ul>
      <h3 class="mt-4 font-semibold">Updating Quiz Details</h3>
      <p class="text-sm">Modify title or description, then click <strong>"Save Changes"</strong>. A confirmation message appears.</p>
      <h3 class="mt-4 font-semibold">Managing Questions</h3>
      <ul class="mt-2 space-y-1 text-sm">
        <li>• <strong>Add:</strong> Use the form at the bottom.</li>
        <li>• <strong>Delete:</strong> Click "Delete" and confirm in the modal dialog.</li>
      </ul>
    </section>

    <section id="import-export" class="frame overflow-hidden p-6">
      <h2 class="mb-4 text-2xl font-bold">{$translate('docs.importExport')}</h2>
      <h3 class="mt-4 font-semibold">Exporting a Quiz</h3>
      <p class="text-sm">If you own a quiz, open its detail page and click <strong>"Export JSON"</strong>. A JSON file containing the quiz and all its questions (including correct answers) downloads to your computer.</p>
      <h3 class="mt-4 font-semibold">Importing a Quiz</h3>
      <ol class="mt-2 space-y-1 text-sm">
        <li>1. Go to <strong>"Create Quiz"</strong> and switch to the <strong>"Import JSON"</strong> tab.</li>
        <li>2. Upload a JSON file matching the export format (quiz title, description, category name, and questions array).</li>
        <li>3. Click <strong>"Import Quiz"</strong>. The quiz and all its questions are created automatically.</li>
      </ol>
      <div class="mt-4 rounded-lg bg-[var(--color-info-500)]/15 px-4 py-3 text-sm text-[var(--color-info-500)]">
        Imports require a valid JSON structure. The format guide on the import page shows the expected schema.
      </div>
    </section>

    <section id="embed" class="frame overflow-hidden p-6">
      <h2 class="mb-4 text-2xl font-bold">{$translate('docs.embedQuizzes')}</h2>
      <p class="text-sm">You can embed your quizzes on any website, blog, or Notion page using an iframe snippet.</p>
      <h3 class="mt-4 font-semibold">Getting the Embed Code</h3>
      <ol class="mt-2 space-y-1 text-sm">
        <li>1. Open your quiz detail page.</li>
        <li>2. Click <strong>"Embed"</strong> to open the embed panel.</li>
        <li>3. Copy the HTML snippet shown.</li>
        <li>4. Paste it into any website's HTML where you want the quiz to appear.</li>
      </ol>
      <h3 class="mt-4 font-semibold">How It Works</h3>
      <ul class="mt-2 space-y-1 text-sm">
        <li>• The embed is a self-contained widget — no extra scripts or dependencies needed.</li>
        <li>• Users can take the quiz directly within the iframe.</li>
        <li>• Results are calculated server-side and saved automatically.</li>
        <li>• The widget communicates results back to the parent page via <code>postMessage</code> for custom event handling.</li>
      </ul>
      <h3 class="mt-4 font-semibold">Viewing Embed Submissions</h3>
      <p class="text-sm">As the quiz owner, you can see all embed submissions on the quiz detail page — click <strong>"Embed Submissions"</strong> to view scores, names, and timing.</p>
    </section>

    <section id="themes" class="frame overflow-hidden p-6">
      <h2 class="mb-4 text-2xl font-bold">{$translate('docs.themes')}</h2>
      <p>Click the sun/moon icon in the navigation bar to toggle between dark and light modes. Your choice persists across sessions.</p>
      <div class="mt-4 grid gap-3 sm:grid-cols-2">
        <div class="rounded-xl border border-[var(--color-surface-300-700)] bg-[var(--color-surface-200-800)] p-4 text-center">
          <span class="text-3xl">🌙</span>
          <h3 class="mt-2 font-semibold">Dark Mode</h3>
          <p class="mt-1 text-xs opacity-50">Deep, eye-friendly theme for low-light environments.</p>
        </div>
        <div class="rounded-xl border border-[var(--color-surface-300-700)] bg-[var(--color-surface-200-800)] p-4 text-center">
          <span class="text-3xl">☀️</span>
          <h3 class="mt-2 font-semibold">Light Mode</h3>
          <p class="mt-1 text-xs opacity-50">Clean, bright theme for daylight use.</p>
        </div>
      </div>
      <p class="mt-3 text-sm opacity-50">Themes are applied via the <code>data-theme</code> attribute using Skeleton v4's theme system.</p>
    </section>

    <section id="faq" class="frame overflow-hidden p-6">
      <h2 class="mb-4 text-2xl font-bold">{$translate('docs.faq')}</h2>
      <div class="mt-4 space-y-3">
        {#each faqItems as item}
          <details class="group rounded-xl border border-[var(--color-surface-300-700)] bg-[var(--color-surface-50-950)]">
            <summary class="cursor-pointer p-4 font-medium transition-colors hover:bg-[var(--color-surface-200-800)] rounded-xl">{item.q}</summary>
            <div class="px-4 pb-4">
              <p class="text-sm opacity-60">{item.a}</p>
            </div>
          </details>
        {/each}
      </div>
    </section>
  </main>
</div>
