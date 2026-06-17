# AGENTS.md

## Project Structure

This is a multi-version quiz application (quiz-v1 through quiz-v6). Each version is a **standalone, self-contained HTML/CSS/JS project** with no build system.

- `quiz-v1` through `quiz-v6`: Independent quiz implementations (v6 is most feature-complete)
- `randomize-or-shuffle-array`: Standalone utility for shuffling arrays
- Root `package.json`: Only defines dependencies (Tailwind CSS, DaisyUI) — no scripts

## Running

Open any version directly in a browser:
```
open quiz-v6/index.html
```
No build step required. Tailwind CSS is pre-compiled (tailwind.css files in each directory).

## Key Technical Details

- **Styling**: Tailwind CSS + DaisyUI plugin (configured in root `tailwind.config.js`)
- **Data persistence**: Quiz questions stored in `localStorage` under key `questionBank`
- **Quiz types**: Single-select, multi-select, and true/false (v6 only)
- **Scoring**: 3 points per correct answer; grading thresholds: ≤40% Fail, ≤59% Pass, ≤69% Good, >69% Excellent

## Version Differences

- v1: Basic single-select only, simpler question format (a/b/c/d properties)
- v6: Adds quiz creation form, multiple question types, category selection, modal support

## Gotchas

- No tests, linter, or formatter configured
- `node_modules/` not installed (run `npm install` if you need Tailwind CLI)
- Each version has its own copy of Tailwind CSS — changes to root `tailwind.config.js` won't affect existing versions without recompilation
