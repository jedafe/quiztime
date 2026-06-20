import { createApi } from '$lib/api';

export const load = async ({ url, fetch }) => {
  const token = url.searchParams.get('token') || '';
  const api = createApi(fetch);
  let message = '';
  let error = '';
  if (token) {
    try {
      const r = await api.verifyEmail(token);
      message = r.message || 'Email verified!';
    } catch (e: any) {
      error = e.message || 'Verification failed.';
    }
  }
  return { token, message, error };
};
