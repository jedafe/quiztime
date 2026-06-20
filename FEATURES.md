# Feature Roadmap — QuizTime

All planned features are implemented. This document serves as a feature reference.

---

## Tier 1 — Viral Growth & Sharing

### 1. Share & Challenge System
**Status**: ✅ Implemented

After finishing a quiz, users can:
- Share results as a link with rich OG preview (inline SVG score card)
- Copy link, share to X/Twitter, or WhatsApp
- **Challenge a friend**: generate a unique link where the friend takes the same quiz and tries to beat the posted score
- Head-to-head comparison page showing winner
- Dashboard section listing all sent/received challenges

### 2. Public Per-Quiz Leaderboard
**Status**: ✅ Implemented

- Top 20 scores per quiz with username, score, percentage, time, date
- Period filters: Today / This Week / This Month / All Time
- Top 3 with 🥇🥈🥉 styling
- Current user highlighted and shown even if outside top 20
- Tab switcher on quiz detail page (Stats | Leaderboard)
- Rank badge on results page

---

## Tier 2 — Discovery & Social Proof

### 3. Quiz Search, Filtering & Sorting
**Status**: ✅ Implemented

- Search bar on browse page (search by title, description)
- Category/tag filtering
- Sort by: newest, popular (most attempts), highest rated
- Pagination controls

### 4. Quiz Ratings & Reviews
**Status**: ✅ Implemented

- 5-star rating system per quiz
- Optional written review
- Average rating shown on quiz cards and detail page
- Sort browse page by highest-rated

---

## Tier 3 — Retention & Engagement

### 5. Gamification (XP, Levels, Badges)
**Status**: ✅ Implemented

- XP from creating/completing quizzes, perfect scores, streaks
- Levels (linear: level = floor(xp / 100) + 1)
- 6 badges: "First Quiz", "Perfect Score", "Quiz Creator", "Streak 3", "Streak 7", "Streak 30"
- Daily streak tracking with streak-based badges
- Dedicated Achievements page (`/achievements`) with badges grid, XP history, progress bar
- Dashboard profile card showing XP, level, streak, and earned badges
- Leaderboard endpoint ranking users by total XP

### 6. Email System
**Status**: ✅ Implemented

- Email verification on registration (verify link with 48h expiry)
- Resend verification email endpoint
- Password reset flow (forgot-password sends link, reset-password with 1h expiry)
- Frontend pages: `/verify-email`, `/forgot-password`, `/reset-password`
- Fire-and-forget email sending (registration doesn't block on SMTP failure)

---

## Tier 4 — Distribution & Content Portability

### 7. Embeddable Quizzes (Widget)
**Status**: ✅ Implemented

- Generate an iframe embed snippet
- Users embed quizzes on their own websites, blogs, or Notion pages
- Results optionally sent back to the quiz creator
- Free distribution channel via backlinks
- Backend: `GET /api/embed/{id}` serves self-contained widget, `POST /api/embed/{id}/submit` for anonymous scoring, `EmbedSubmission` model tracks results
- Frontend: "Embed" button on quiz detail page shows iframe snippet with copy

### 8. Quiz Import/Export (JSON)
**Status**: ✅ Implemented

- Export any quiz as a downloadable JSON file (owner/admin)
- Import JSON to create a new quiz (including questions)
- Enables content migration, backup, and sharing outside the platform
- Backend: `GET /api/quizzes/{id}/export` and `POST /api/quizzes/import`
- Frontend: "Export JSON" button on quiz detail page, "Import JSON" tab on create page

---

## Tier 5 — Platform Maturity

### 9. Multi-Language / i18n
**Status**: ✅ Implemented

- Language switcher in navbar (🇬🇧 EN / 🇪🇸 ES / 🇫🇷 FR)
- 3 locale files (~450 lines each, 22 namespace sections): English, Spanish, French
- All 20 frontend pages fully translated via `$translate()` derived store
- Lightweight writable+derived i18n store (no external library)
- Template parameter support: `{$translate('key', {name: val})}`
- Locale persisted in localStorage
- Quiz content language tagging (`language` column on Quiz model)

### 10. Admin Dashboard
**Status**: ✅ Implemented

- 8-tab admin interface at `/admin`: Overview, Users, Quizzes, Creators, Categories, Subcategories, Badge Definitions, All Attempts
- Site-wide stats: total users, quizzes, attempts, DAU
- User management: list, role change, delete
- Quiz management: list all quizzes site-wide, force-delete
- Creators leaderboard: top quiz creators by count
- Category/Subcategory CRUD with inline forms
- Badge definition CRUD
- All attempts table with pagination and user/quiz filters
- Backend: 17 admin CRUD endpoints under `/api/admin/` (all protected by `require_admin`)

---

## Implementation Notes

- Features are designed to be built incrementally, starting with Tier 1
- All 10 feature tiers are now fully implemented
- See `AGENTS.md` for the system architecture reference
- All new DB models require `alembic revision --autogenerate -m "description"` for migrations
