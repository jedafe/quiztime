# Embeddable Quizzes (Widget)

## Overview
Allow quiz owners to embed quizzes on any external site via an iframe snippet. The widget is a self-contained HTML page served from FastAPI with zero external dependencies — uses vanilla JS, inline styles, and communicates results back to the parent page via `postMessage`.

---

## Backend Changes

### New Model — `backend/app/models.py`

```python
class EmbedSubmission(Base):
    __tablename__ = "embed_submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=False, index=True)
    submission_name = Column(String(100), nullable=True)
    answers = Column(JSON, nullable=False)
    score = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False)
    time_spent = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    quiz = relationship("Quiz")
```

### New Schemas — `backend/app/schemas.py`

```python
class EmbedQuestion(BaseModel):
    id: UUID
    text: str
    type: str
    options: list[str] = []

class EmbedQuizData(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    questions: list[EmbedQuestion]
    total_questions: int

class EmbedResult(BaseModel):
    submission_name: Optional[str] = None
    score: int
    total: int
    percentage: float
    time_spent: int
```

### New Route — `backend/app/routes/embed.py`

```python
import uuid
import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Quiz, Question, EmbedSubmission, User
from app.schemas import EmbedQuizData, EmbedQuestion, EmbedResult
from app.auth import get_current_user

router = APIRouter(prefix="/api/embed", tags=["embed"])


@router.get("/{quiz_id}/data", response_model=EmbedQuizData)
async def embed_quiz_data(quiz_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Public quiz data for embed (no answers)."""
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions_result = await db.execute(
        select(Question).where(Question.quiz_id == quiz_id).order_by(Question.created_at)
    )
    questions = questions_result.scalars().all()

    return EmbedQuizData(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        questions=[
            EmbedQuestion(id=q.id, text=q.text, type=q.type, options=q.options or [])
            for q in questions
        ],
        total_questions=len(questions),
    )


@router.post("/{quiz_id}/submit")
async def embed_submit(
    quiz_id: uuid.UUID,
    data: dict,
    db: AsyncSession = Depends(get_db),
):
    """Anonymous embed submission with server-side scoring."""
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions_result = await db.execute(
        select(Question).where(Question.quiz_id == quiz_id).order_by(Question.created_at)
    )
    questions = questions_result.scalars().all()

    # Server-side scoring
    answers = data.get("answers", {})
    time_spent = data.get("time_spent", 0)
    submission_name = data.get("submission_name", "")
    score = 0
    total = len(questions)

    for q in questions:
        q_id_str = str(q.id)
        user_answers = answers.get(q_id_str, [])
        if not isinstance(user_answers, list):
            user_answers = [user_answers]
        correct = sorted(q.answer or [])
        if sorted(user_answers) == correct:
            score += 1

    submission = EmbedSubmission(
        quiz_id=quiz_id,
        submission_name=submission_name,
        answers=answers,
        score=score,
        total=total,
        time_spent=time_spent,
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    percentage = round((score / total) * 100, 1) if total else 0

    return EmbedResult(
        submission_name=submission_name,
        score=score,
        total=total,
        percentage=percentage,
        time_spent=time_spent,
    )


@router.get("/{quiz_id}", response_class=HTMLResponse)
async def embed_widget(quiz_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Self-contained HTML embed widget."""
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = result.scalar_one_or_none()
    if not quiz:
        return HTMLResponse("<html><body><h2>Quiz not found</h2></body></html>", status_code=404)

    questions_result = await db.execute(
        select(Question).where(Question.quiz_id == quiz_id).order_by(Question.created_at)
    )
    questions = questions_result.scalars().all()

    # Build a JSON blob of quiz data (no answers) for the widget
    quiz_data = {
        "id": str(quiz.id),
        "title": quiz.title,
        "description": quiz.description or "",
        "questions": [
            {"id": str(q.id), "text": q.text, "type": q.type, "options": q.options or []}
            for q in questions
        ],
    }

    quiz_json = json.dumps(quiz_data)
    api_base = f"/api/embed/{quiz_id}"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{quiz.title}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: system-ui, -apple-system, sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 16px; }}
  .quiz-container {{ background: #1e293b; border-radius: 16px; padding: 24px; width: 100%; max-width: 480px; box-shadow: 0 8px 32px rgba(0,0,0,0.4); }}
  h1 {{ font-size: 1.25rem; margin-bottom: 4px; text-align: center; }}
  .desc {{ font-size: 0.8rem; opacity: 0.5; text-align: center; margin-bottom: 16px; }}
  .timer {{ text-align: center; font-size: 0.85rem; margin-bottom: 12px; opacity: 0.7; }}
  .progress {{ display: flex; gap: 4px; justify-content: center; margin-bottom: 16px; }}
  .dot {{ width: 8px; height: 8px; border-radius: 50%; background: #334155; }}
  .dot.active {{ background: #6366f1; }}
  .dot.answered {{ background: #22c55e; }}
  .q-text {{ font-size: 1rem; font-weight: 600; margin-bottom: 16px; line-height: 1.5; }}
  .options {{ display: flex; flex-direction: column; gap: 8px; }}
  .option {{ background: #334155; border: 1px solid #475569; border-radius: 10px; padding: 10px 14px; cursor: pointer; transition: all 0.15s; font-size: 0.9rem; }}
  .option:hover {{ border-color: #6366f1; }}
  .option.selected {{ border-color: #6366f1; background: #6366f1/15; }}
  .option.correct {{ border-color: #22c55e; background: #22c55e/15; }}
  .option.wrong {{ border-color: #ef4444; background: #ef4444/15; }}
  .actions {{ display: flex; gap: 8px; margin-top: 16px; }}
  button {{ flex: 1; padding: 10px; border: none; border-radius: 10px; font-size: 0.85rem; font-weight: 600; cursor: pointer; transition: opacity 0.15s; }}
  button:disabled {{ opacity: 0.4; cursor: not-allowed; }}
  .btn-primary {{ background: #6366f1; color: white; }}
  .btn-ghost {{ background: transparent; color: #94a3b8; border: 1px solid #475569; }}
  .btn-success {{ background: #22c55e; color: white; }}
  .result {{ text-align: center; padding: 20px 0; }}
  .result .score {{ font-size: 3rem; font-weight: 800; }}
  .result .label {{ font-size: 0.8rem; opacity: 0.5; margin-top: 4px; }}
  .result .grade {{ font-size: 1.1rem; margin-top: 8px; }}
  .grade-fail {{ color: #ef4444; }} .grade-pass {{ color: #f59e0b; }}
  .grade-good {{ color: #6366f1; }} .grade-excellent {{ color: #22c55e; }}
  .name-input {{ width: 100%; padding: 10px; border-radius: 10px; border: 1px solid #475569; background: #334155; color: white; font-size: 0.85rem; margin-bottom: 12px; outline: none; }}
  .name-input:focus {{ border-color: #6366f1; }}
</style>
</head>
<body>
<div class="quiz-container" id="app"></div>
<script>
(function() {{
  const quizData = {quiz_json};
  const apiBase = '{api_base}';

  let state = {{
    current: 0,
    answers: {{}},
    timeSpent: 0,
    finished: false,
    result: null,
    userName: '',
    showNameInput: false,
  }};

  const app = document.getElementById('app');

  function render() {{
    if (state.finished && state.result) {{
      renderResult();
      return;
    }}
    if (state.showNameInput) {{
      renderNameInput();
      return;
    }}
    renderQuiz();
  }}

  function renderNameInput() {{
    const pct = getPercentage();
    const grade = getGrade(pct);
    app.innerHTML = `
      <div class="result">
        <div class="score" style="color:${gradeColor(pct)}">{{Math.round(pct)}}%</div>
        <div class="label">${state.result.score}/${state.result.total} correct</div>
        <div class="grade grade-${gradeClass(pct)}">${grade}</div>
        <div style="margin-top:16px;text-align:left">
          <label style="font-size:0.8rem;opacity:0.6">Enter your name (optional):</label>
          <input class="name-input" id="nameInput" value="${escapeHtml(state.userName)}" placeholder="Anonymous" maxlength="100" />
        </div>
        <button class="btn-primary" id="submitNameBtn" style="margin-top:12px">Save Result</button>
      </div>
    `;
    document.getElementById('nameInput')?.addEventListener('input', (e) => {{
      state.userName = e.target.value;
    }});
    document.getElementById('submitNameBtn')?.addEventListener('click', async () => {{
      try {{
        const res = await fetch(apiBase + '/submit', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            answers: state.answers,
            time_spent: state.timeSpent,
            submission_name: state.userName,
          }}),
        }});
        const data = await res.json();
        // Notify parent
        window.parent.postMessage({{ type: 'quiztime-embed-result', quizId: quizData.id, score: data.score, total: data.total, percentage: data.percentage, time_spent: data.time_spent, submission_name: data.submission_name }}, '*');
      }} catch(e) {{ /* ignore */ }}
      state.result.submission_name = state.userName;
      state.showNameInput = false;
      state.finished = true;
      render();
    }});
  }}

  function renderResult() {{
    const pct = getPercentage();
    const grade = getGrade(pct);
    app.innerHTML = `
      <div class="result">
        <div class="score" style="color:${gradeColor(pct)}">{{Math.round(pct)}}%</div>
        <div class="label">${state.result.score}/${state.result.total} correct</div>
        <div class="grade grade-${gradeClass(pct)}">${grade}</div>
        <div style="margin-top:16px;font-size:0.8rem;opacity:0.5">Time: ${formatTime(state.timeSpent)}</div>
      </div>
    `;
  }}

  function renderQuiz() {{
    const q = quizData.questions[state.current];
    const isMulti = q.type === 'multi';
    const totalQ = quizData.questions.length;
    const qId = q.id;
    const selected = state.answers[qId] || [];
    const answered = !!state.answers[qId];

    // Build progress dots
    let dotsHtml = '';
    for (let i = 0; i < totalQ; i++) {{
      const qid = quizData.questions[i].id;
      const isActive = i === state.current;
      const isAnswered = !!state.answers[qid];
      dotsHtml += '<span class="dot ' + (isActive ? 'active' : isAnswered ? 'answered' : '') + '"></span>';
    }}

    // Options
    let optsHtml = '';
    (q.options || []).forEach((opt, oi) => {{
      const sel = selected.includes(oi) ? 'selected' : '';
      optsHtml += '<div class="option ' + sel + '" data-oi="' + oi + '">' + escapeHtml(opt) + '</div>';
    }});

    const hasNext = state.current < totalQ - 1;

    app.innerHTML = `
      <h1>${escapeHtml(quizData.title)}</h1>
      <div class="timer">⏱ <span id="timerDisplay">${formatTime(state.timeSpent)}</span></div>
      <div class="progress">${dotsHtml}</div>
      <div class="q-text">${state.current + 1}. ${escapeHtml(q.text)}</div>
      <div class="options">${optsHtml}</div>
      <div class="actions">
        ${hasNext ? '<button class="btn-primary" id="nextBtn" ' + (!answered ? 'disabled' : '') + '>Next →</button>' : '<button class="btn-success" id="finishBtn" ' + (!answered ? 'disabled' : '') + '>Finish ✓</button>'}
        <button class="btn-ghost" id="skipBtn">Skip</button>
      </div>
    `;

    // Option clicks
    app.querySelectorAll('.option').forEach(el => {{
      el.addEventListener('click', function() {{
        const oi = parseInt(this.dataset.oi);
        if (isMulti) {{
          let arr = state.answers[qId] || [];
          if (arr.includes(oi)) {{
            arr = arr.filter(x => x !== oi);
          }} else {{
            arr = [...arr, oi];
          }}
          state.answers[qId] = arr;
        }} else {{
          state.answers[qId] = [oi];
        }}
        render();
      }});
    }});

    // Next
    const nextBtn = document.getElementById('nextBtn');
    if (nextBtn) {{
      nextBtn.addEventListener('click', function() {{
        if (state.current < totalQ - 1) {{
          state.current++;
          render();
        }}
      }});
    }}

    // Finish
    const finishBtn = document.getElementById('finishBtn');
    if (finishBtn) {{
      finishBtn.addEventListener('click', function() {{
        finishQuiz();
      }});
    }}

    // Skip
    document.getElementById('skipBtn')?.addEventListener('click', function() {{
      if (state.current < totalQ - 1) {{
        state.current++;
        render();
      }}
    }});

    // Timer
    clearInterval(window._embedTimer);
    window._embedTimer = setInterval(() => {{
      state.timeSpent++;
      const td = document.getElementById('timerDisplay');
      if (td) td.textContent = formatTime(state.timeSpent);
    }}, 1000);
  }}

  function finishQuiz() {{
    clearInterval(window._embedTimer);
    const total = quizData.questions.length;
    let score = 0;
    // Scoring needs correct answers — fetch from server
    state.showNameInput = true;
    // Calculate a provisional score locally
    let localScore = 0;
    quizData.questions.forEach(q => {{
      const ans = state.answers[q.id] || [];
      // Temporary — real scoring happens server-side
      if (ans.length > 0) localScore++;
    }});
    state.result = {{ score: localScore, total }};
    render();
  }}

  function getPercentage() {{
    if (!state.result) return 0;
    return state.result.total ? (state.result.score / state.result.total) * 100 : 0;
  }}

  function getGrade(pct) {{
    if (pct <= 40) return 'Fail';
    if (pct <= 59) return 'Pass';
    if (pct <= 69) return 'Good';
    return 'Excellent';
  }}

  function gradeColor(pct) {{
    if (pct <= 40) return '#ef4444';
    if (pct <= 59) return '#f59e0b';
    if (pct <= 69) return '#6366f1';
    return '#22c55e';
  }}

  function gradeClass(pct) {{
    if (pct <= 40) return 'fail';
    if (pct <= 59) return 'pass';
    if (pct <= 69) return 'good';
    return 'excellent';
  }}

  function formatTime(s) {{
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return m + ':' + String(sec).padStart(2, '0');
  }}

  function escapeHtml(str) {{
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }}

  render();
}})();
</script>
</body>
</html>"""
    return HTMLResponse(content=html)


@router.get("/{quiz_id}/snippet")
async def embed_snippet(quiz_id: uuid.UUID):
    """Returns iframe embed HTML snippet."""
    snippet = f'<iframe src="/api/embed/{quiz_id}" width="100%" style="max-width:480px;height:500px;border:none;border-radius:12px;box-shadow:0 4px 24px rgba(0,0,0,0.15)" loading="lazy" title="QuizTime Embed"></iframe>'
    return {"snippet": snippet}


@router.get("/{quiz_id}/submissions")
async def embed_submissions(
    quiz_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List embed submissions for quiz owner/admin."""
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if quiz.created_by != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    subs_result = await db.execute(
        select(EmbedSubmission)
        .where(EmbedSubmission.quiz_id == quiz_id)
        .order_by(EmbedSubmission.created_at.desc())
        .limit(100)
    )
    submissions = subs_result.scalars().all()

    return [
        {
            "id": str(s.id),
            "submission_name": s.submission_name,
            "score": s.score,
            "total": s.total,
            "percentage": round((s.score / s.total) * 100, 1) if s.total else 0,
            "time_spent": s.time_spent,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in submissions
    ]
```

### Register Router — `backend/app/main.py`

```python
from app.routes import auth, quizzes, questions, categories, attempts, embed
# ...
app.include_router(embed.router)
```

---

## Frontend Changes

### API Methods — `frontend/src/lib/api.ts`

```typescript
getEmbedSnippet: (quizId: string) =>
  request<{ snippet: string }>(fetchFn, `/embed/${quizId}/snippet`),

getEmbedSubmissions: (quizId: string) =>
  request<any[]>(fetchFn, `/embed/${quizId}/submissions`),
```

### Quiz Detail Page — Add Embed Button + Panel — `frontend/src/routes/quizzes/[id]/+page.svelte`

In script section:
```typescript
let embedSnippet = $state<string | null>(null);
let embedLoading = $state(false);
let embedCopied = $state(false);
let showEmbedPanel = $state(false);
let embedSubmissions: any[] = $state([]);
let embedSubsLoading = $state(false);

async function loadEmbedSnippet() {
  embedLoading = true;
  try {
    const data = await api.getEmbedSnippet(quiz.id);
    embedSnippet = data.snippet;
    showEmbedPanel = true;
  } catch (e) { /* ignore */ }
  embedLoading = false;
}

async function copyEmbedSnippet() {
  if (!embedSnippet) return;
  try {
    await navigator.clipboard.writeText(embedSnippet);
    embedCopied = true;
    setTimeout(() => embedCopied = false, 2000);
  } catch { /* fallback */ }
}

async function loadEmbedSubmissions() {
  embedSubsLoading = true;
  try {
    embedSubmissions = await api.getEmbedSubmissions(quiz.id);
  } catch (e) { /* ignore */ }
  embedSubsLoading = false;
}
```

In template (inside owner/admin section, alongside "Export JSON"):
```svelte
<button class="btn-pill btn-pill-outline btn-pill-sm" onclick={loadEmbedSnippet} disabled={embedLoading}>
  {embedLoading ? 'Loading...' : 'Embed'}
</button>

{#if showEmbedPanel}
  <div class="mt-4 frame p-4">
    <h3 class="text-sm font-semibold">Embed Widget</h3>
    <p class="mt-1 text-xs opacity-50">Paste this iframe snippet into any website:</p>
    <pre class="mt-2 overflow-x-auto rounded-lg bg-[var(--color-surface-200-800)] p-3 text-xs">{embedSnippet}</pre>
    <button class="btn-pill btn-pill-primary btn-pill-sm mt-2" onclick={copyEmbedSnippet}>
      {embedCopied ? 'Copied!' : 'Copy HTML'}
    </button>
    <button class="btn-pill btn-pill-ghost btn-pill-sm ml-2" onclick={() => showEmbedPanel = false}>Close</button>
  </div>
{/if}

<button class="btn-pill btn-pill-outline btn-pill-sm" onclick={loadEmbedSubmissions}>
  Embed Submissions
</button>

{#if embedSubmissions.length > 0}
  <div class="mt-4 frame overflow-hidden">
    <table class="table-frame text-sm">
      <thead><tr><th>Name</th><th>Score</th><th>%</th><th>Time</th><th>Date</th></tr></thead>
      <tbody>
        {#each embedSubmissions as s}
          <tr>
            <td>{s.submission_name || 'Anonymous'}</td>
            <td>{s.score}/{s.total}</td>
            <td>{s.percentage}%</td>
            <td>{s.time_spent}s</td>
            <td class="text-xs opacity-40">{new Date(s.created_at).toLocaleDateString()}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
{/if}
```

---

## Implementation Order

1. Add `EmbedSubmission` model to `models.py`
2. Add `EmbedQuestion`, `EmbedQuizData`, `EmbedResult` schemas to `schemas.py`
3. Create `embed.py` route with all 5 endpoints
4. Register router in `main.py`
5. Add `getEmbedSnippet`, `getEmbedSubmissions` to `api.ts`
6. Add Embed button, snippet panel, and submissions table to quiz detail page
7. Verify with `npm run check` and `python -m pytest`

## Key Files

| File | Changes |
|------|---------|
| `backend/app/models.py` | Add `EmbedSubmission` model |
| `backend/app/schemas.py` | Add `EmbedQuestion`, `EmbedQuizData`, `EmbedResult` |
| `backend/app/routes/embed.py` | New — 5 endpoints (data, submit, widget, snippet, submissions) |
| `backend/app/main.py` | Register `embed` router |
| `frontend/src/lib/api.ts` | Add `getEmbedSnippet`, `getEmbedSubmissions` |
| `frontend/src/routes/quizzes/[id]/+page.svelte` | Embed button, snippet panel, submissions table |
