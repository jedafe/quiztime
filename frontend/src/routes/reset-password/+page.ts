import { createApi } from '$lib/api';

export const load = async ({ url, fetch }) => {
  const token = url.searchParams.get('token') || '';
  return { token };
};
