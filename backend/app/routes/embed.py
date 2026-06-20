from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Quiz, Question, EmbedSubmission, User
from app.schemas import EmbedQuizData, EmbedQuestion, EmbedResult
from app.auth import get_current_user

router = APIRouter(prefix="/api/embed", tags=["embed"])


def grade(score: int, total: int) -> str:
    if total == 0:
        return "N/A"
    pct = score / total
    if pct >= 0.9:
        return "A"
    if pct >= 0.8:
        return "B"
    if pct >= 0.7:
        return "C"
    if pct >= 0.6:
        return "D"
    return "F"


@router.get("/{quiz_id}/data", response_model=EmbedQuizData)
async def embed_quiz_data(quiz_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    q_result = await db.execute(select(Question).where(Question.quiz_id == quiz_id))
    questions = q_result.scalars().all()

    return EmbedQuizData(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        questions=[
            EmbedQuestion(id=q.id, type=q.type, text=q.text, options=q.options)
            for q in questions
        ],
    )


@router.post("/{quiz_id}/submit", response_model=EmbedResult)
async def embed_submit(
    quiz_id: UUID,
    data: dict,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    q_result = await db.execute(select(Question).where(Question.quiz_id == quiz_id))
    questions = {str(q.id): q for q in q_result.scalars().all()}

    answers = data.get("answers", {})
    time_spent = data.get("time_spent", 0)
    name = data.get("name", "")

    score = 0
    total = len(questions)
    for qid, selected in answers.items():
        q = questions.get(qid)
        if q and set(selected) == set(q.answer):
            score += 1

    submission = EmbedSubmission(
        quiz_id=quiz_id,
        submission_name=name[:100] if name else "",
        answers=answers,
        score=score,
        total=total,
        time_spent=time_spent,
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    pct = round((score / total) * 100, 1) if total else 0

    return EmbedResult(
        score=score,
        total=total,
        percentage=pct,
        grade=grade(score, total),
        time_spent=time_spent,
        answers=answers,
        submission_id=submission.id,
    )


@router.get("/{quiz_id}/submissions")
async def embed_submissions(
    quiz_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if quiz.created_by != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    sub_result = await db.execute(
        select(EmbedSubmission)
        .where(EmbedSubmission.quiz_id == quiz_id)
        .order_by(EmbedSubmission.created_at.desc())
    )
    subs = sub_result.scalars().all()

    return [
        {
            "id": s.id,
            "submission_name": s.submission_name,
            "score": s.score,
            "total": s.total,
            "percentage": round((s.score / s.total) * 100, 1) if s.total else 0,
            "time_spent": s.time_spent,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in subs
    ]


WIDGET_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #f8f9fa;
    color: #1a1a2e;
    line-height: 1.5;
  }}
  .container {{ max-width: 600px; margin: 0 auto; padding: 16px; }}
  h1 {{ font-size: 1.25rem; margin-bottom: 4px; }}
  .desc {{ font-size: 0.875rem; color: #666; margin-bottom: 16px; }}
  .card {{
    background: #fff;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    margin-bottom: 12px;
  }}
  .q-text {{ font-size: 1rem; font-weight: 600; margin-bottom: 12px; }}
  .option {{
    display: block;
    width: 100%;
    text-align: left;
    padding: 10px 14px;
    margin-bottom: 6px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    background: #fff;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.15s;
  }}
  .option:hover {{ border-color: #6366f1; background: #f0f0ff; }}
  .option.selected {{ border-color: #6366f1; background: #eef2ff; }}
  .option.correct {{ border-color: #22c55e; background: #f0fdf4; }}
  .option.wrong {{ border-color: #ef4444; background: #fef2f2; }}
  .controls {{ display: flex; gap: 8px; margin-top: 16px; }}
  .btn {{
    padding: 10px 20px;
    border: none;
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
  }}
  .btn-primary {{ background: #6366f1; color: #fff; }}
  .btn-primary:hover {{ background: #4f46e5; }}
  .btn-primary:disabled {{ opacity: 0.5; cursor: not-allowed; }}
  .btn-ghost {{ background: transparent; color: #666; }}
  .btn-ghost:hover {{ background: #f0f0f0; }}
  .progress {{ display: flex; gap: 4px; margin-bottom: 16px; }}
  .dot {{
    width: 100%; height: 4px; border-radius: 2px;
    background: #e0e0e0; transition: background 0.2s;
  }}
  .dot.active {{ background: #6366f1; }}
  .dot.answered {{ background: #22c55e; }}
  .dot.skipped {{ background: #f59e0b; }}
  .result-card {{ text-align: center; padding: 32px 20px; }}
  .score-circle {{
    width: 120px; height: 120px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    margin: 16px auto; font-size: 2rem; font-weight: 700;
  }}
  .score-grade-a {{ background: #f0fdf4; color: #22c55e; }}
  .score-grade-b {{ background: #f0f9ff; color: #3b82f6; }}
  .score-grade-c {{ background: #fffbeb; color: #f59e0b; }}
  .score-grade-d {{ background: #fef2f2; color: #ef4444; }}
  .score-grade-f {{ background: #fef2f2; color: #dc2626; }}
  .score-detail {{ font-size: 0.875rem; color: #666; margin-top: 8px; }}
  .grade-label {{ font-size: 1.5rem; font-weight: 700; margin-top: 4px; }}
  .name-input {{
    width: 100%; padding: 10px 14px; border: 2px solid #e0e0e0;
    border-radius: 8px; font-size: 0.9rem; margin-bottom: 12px;
  }}
  .footer {{ text-align: center; margin-top: 16px; font-size: 0.75rem; color: #999; }}
  .feedback {{ font-size: 0.8rem; margin-top: 4px; }}
  .feedback-correct {{ color: #22c55e; }}
  .feedback-wrong {{ color: #ef4444; }}
  .hidden {{ display: none; }}
  .timer {{ font-size: 0.8rem; color: #666; text-align: right; margin-bottom: 8px; }}
  .timer-urgent {{ color: #ef4444; font-weight: 600; }}
</style>
</head>
<body>
<div class="container" id="app">
  <div id="loading" class="card" style="text-align:center;padding:40px 20px">
    <p>Loading quiz...</p>
  </div>
  <div id="quiz-view" class="hidden">
    <h1 id="q-title"></h1>
    <p class="desc" id="q-desc"></p>
    <div class="timer" id="timer"></div>
    <div class="progress" id="progress"></div>
    <div class="card">
      <div class="q-text" id="q-text"></div>
      <div id="options"></div>
      <div id="feedback" class="hidden"></div>
      <div class="controls">
        <button class="btn btn-ghost" id="skip-btn">Skip</button>
        <button class="btn btn-primary" id="next-btn" style="margin-left:auto">Next</button>
      </div>
    </div>
    <div class="hidden" id="name-section">
      <div class="card">
        <input type="text" id="name-input" class="name-input" placeholder="Your name (optional)" maxlength="100">
      </div>
    </div>
  </div>
  <div id="result-view" class="hidden">
    <div class="card result-card">
      <h1>Quiz Complete!</h1>
      <div class="score-circle" id="score-circle">
        <span id="score-pct"></span>
      </div>
      <div class="grade-label" id="grade-label"></div>
      <div class="score-detail" id="score-detail"></div>
    </div>
    <div class="footer">Powered by QuizTime</div>
  </div>
</div>
<script>
(function(){{
  const BASE = '{base}';
  const QUIZ_ID = '{quiz_id}';
  const quizDataUrl = BASE + '/api/embed/' + QUIZ_ID + '/data';
  const submitUrl = BASE + '/api/embed/' + QUIZ_ID + '/submit';

  let quiz, questions, currentIdx = 0, answers = {{}}, selection = [];
  let startTime, timerInterval;

  const $ = id => document.getElementById(id);

  async function load() {{
    try {{
      const res = await fetch(quizDataUrl);
      if (!res.ok) throw new Error('Failed to load');
      quiz = await res.json();
      questions = quiz.questions;
      if (!questions || questions.length === 0) {{
        $('loading').innerHTML = '<p>This quiz has no questions.</p>';
        return;
      }}
      $('loading').classList.add('hidden');
      $('quiz-view').classList.remove('hidden');
      renderProgress();
      showQuestion(0);
      startTimer();
    }} catch(e) {{
      $('loading').innerHTML = '<p>Failed to load quiz. Please try again.</p>';
    }}
  }}

  function startTimer() {{
    startTime = Date.now();
    timerInterval = setInterval(updateTimer, 1000);
    updateTimer();
  }}

  function updateTimer() {{
    const total = questions.length * 30;
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    const remaining = Math.max(0, total - elapsed);
    const m = Math.floor(remaining / 60);
    const s = remaining % 60;
    const el = $('timer');
    el.textContent = m + ':' + (s < 10 ? '0' : '') + s;
    el.className = 'timer' + (remaining < 60 ? ' timer-urgent' : '');
    if (remaining <= 0) submitQuiz();
  }}

  function renderProgress() {{
    $('progress').innerHTML = questions.map((_, i) =>
      '<div class="dot" id="dot-' + i + '"></div>'
    ).join('');
  }}

  function updateProgress() {{
    questions.forEach((_, i) => {{
      const dot = $('dot-' + i);
      dot.className = 'dot';
      if (i === currentIdx) dot.classList.add('active');
      else if (answers[questions[i].id] !== undefined) dot.classList.add('answered');
    }});
  }}

  function showQuestion(idx) {{
    currentIdx = idx;
    const q = questions[idx];
    $('q-title').textContent = quiz.title;
    $('q-desc').textContent = quiz.description;
    $('q-text').textContent = (idx + 1) + '. ' + q.text;
    $('feedback').classList.add('hidden');
    $('skip-btn').classList.remove('hidden');

    const prevAnswer = answers[q.id];
    selection = prevAnswer ? [...prevAnswer] : [];

    const optsEl = $('options');
    optsEl.innerHTML = q.options.map((opt, i) => {{
      const sel = prevAnswer && prevAnswer.includes(i) ? ' selected' : '';
      return '<button class="option' + sel + '" data-idx="' + i + '">' + opt + '</button>';
    }}).join('');

    optsEl.querySelectorAll('.option').forEach(btn => {{
      btn.addEventListener('click', () => {{
        if (q.type === 'multiple') {{
          btn.classList.toggle('selected');
          const idx = parseInt(btn.dataset.idx);
          const pos = selection.indexOf(idx);
          if (pos >= 0) selection.splice(pos, 1);
          else selection.push(idx);
        }} else {{
          optsEl.querySelectorAll('.option').forEach(b => b.classList.remove('selected'));
          btn.classList.add('selected');
          selection = [parseInt(btn.dataset.idx)];
        }}
      }});
    }});

    $('next-btn').textContent = idx === questions.length - 1 ? 'Submit' : 'Next';
    updateProgress();
  }}

  function handleNext() {{
    const q = questions[currentIdx];
    if (selection.length > 0) {{
      answers[q.id] = [...selection];
    }}

    if (currentIdx === questions.length - 1) {{
      submitQuiz();
    }} else {{
      showQuestion(currentIdx + 1);
    }}
  }}

  $('next-btn').addEventListener('click', handleNext);
  $('skip-btn').addEventListener('click', () => {{
    if (currentIdx < questions.length - 1) {{
      showQuestion(currentIdx + 1);
    }}
  }});

  async function submitQuiz() {{
    clearInterval(timerInterval);
    const timeSpent = Math.floor((Date.now() - startTime) / 1000);
    const el = $('name-input');
    const name = el ? el.value.trim() : '';

    $('quiz-view').classList.add('hidden');
    $('loading').classList.remove('hidden');
    $('loading').innerHTML = '<p>Submitting...</p>';

    try {{
      const res = await fetch(submitUrl, {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ answers, time_spent, name }})
      }});
      if (!res.ok) throw new Error('Submit failed');
      const result = await res.json();

      showResults(result);
    }} catch(e) {{
      $('loading').innerHTML = '<p>Submission failed. Please try again.</p>';
    }}
  }}

  function showResults(result) {{
    $('loading').classList.add('hidden');
    $('result-view').classList.remove('hidden');

    const pct = result.percentage;
    const grade = result.grade;
    const circle = $('score-circle');
    circle.className = 'score-circle score-grade-' + grade.toLowerCase();
    $('score-pct').textContent = pct + '%';
    $('grade-label').textContent = 'Grade: ' + grade;
    $('score-detail').textContent = result.score + ' / ' + result.total + ' correct';

    window.parent.postMessage({{
      type: 'quiztime-embed-result',
      quizId: QUIZ_ID,
      score: result.score,
      total: result.total,
      percentage: pct,
      grade: grade,
      timeSpent: result.time_spent,
      submissionId: result.submission_id,
    }}, '*');
  }}

  load();
}})();
</script>
</body>
</html>"""


@router.get("/{quiz_id}", response_class=HTMLResponse)
async def embed_widget(quiz_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    return HTMLResponse(
        WIDGET_HTML.format(
            title=quiz.title.replace("{", "{{").replace("}", "}}"),
            base="",
            quiz_id=quiz_id,
        )
    )


@router.get("/{quiz_id}/snippet")
async def embed_snippet(quiz_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    embed_url = f"/api/embed/{quiz_id}"
    html = f'<iframe src="{embed_url}" width="100%" height="500" frameborder="0" style="border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,0.1)"></iframe>'

    return {
        "embed_url": embed_url,
        "html": html,
        "javascript": f'<div id="quiztime-embed-{quiz_id}"></div>\n<script src="{embed_url}/loader.js" data-quiz="{quiz_id}"></script>',
    }
