import { describe, it, expect, vi, beforeEach } from 'vitest';

const mockFetch = vi.fn();
globalThis.fetch = mockFetch as any;

beforeEach(() => {
  localStorage.clear();
  mockFetch.mockReset();
});

async function loadApi() {
  vi.resetModules();
  return await import('$lib/api');
}

function jsonResponse(data: any, status = 200) {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(data),
  }) as any;
}

describe('API Client', () => {
  it('sends Authorization header when token exists', async () => {
    localStorage.setItem('auth', JSON.stringify({ token: 'test-jwt', user: null }));
    mockFetch.mockReturnValueOnce(jsonResponse([]));

    const { api } = await loadApi();
    await api.listQuizzes();

    expect(mockFetch).toHaveBeenCalledWith(
      '/api/quizzes?page=1&page_size=20',
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer test-jwt',
        }),
      }),
    );
  });

  it('does not send Authorization header when no token', async () => {
    mockFetch.mockReturnValueOnce(jsonResponse([]));

    const { api } = await loadApi();
    await api.listQuizzes();

    const sentHeaders = mockFetch.mock.calls[0][1].headers;
    expect(sentHeaders.Authorization).toBeUndefined();
  });

  it('login sends credentials', async () => {
    mockFetch.mockReturnValueOnce(jsonResponse({ access_token: 'jwt', user: { id: '1' } }));

    const { api } = await loadApi();
    await api.login({ username: 'admin', password: 'pass' });

    expect(mockFetch).toHaveBeenCalledWith(
      '/api/auth/login',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ username: 'admin', password: 'pass' }),
      }),
    );
  });

  it('throws error on non-ok response', async () => {
    mockFetch.mockReturnValueOnce(jsonResponse({ detail: 'Not found' }, 404));

    const { api } = await loadApi();
    await expect(api.getQuiz('bad-id')).rejects.toThrow('Not found');
  });

  it('listQuizzes returns array', async () => {
    const data = [{ id: '1', title: 'Quiz 1' }];
    mockFetch.mockReturnValueOnce(jsonResponse(data));

    const { api } = await loadApi();
    const result = await api.listQuizzes();
    expect(result).toEqual(data);
  });

  it('createQuiz sends POST with body', async () => {
    const quiz = { id: '2', title: 'New Quiz' };
    mockFetch.mockReturnValueOnce(jsonResponse(quiz));

    const { api } = await loadApi();
    const result = await api.createQuiz({ title: 'New Quiz', description: 'desc' });

    expect(result).toEqual(quiz);
    expect(mockFetch).toHaveBeenCalledWith(
      '/api/quizzes',
      expect.objectContaining({ method: 'POST' }),
    );
  });

  it('submitAttempt sends answers payload', async () => {
    const attempt = { id: 'a1', score: 2, total: 3 };
    mockFetch.mockReturnValueOnce(jsonResponse(attempt));

    const { api } = await loadApi();
    const result = await api.submitAttempt({
      quiz_id: 'q1',
      answers: { 'q1': [0], 'q2': [1, 2] },
      time_spent: 30,
    });

    expect(result).toEqual(attempt);
    const body = JSON.parse(mockFetch.mock.calls[0][1].body);
    expect(body.quiz_id).toBe('q1');
    expect(body.time_spent).toBe(30);
  });

  it('myAttempts sends GET to /attempts/mine', async () => {
    mockFetch.mockReturnValueOnce(jsonResponse([]));

    const { api } = await loadApi();
    await api.myAttempts();

    expect(mockFetch).toHaveBeenCalledWith(
      '/api/attempts/mine',
      expect.anything(),
    );
  });
});
