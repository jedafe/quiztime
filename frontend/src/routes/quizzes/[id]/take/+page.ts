import { createApi } from '$lib/api';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, params }) => {
  const api = createApi(fetch);
  try {
    const quiz = await api.getQuizTake(params.id);
    return { quiz };
  } catch {
    const quiz = await api.getQuiz(params.id);
    return { quiz, needsAuth: true };
  }
};
