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

    listQuizzes: (page = 1, pageSize = 100) =>
      request<{ items: any[]; total: number; page: number; page_size: number; total_pages: number }>(
        fetchFn, `/quizzes?page=${page}&page_size=${pageSize}`
      ),

    getQuiz: (id: string) => request<any>(fetchFn, `/quizzes/${id}`),

    createQuiz: (data: { title: string; description?: string }) =>
      request<any>(fetchFn, '/quizzes', { method: 'POST', body: JSON.stringify(data) }),

    updateQuiz: (id: string, data: { title?: string; description?: string }) =>
      request<any>(fetchFn, `/quizzes/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

    deleteQuiz: (id: string) =>
      request<void>(fetchFn, `/quizzes/${id}`, { method: 'DELETE' }),

    getQuizManage: (id: string) => request<any>(fetchFn, `/quizzes/${id}/manage`),

    getQuizTake: (id: string) => request<any>(fetchFn, `/quizzes/${id}/take`),

    createQuestion: (quizId: string, data: any) =>
      request<any>(fetchFn, `/questions/${quizId}`, { method: 'POST', body: JSON.stringify(data) }),

    updateQuestion: (id: string, data: any) =>
      request<any>(fetchFn, `/questions/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

    deleteQuestion: (id: string) =>
      request<void>(fetchFn, `/questions/${id}`, { method: 'DELETE' }),

    listCategories: () => request<any[]>(fetchFn, '/categories'),

    createCategory: (data: { name: string }) =>
      request<any>(fetchFn, '/categories', { method: 'POST', body: JSON.stringify(data) }),

    submitAttempt: (data: { quiz_id: string; answers: Record<string, number[]>; time_spent: number }) =>
      request<any>(fetchFn, '/attempts', { method: 'POST', body: JSON.stringify(data) }),

    myAttempts: () => request<any[]>(fetchFn, '/attempts/mine'),

    getAttempt: (id: string) => request<any>(fetchFn, `/attempts/${id}`),

    quizStats: (quizId: string) => request<any>(fetchFn, `/attempts/quiz/${quizId}/stats`),
  };
}

export type Api = ReturnType<typeof buildApi>;

export const api: Api = buildApi(globalThis.fetch);

export function createApi(fetchFn: FetchFn): Api {
  return buildApi(fetchFn);
}
