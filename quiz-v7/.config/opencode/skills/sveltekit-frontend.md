# SvelteKit Frontend Skill

## Overview
This skill covers working with the SvelteKit frontend in `quiz-v7/frontend/`.

## Project Structure
```
frontend/
├── src/
│   ├── routes/             # SvelteKit file-based routing
│   │   ├── +layout.svelte  # Global nav + auth state
│   │   ├── +page.svelte    # Landing page
│   │   ├── +page.ts        # Load function for landing
│   │   ├── login/          # Login page
│   │   ├── register/       # Registration page
│   │   ├── quizzes/        # Browse quizzes
│   │   │   ├── [id]/       # Quiz detail
│   │   │   │   ├── take/   # Quiz player
│   │   │   │   ├── results/# Score display
│   │   │   │   └── edit/   # Manage questions
│   │   ├── dashboard/      # User dashboard
│   │   └── create/         # Create quiz form
│   ├── lib/
│   │   ├── api.ts          # API client (fetch wrapper)
│   │   └── stores/
│   │       └── auth.ts     # Auth store (JWT + user)
│   ├── app.html            # HTML template
│   └── app.css             # Tailwind imports
├── package.json
├── svelte.config.js
├── vite.config.ts          # Vite config + API proxy
└── tailwind.config.js
```

## Commands
```bash
npm run dev       # Dev server (port 5173)
npm run build     # Production build
npm run check     # TypeScript check
```

## Key Patterns

### API calls
Use the centralized API client (`$lib/api`):
```typescript
import { api } from '$lib/api';
const quizzes = await api.listQuizzes();
const quiz = await api.getQuiz(id);
```

### Auth state
```typescript
import { auth, isLoggedIn, currentUser, isAdmin } from '$lib/stores/auth';
auth.login(token, user);  // saves to localStorage
auth.logout();            // clears + redirects
```

### Page data loading
Each route can have a `+page.ts` that exports a `load` function:
```typescript
export const load: PageLoad = async ({ params }) => {
  const quiz = await api.getQuiz(params.id);
  return { quiz };
};
```

### Adding a new page
1. Create route directory: `src/routes/my-page/`
2. Add `+page.svelte` (component)
3. Optionally add `+page.ts` (data loading)
4. Add link in `+layout.svelte` nav if needed

### Component conventions
- Use DaisyUI component classes (`btn`, `card`, `alert`, etc.)
- Tailwind utility classes for layout (`flex`, `gap-4`, `grid`, etc.)
- Svelte reactive declarations with `$:` for derived state
- `{#if}` / `{#each}` for conditional/list rendering

## API Proxy
Vite proxies `/api/*` to `http://localhost:8000` in dev mode (configured in `vite.config.ts`).

## Auth Flow
1. User submits login form → `api.login()` → receives JWT
2. Token stored in `auth` store + localStorage
3. API client reads token from store for each request
4. On 401 response → auto-logout + redirect to `/login`
