import { auth } from './stores/auth';
import { goto } from '$app/navigation';
import { browser } from '$app/environment';

const BASE = '/api';

type FetchFn = typeof globalThis.fetch;

async function request<T>(fetchFn: FetchFn, path: string, options: RequestInit = {}): Promise<T> {
  let token: string | null = null;
  if (browser) {
    auth.subscribe((s) => (token = s.token))();
  }

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((options.headers as Record<string, string>) || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetchFn(`${BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    if (browser) {
      auth.logout();
      goto('/login');
    }
    throw new Error('Unauthorized');
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(err.detail || 'Request failed');
  }

  if (res.status === 204) return null as T;
  return res.json();
}

function buildApi(fetchFn: FetchFn) {
  return {
    register: (data: { username: string; email: string; password: string }) =>
      request<{ access_token: string; user: any }>(fetchFn, '/auth/register', {
        method: 'POST',
        body: JSON.stringify(data),
      }),

    login: (data: { username: string; password: string }) =>
      request<{ access_token: string; user: any }>(fetchFn, '/auth/login', {
        method: 'POST',
        body: JSON.stringify(data),
      }),

    me: () => request<any>(fetchFn, '/auth/me'),

    listQuizzes: (params?: { page?: number; pageSize?: number; search?: string; category_id?: string; sort_by?: string; sort_order?: string }) => {
      const p = params || {};
      const q = new URLSearchParams();
      q.set('page', String(p.page || 1));
      q.set('page_size', String(p.pageSize || 20));
      if (p.search) q.set('search', p.search);
      if (p.category_id) q.set('category_id', p.category_id);
      if (p.sort_by) q.set('sort_by', p.sort_by);
      if (p.sort_order) q.set('sort_order', p.sort_order);
      return request<{ items: any[]; total: number; page: number; page_size: number; total_pages: number }>(
        fetchFn, `/quizzes?${q.toString()}`
      );
    },

    getQuiz: (id: string) => request<any>(fetchFn, `/quizzes/${id}`),

    createQuiz: (data: { title: string; description?: string; category_id?: string | null }) =>
      request<any>(fetchFn, '/quizzes', { method: 'POST', body: JSON.stringify(data) }),

    updateQuiz: (id: string, data: { title?: string; description?: string; category_id?: string | null }) =>
      request<any>(fetchFn, `/quizzes/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

    deleteQuiz: (id: string) =>
      request<void>(fetchFn, `/quizzes/${id}`, { method: 'DELETE' }),

    exportQuiz: (id: string) =>
      request<any>(fetchFn, `/quizzes/${id}/export`),

    importQuiz: (data: { title: string; description?: string; category_name?: string | null; questions: any[] }) =>
      request<any>(fetchFn, '/quizzes/import', { method: 'POST', body: JSON.stringify(data) }),

    getQuizManage: (id: string) => request<any>(fetchFn, `/quizzes/${id}/manage`),

    getQuizTake: (id: string) => request<any>(fetchFn, `/quizzes/${id}/take`),

    createQuestion: (quizId: string, data: any) =>
      request<any>(fetchFn, `/questions/${quizId}`, { method: 'POST', body: JSON.stringify(data) }),

    updateQuestion: (id: string, data: any) =>
      request<any>(fetchFn, `/questions/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

    deleteQuestion: (id: string) =>
      request<void>(fetchFn, `/questions/${id}`, { method: 'DELETE' }),

    listCategories: () => request<any[]>(fetchFn, '/categories'),
    listSubcategories: (categoryId: string) =>
      request<any[]>(fetchFn, `/categories/subcategories?category_id=${categoryId}`),

    createCategory: (data: { name: string }) =>
      request<any>(fetchFn, '/categories', { method: 'POST', body: JSON.stringify(data) }),

    submitAttempt: (data: { quiz_id: string; answers: Record<string, number[]>; time_spent: number; challenge_code?: string }) =>
      request<any>(fetchFn, '/attempts', { method: 'POST', body: JSON.stringify(data) }),

    myAttempts: () => request<any[]>(fetchFn, '/attempts/mine'),

    getAttempt: (id: string) => request<any>(fetchFn, `/attempts/${id}`),

    quizStats: (quizId: string) => request<any>(fetchFn, `/attempts/quiz/${quizId}/stats`),

    // ── Share ──────────────────────────────────────────
    createShareLink: (data: { quiz_id: string; attempt_id: string }) =>
      request<{ code: string; share_url: string; og_url: string }>(fetchFn, '/share', {
        method: 'POST', body: JSON.stringify(data),
      }),

    getShareLink: (code: string) =>
      request<any>(fetchFn, `/share/${code}`),

    // ── Challenge ──────────────────────────────────────
    createChallenge: (data: { quiz_id: string; score_to_beat: number; total_questions: number; challenger_attempt_id: string }) =>
      request<any>(fetchFn, '/challenges', { method: 'POST', body: JSON.stringify(data) }),

    getChallenge: (code: string) =>
      request<any>(fetchFn, `/challenges/${code}`),

    acceptChallenge: (code: string) =>
      request<any>(fetchFn, `/challenges/${code}/accept`, { method: 'POST' }),

    getChallengeResult: (code: string) =>
      request<any>(fetchFn, `/challenges/${code}/result`),

    myChallenges: () =>
      request<any[]>(fetchFn, '/challenges'),

    // ── Leaderboard ────────────────────────────────────
    getLeaderboard: (quizId: string, limit = 20, period = 'all') =>
      request<any>(fetchFn, `/quizzes/${quizId}/leaderboard?limit=${limit}&period=${period}`),

    // ── Ratings & Reviews ──────────────────────────────
    createRating: (data: { quiz_id: string; score: number; review?: string }) =>
      request<any>(fetchFn, '/ratings', { method: 'POST', body: JSON.stringify(data) }),

    listRatings: (quizId: string, page = 1, pageSize = 20) =>
      request<{ items: any[]; total: number; page: number; page_size: number }>(
        fetchFn, `/ratings/${quizId}?page=${page}&page_size=${pageSize}`
      ),

    ratingStats: (quizId: string) =>
      request<any>(fetchFn, `/ratings/${quizId}/stats`),

    myRating: (quizId: string) =>
      request<any>(fetchFn, `/ratings/${quizId}/my`),

    deleteRating: (ratingId: string) =>
      request<void>(fetchFn, `/ratings/${ratingId}`, { method: 'DELETE' }),

    // ── Gamification ────────────────────────────────────
    getMyProfile: () =>
      request<any>(fetchFn, '/gamification/my-profile'),

    getUserProfile: (userId: string) =>
      request<any>(fetchFn, `/gamification/profile/${userId}`),

    getXpHistory: (page = 1, pageSize = 20) =>
      request<{ items: any[]; total: number }>(fetchFn, `/gamification/xp-history?page=${page}&page_size=${pageSize}`),

    getAllBadges: () =>
      request<any[]>(fetchFn, '/gamification/badges'),

    getXpLeaderboard: (limit = 50) =>
      request<any[]>(fetchFn, `/gamification/leaderboard?limit=${limit}`),

    // ── Email / Verification ────────────────────────────
    verifyEmail: (token: string) =>
      request<{ message: string }>(fetchFn, '/email/verify', {
        method: 'POST', body: JSON.stringify({ token }),
      }),

    resendVerification: () =>
      request<{ message: string }>(fetchFn, '/email/resend-verification', { method: 'POST' }),

    forgotPassword: (email: string) =>
      request<{ message: string }>(fetchFn, '/email/forgot-password', {
        method: 'POST', body: JSON.stringify({ email }),
      }),

    resetPassword: (token: string, newPassword: string) =>
      request<{ message: string }>(fetchFn, '/email/reset-password', {
        method: 'POST', body: JSON.stringify({ token, new_password: newPassword }),
      }),

    // ── Embed ────────────────────────────────────────────
    getEmbedSnippet: (quizId: string) =>
      request<{ embed_url: string; html: string; javascript: string }>(fetchFn, `/embed/${quizId}/snippet`),

    // ── Embed Submissions (for quiz owner) ───────────────
    getEmbedSubmissions: (quizId: string) =>
      request<any[]>(fetchFn, `/embed/${quizId}/submissions`),
  };
}

export type Api = ReturnType<typeof buildApi>;

export const api: Api = buildApi(globalThis.fetch);

export function createApi(fetchFn: FetchFn): Api {
  return buildApi(fetchFn);
}
