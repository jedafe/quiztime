import { createApi } from '$lib/api';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
  const api = createApi(fetch);
  const result = await api.listQuizzes();
  return { quizzes: result.items, total: result.total, totalPages: result.total_pages };
};
