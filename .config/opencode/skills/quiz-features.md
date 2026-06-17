# Quiz Feature Skill

## Overview
This skill covers the quiz-specific business logic in the QuizTime application.

## Quiz Data Model

### Question Types
| Type | Options | Answer Format | Input UI |
|------|---------|---------------|----------|
| `single` | 4 options | `[index]` (1 value) | Radio buttons |
| `multiple` | 4 options | `[i, j, ...]` (1+ values) | Checkboxes |
| `true-false` | 2 options (True/False) | `[0]` or `[1]` | Radio buttons |

### Scoring Rules
- **3 points per correct answer** (client display)
- **Server calculates actual score** as count of correct answers
- Grade thresholds: ≤40% Fail, ≤59% Pass, ≤69% Good, >69% Excellent

### Answer Validation
```python
# Backend: sorted comparison handles multi-select
user_answer = data.answers.get(str(q.id), [])
if sorted(user_answer) == sorted(q.answer):
    score += 1
```

## Quiz Player Flow

1. **Start**: Load quiz, shuffle questions (client-side optional)
2. **Timer**: Countdown from `totalQuestions * 30` seconds
3. **Per Question**:
   - Display question + options
   - User selects answer(s)
   - "Check" shows correct/wrong feedback
   - "Next" advances (auto-submits if not checked)
   - "Skip" increments skip counter
4. **Finish**: Time runs out OR all questions answered
5. **Submit**: Send answers to `POST /api/attempts`
6. **Results**: Show score, grade, time spent

## Quiz Creation Flow

1. Create quiz (title + description) → `POST /api/quizzes`
2. Add questions one by one → `POST /api/questions/{quizId}`
   - Select type → shows appropriate option inputs
   - Select category (optional)
   - Mark correct answer(s)
3. Questions saved server-side immediately

## Key Files

| File | Responsibility |
|------|---------------|
| `backend/app/routes/attempts.py` | Submit answers, calculate score |
| `backend/app/routes/quizzes.py` | Quiz CRUD + permissions |
| `backend/app/routes/questions.py` | Question CRUD |
| `frontend/src/routes/quizzes/[id]/take/+page.svelte` | Quiz player UI |
| `frontend/src/routes/quizzes/[id]/results/+page.svelte` | Results display |
| `frontend/src/routes/quizzes/[id]/edit/+page.svelte` | Quiz manager |

## Permissions

| Action | Who |
|--------|-----|
| Take any quiz | Any logged-in user |
| Create quiz | Any logged-in user |
| Edit/delete quiz | Owner or admin |
| Create category | Admin only |
| View quiz stats | Public |
| View answers | Owner via `/manage` endpoint |
