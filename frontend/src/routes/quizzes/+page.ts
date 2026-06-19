import { createApi } from '$lib/api';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, url }) => {
  const api = createApi(fetch);
  const result = await api.listQuizzes({
    page: 1,
    pageSize: 20,
    search: url.searchParams.get('search') || undefined,
    category_id: url.searchParams.get('category_id') || undefined,
    sort_by: url.searchParams.get('sort_by') || 'newest',
  });
  return { quizzes: result.items, total: result.total, totalPages: result.total_pages };
};
