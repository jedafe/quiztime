import { createApi } from '$lib/api';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, params, url }) => {
  const api = createApi(fetch);
  const quiz = await api.getQuiz(params.id);
  return { quiz };
};
