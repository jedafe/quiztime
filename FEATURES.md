# Feature Roadmap — QuizTime

Planned features to drive wider adoption, organized by implementation priority.

---

## Tier 1 — Viral Growth & Sharing

### 1. Share & Challenge System
**Status**: Skill file ready → `.config/opencode/skills/share-challenge-feature.md`

After finishing a quiz, users can:
- Share results as a link with rich OG preview (inline SVG score card)
- Copy link, share to X/Twitter, or WhatsApp
- **Challenge a friend**: generate a unique link where the friend takes the same quiz and tries to beat the posted score
- Head-to-head comparison page showing winner
- Dashboard section listing all sent/received challenges

### 2. Public Per-Quiz Leaderboard
**Status**: Skill file ready → `.config/opencode/skills/leaderboard-feature.md`

- Top 20 scores per quiz with username, score, percentage, time, date
- Period filters: Today / This Week / This Month / All Time
- Top 3 with 🥇🥈🥉 styling
- Current user highlighted and shown even if outside top 20
- Tab switcher on quiz detail page (Stats | Leaderboard)
- Rank badge on results page

---

## Tier 2 — Discovery & Social Proof

### 3. Quiz Search, Filtering & Sorting
- Search bar on browse page (search by title, description)
- Category/tag filtering
- Sort by: newest, popular (most attempts), highest rated
- Proper pagination UI (currently uses `page_size=100` with no pagination controls)

### 4. Quiz Ratings & Reviews
- 5-star rating system per quiz
- Optional written review
- Average rating shown on quiz cards and detail page
- Sort browse page by highest-rated

---

## Tier 3 — Retention & Engagement

### 5. Gamification (XP, Levels, Badges)
- XP from creating/completing quizzes, perfect scores, streaks
- Levels that unlock cosmetic rewards or features
- Badges: "First Quiz", "Perfect Score", "Quiz Creator", "Streak Master", "Knowledge Seeker"
- Dedicated Achievements page
- Display badges on user profiles

### 6. Email System
- Email verification on registration (reduces spam bots)
- Password reset flow (reduces churn from forgotten passwords)
- Optional weekly digest ("Most popular quizzes this week")

---

## Tier 4 — Distribution & Content Portability

### 7. Embeddable Quizzes (Widget)
- Generate an iframe embed snippet
- Users embed quizzes on their own websites, blogs, or Notion pages
- Results optionally sent back to the quiz creator
- Free distribution channel via backlinks

### 8. Quiz Import/Export (JSON)
- Export any quiz as a downloadable JSON file
- Import JSON to create a new quiz (including questions)
- Enables content migration, backup, and sharing outside the platform

---

## Tier 5 — Platform Maturity

### 9. Multi-Language / i18n
- Language switcher in navbar
- Translated UI strings (start with Spanish + French)
- Quiz content language tagging so users find content in their language

### 10. Admin Dashboard
- Site-wide stats: total users, quizzes, attempts, DAU/WAU
- Top quizzes and creators
- User management table (ban, role change, view activity)
- Recent reports/moderations

---

## Implementation Notes

- Features are designed to be built incrementally, starting with Tier 1
- Each feature has a corresponding skill file in `.config/opencode/skills/` with detailed implementation plans
- See `AGENTS.md` for the system architecture reference
- All new DB models require `alembic revision --autogenerate -m "description"` for migrations
