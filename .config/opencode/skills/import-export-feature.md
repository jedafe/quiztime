# Quiz Import/Export (JSON)

## Overview
Allow quiz owners to export their quizzes (with answers) as downloadable JSON files, and import JSON files to create new quizzes. Enables content migration, backup, and sharing outside the platform.

---

## Backend Changes

### New Schemas — `backend/app/schemas.py`

```python
class QuestionExport(BaseModel):
    text: str
    type: str
    options: list[str]
    answer: list[int]

class QuizExport(BaseModel):
    title: str
    description: Optional[str] = None
    category_name: Optional[str] = None
    questions: list[QuestionExport]

class QuestionImport(BaseModel):
    text: str
    type: str = "single"
    options: list[str] = []
    answer: list[int] = []

class QuizImport(BaseModel):
    title: str
    description: Optional[str] = None
    category_name: Optional[str] = None
    questions: list[QuestionImport] = []
```

### Export Endpoint — Add to `backend/app/routes/quizzes.py`

```python
from fastapi.responses import JSONResponse

@router.get("/{quiz_id}/export")
async def export_quiz(
    quiz_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Export quiz as downloadable JSON (owner/admin only)."""
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if quiz.created_by != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Only the owner can export")

    questions_result = await db.execute(
        select(Question).where(Question.quiz_id == quiz_id).order_by(Question.created_at)
    )
    questions = questions_result.scalars().all()

    # Resolve category name
    category_name = None
    if quiz.category_id:
        cat_result = await db.execute(select(Category).where(Category.id == quiz.category_id))
        category = cat_result.scalar_one_or_none()
        if category:
            category_name = category.name

    export_data = QuizExport(
        title=quiz.title,
        description=quiz.description,
        category_name=category_name,
        questions=[
            QuestionExport(
                text=q.text,
                type=q.type,
                options=q.options or [],
                answer=q.answer or [],
            )
            for q in questions
        ],
    )

    return JSONResponse(
        content=export_data.model_dump(),
        headers={"Content-Disposition": f'attachment; filename="{quiz.title}.json"'},
    )
```

### Import Endpoint — Add to `backend/app/routes/quizzes.py`

```python
@router.post("/import", response_model=QuizResponse, status_code=201)
async def import_quiz(
    data: QuizImport,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Import a quiz from JSON data."""
    # Resolve category by name
    category_id = None
    if data.category_name:
        cat_result = await db.execute(
            select(Category).where(Category.name == data.category_name)
        )
        category = cat_result.scalar_one_or_none()
        if category:
            category_id = category.id
        # If category not found, silently skip (quiz won't have a category)

    quiz = Quiz(
        title=data.title,
        description=data.description or "",
        category_id=category_id,
        created_by=user.id,
    )
    db.add(quiz)
    await db.flush()

    for qi in data.questions:
        question = Question(
            quiz_id=quiz.id,
            text=qi.text,
            type=qi.type,
            options=qi.options or [],
            answer=qi.answer or [],
        )
        db.add(question)

    # Award XP for creating quiz + questions
    from app.models import XpEvent
    xp_amount = 10 + min(len(data.questions) * 5, 50)
    xp_event = XpEvent(user_id=user.id, source="import_quiz", amount=xp_amount)
    db.add(xp_event)

    await db.commit()
    await db.refresh(quiz)

    return QuizResponse(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        category_id=quiz.category_id,
        created_by=quiz.created_by,
        created_at=quiz.created_at,
        updated_at=quiz.updated_at,
    )
```

---

## Frontend Changes

### API Methods — `frontend/src/lib/api.ts`

```typescript
exportQuiz: (quizId: string) =>
  request<any>(fetchFn, `/quizzes/${quizId}/export`),

importQuiz: (data: { title: string; description?: string; category_name?: string; questions: Array<{ text: string; type: string; options: string[]; answer: number[] }> }) =>
  request<any>(fetchFn, '/quizzes/import', { method: 'POST', body: JSON.stringify(data) }),
```

### Quiz Detail Page — Add Export Button — `frontend/src/routes/quizzes/[id]/+page.svelte`

In script section:
```typescript
async function exportQuizJson() {
  try {
    const data = await api.exportQuiz(quiz.id);
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${quiz.title}.json`;
    a.click();
    URL.revokeObjectURL(url);
  } catch (e) { /* ignore */ }
}
```

Add button (inside owner/admin section):
```svelte
<button class="btn-pill btn-pill-outline btn-pill-sm" onclick={exportQuizJson}>
  Export JSON
</button>
```

### Create Page — Add Import Tab — `frontend/src/routes/create/+page.svelte`

Add tab state:
```typescript
let importTab = $state(false);
```

Add the import UI alongside the create form:
```svelte
<div class="mb-6 flex gap-2">
  <button class="btn-pill btn-pill-sm" class:btn-pill-primary={!importTab} class:btn-pill-ghost={importTab} onclick={() => importTab = false}>
    Create Manually
  </button>
  <button class="btn-pill btn-pill-sm" class:btn-pill-primary={importTab} class:btn-pill-ghost={!importTab} onclick={() => importTab = true}>
    Import JSON
  </button>
</div>

{#if importTab}
  <div class="frame p-6">
    <h2 class="mb-4 text-lg font-bold">Import Quiz from JSON</h2>
    <div class="mb-4 rounded-lg bg-[var(--color-info-500)]/15 p-3 text-sm">
      <strong>Format:</strong> Upload a JSON file with the following structure:
      <pre class="mt-2 overflow-x-auto rounded bg-[var(--color-surface-200-800)] p-2 text-xs">
{<!-- -->{
  "title": "My Quiz",
  "description": "Optional description",
  "category_name": "Science",
  "questions": [
    {
      "text": "What is 2+2?",
      "type": "single",
      "options": ["3", "4", "5"],
      "answer": [1]
    }
  ]
}<!-- -->}</pre>
    </div>
    <input
      type="file"
      accept=".json"
      onchange={handleImportFile}
      class="block w-full text-sm file:mr-3 file:rounded-lg file:border-0 file:bg-[var(--color-primary-500)] file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-white"
    />
    {#if importError}
      <p class="mt-2 text-sm text-[var(--color-error-500)]">{importError}</p>
    {/if}
    {#if importData}
      <div class="mt-4">
        <p class="text-sm"><strong>Quiz:</strong> {importData.title}</p>
        <p class="text-sm opacity-60">{importData.questions.length} question(s)</p>
        <button class="btn-pill btn-pill-primary mt-3" onclick={submitImport} disabled={importing}>
          {importing ? 'Importing...' : 'Import Quiz'}
        </button>
      </div>
    {/if}
  </div>
{/if}
```

Add import logic in script:
```typescript
let importData: any = $state(null);
let importError = $state('');
let importing = $state(false);

function handleImportFile(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (!file) return;
  importError = '';
  importData = null;
  const reader = new FileReader();
  reader.onload = async (ev) => {
    try {
      const json = JSON.parse(ev.target?.result as string);
      if (!json.title || !json.questions) {
        importError = 'Invalid format: missing "title" or "questions"';
        return;
      }
      importData = json;
    } catch {
      importError = 'Invalid JSON file';
    }
  };
  reader.readAsText(file);
}

async function submitImport() {
  if (!importData || importing) return;
  importing = true;
  importError = '';
  try {
    const result = await api.importQuiz(importData);
    goto(`/quizzes/${result.id}/edit`);
  } catch (e: any) {
    importError = e.message || 'Import failed';
  }
  importing = false;
}
```

---

## Implementation Order

1. Add `QuizExport`, `QuestionExport`, `QuizImport`, `QuestionImport` schemas to `schemas.py`
2. Add `GET /api/quizzes/{id}/export` endpoint to `quizzes.py`
3. Add `POST /api/quizzes/import` endpoint to `quizzes.py`
4. Add `exportQuiz`, `importQuiz` to `api.ts`
5. Add "Export JSON" button to quiz detail page
6. Add import tab to quiz create page
7. Verify with `npm run check` and `python -m pytest`

## Key Files

| File | Changes |
|------|---------|
| `backend/app/schemas.py` | Add `QuizExport`, `QuestionExport`, `QuizImport`, `QuestionImport` |
| `backend/app/routes/quizzes.py` | Add export + import endpoints |
| `frontend/src/lib/api.ts` | Add `exportQuiz`, `importQuiz` |
| `frontend/src/routes/quizzes/[id]/+page.svelte` | Export JSON button |
| `frontend/src/routes/create/+page.svelte` | Import JSON tab |
