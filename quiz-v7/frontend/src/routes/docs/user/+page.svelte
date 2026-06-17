<script lang="ts">
  const faqItems = [
    { q: 'Can I take a quiz without an account?', a: 'No. You must be logged in so your scores are saved.' },
    { q: 'Can I retake a quiz?', a: 'Yes! Click "Retry Quiz" after viewing results. Each attempt is saved separately.' },
    { q: 'What happens if the timer runs out?', a: 'The quiz auto-submits with your selected answers. Unanswered questions count as wrong.' },
    { q: 'How is my score calculated?', a: 'Each correct answer earns 3 points. Your score is displayed as a percentage.' },
    { q: 'What do the grade labels mean?', a: 'Fail (≤40%), Pass (41-59%), Good (60-69%), Excellent (≥70%).' },
    { q: 'Can I edit a quiz after creating it?', a: 'Yes. Go to Dashboard, click "Edit", and modify title, description, or questions.' },
  ];
</script>

<svelte:head>
  <title>User Guide — QuizTime</title>
</svelte:head>

<div class="mb-8">
  <h1 class="text-4xl font-bold mb-2">User Guide</h1>
  <p class="text-base-content/60">How to use QuizTime — take quizzes, track your progress, and create your own.</p>
</div>

<div class="grid lg:grid-cols-[220px_1fr] gap-8">
  <aside class="hidden lg:block">
    <ul class="menu bg-base-100 rounded-box shadow w-52 sticky top-20">
      <li class="menu-title">Contents</li>
      <li><a href="#getting-started">Getting Started</a></li>
      <li><a href="#browse">Browsing Quizzes</a></li>
      <li><a href="#taking">Taking a Quiz</a></li>
      <li><a href="#results">Viewing Results</a></li>
      <li><a href="#dashboard">Your Dashboard</a></li>
      <li><a href="#creating">Creating a Quiz</a></li>
      <li><a href="#editing">Editing a Quiz</a></li>
      <li><a href="#themes">Themes</a></li>
      <li><a href="#faq">FAQ</a></li>
    </ul>
  </aside>

  <main class="space-y-12">

    <section id="getting-started" class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">Getting Started</h2>
        <h3 class="font-semibold mt-4">What is QuizTime?</h3>
        <p>QuizTime is a quiz platform where you can take quizzes on various topics, track your scores, and create your own quizzes for others to play.</p>
        <h3 class="font-semibold mt-4">Create an Account</h3>
        <ol class="list-decimal list-inside text-sm space-y-1">
          <li>Click <strong>"Register"</strong> in the top navigation bar.</li>
          <li>Enter a username, email, and password.</li>
          <li>Click <strong>"Create Account"</strong>.</li>
          <li>You'll be automatically logged in and redirected to the home page.</li>
        </ol>
        <div class="alert alert-info mt-4">
          <span class="text-sm">You can browse quizzes without an account, but you need to log in to take or create one.</span>
        </div>
      </div>
    </section>

    <section id="browse" class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">Browsing Quizzes</h2>
        <ol class="list-decimal list-inside text-sm space-y-1">
          <li>Click <strong>"Browse"</strong> in the navigation bar.</li>
          <li>Scroll through the list of available quizzes.</li>
          <li>Each quiz card shows: title, description, number of questions, and creator.</li>
        </ol>
        <h3 class="font-semibold mt-4">Quiz Detail</h3>
        <p class="text-sm">Click a quiz title to see its detail page with full description, question list, and average score.</p>
      </div>
    </section>

    <section id="taking" class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">Taking a Quiz</h2>
        <div class="grid sm:grid-cols-2 gap-4 mt-4">
          <div class="bg-base-200 p-4 rounded-lg">
            <h4 class="font-medium">Timer</h4>
            <p class="text-sm text-base-content/60">30 seconds per question. Quiz auto-submits when time runs out.</p>
          </div>
          <div class="bg-base-200 p-4 rounded-lg">
            <h4 class="font-medium">Progress Bar</h4>
            <p class="text-sm text-base-content/60">Shows current question number out of total.</p>
          </div>
        </div>
        <h3 class="font-semibold mt-4">Answering Questions</h3>
        <ol class="list-decimal list-inside text-sm space-y-1">
          <li><strong>Select your answer</strong> — Click options depending on type:
            <ul class="list-disc list-inside ml-6 mt-1">
              <li><strong>Single Select:</strong> Click one option.</li>
              <li><strong>Multi Select:</strong> Click multiple options.</li>
              <li><strong>True/False:</strong> Click True or False.</li>
            </ul>
          </li>
          <li><strong>Check</strong> — Click "Check" to see if you're correct (green = correct, red = wrong).</li>
          <li><strong>Move on</strong> — Click "Next" or "Finish" on the last question.</li>
        </ol>
        <h3 class="font-semibold mt-4">Skipping</h3>
        <p class="text-sm">Click "Skip" to skip a question. The timer keeps running.</p>
      </div>
    </section>

    <section id="results" class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">Viewing Results</h2>
        <div class="grid sm:grid-cols-2 gap-4 mt-4">
          <div class="bg-base-200 p-4 rounded-lg">
            <h4 class="font-medium">Score Circle</h4>
            <p class="text-sm text-base-content/60">Your percentage in a radial progress indicator.</p>
          </div>
          <div class="bg-base-200 p-4 rounded-lg">
            <h4 class="font-medium">Grade</h4>
            <p class="text-sm text-base-content/60">
              <span class="text-error">Fail</span> (≤40%),
              <span class="text-warning">Pass</span> (≤59%),
              <span class="text-primary">Good</span> (≤69%),
              <span class="text-success">Excellent</span> (&gt;69%)
            </p>
          </div>
        </div>
        <h3 class="font-semibold mt-4">Actions</h3>
        <ul class="list-disc list-inside text-sm mt-2 space-y-1">
          <li><strong>"Retry Quiz"</strong> — Take the same quiz again.</li>
          <li><strong>"Browse More"</strong> — Go back to the quiz list.</li>
        </ul>
      </div>
    </section>

    <section id="dashboard" class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">Your Dashboard</h2>
        <p>Click <strong>"Dashboard"</strong> to access your personal hub.</p>
        <h3 class="font-semibold mt-4">Stats Cards</h3>
        <div class="grid sm:grid-cols-3 gap-4 mt-2">
          <div class="stat bg-base-200 rounded-box p-4">
            <div class="stat-title">My Quizzes</div>
            <div class="stat-value text-primary text-2xl">—</div>
          </div>
          <div class="stat bg-base-200 rounded-box p-4">
            <div class="stat-title">Attempts</div>
            <div class="stat-value text-secondary text-2xl">—</div>
          </div>
          <div class="stat bg-base-200 rounded-box p-4">
            <div class="stat-title">Avg Score</div>
            <div class="stat-value text-accent text-2xl">—</div>
          </div>
        </div>
        <h3 class="font-semibold mt-4">My Quizzes Table</h3>
        <p class="text-sm">Click "Edit" to modify, "Delete" to remove, or the title to view.</p>
      </div>
    </section>

    <section id="creating" class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">Creating a Quiz</h2>
        <h3 class="font-semibold mt-4">Step 1: Create the Quiz</h3>
        <ol class="list-decimal list-inside text-sm space-y-1">
          <li>Click <strong>"Create Quiz"</strong> in the navigation bar.</li>
          <li>Enter a title (required) and description (optional).</li>
          <li>Click <strong>"Create Quiz"</strong>.</li>
        </ol>
        <h3 class="font-semibold mt-4">Step 2: Add Questions</h3>
        <ol class="list-decimal list-inside text-sm mt-2 space-y-1">
          <li>Enter the question text.</li>
          <li>Select the type (Single, Multi, or True/False).</li>
          <li>Optionally select a category.</li>
          <li>Fill in options and click letter buttons to mark correct answers.</li>
          <li>Click <strong>"Add Question"</strong>.</li>
        </ol>
        <div class="alert alert-info mt-4">
          <span class="text-sm">For Multi Select, click multiple letter buttons to mark several correct answers.</span>
        </div>
      </div>
    </section>

    <section id="editing" class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">Editing a Quiz</h2>
        <h3 class="font-semibold mt-4">Accessing the Edit Page</h3>
        <ul class="list-disc list-inside text-sm space-y-1">
          <li>From Dashboard, click <strong>"Edit"</strong> next to your quiz.</li>
          <li>Or navigate to <code>/quizzes/{'{id}'}/edit</code> directly.</li>
        </ul>
        <h3 class="font-semibold mt-4">Updating Quiz Details</h3>
        <p class="text-sm">Modify title or description, then click <strong>"Save Changes"</strong>. A toast confirms the save.</p>
        <h3 class="font-semibold mt-4">Managing Questions</h3>
        <ul class="list-disc list-inside text-sm mt-2 space-y-1">
          <li><strong>Add:</strong> Use the form at the bottom.</li>
          <li><strong>Delete:</strong> Click "Delete" and confirm in the modal.</li>
        </ul>
      </div>
    </section>

    <section id="themes" class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">Themes</h2>
        <p>Click the theme button in the navigation bar to cycle through themes.</p>
        <div class="grid sm:grid-cols-3 gap-4 mt-4">
          <div class="card bg-base-200 border border-base-300">
            <div class="card-body p-4 text-center">
              <span class="text-3xl">🌙</span>
              <h3 class="font-semibold">Dark</h3>
              <p class="text-xs text-base-content/60">Default. Easy on the eyes.</p>
            </div>
          </div>
          <div class="card bg-base-200 border border-base-300">
            <div class="card-body p-4 text-center">
              <span class="text-3xl">☀️</span>
              <h3 class="font-semibold">Light</h3>
              <p class="text-xs text-base-content/60">Clean and bright.</p>
            </div>
          </div>
          <div class="card bg-base-200 border border-base-300">
            <div class="card-body p-4 text-center">
              <span class="text-3xl">🌟</span>
              <h3 class="font-semibold">Night</h3>
              <p class="text-xs text-base-content/60">Deep blue ultra-dark.</p>
            </div>
          </div>
        </div>
        <p class="text-sm mt-4">Your choice persists across sessions.</p>
      </div>
    </section>

    <section id="faq" class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl">FAQ</h2>
        <div class="space-y-4 mt-4">
          {#each faqItems as item}
            <div class="collapse collapse-arrow bg-base-200">
              <input type="checkbox" />
              <div class="collapse-title font-medium">{item.q}</div>
              <div class="collapse-content">
                <p class="text-sm">{item.a}</p>
              </div>
            </div>
          {/each}
        </div>
      </div>
    </section>
  </main>
</div>
