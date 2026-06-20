import { createApi } from '$lib/api';

export const load = async ({ fetch }) => {
  const api = createApi(fetch);
  const [badges, profile] = await Promise.all([
    api.getAllBadges().catch(() => []),
    api.getMyProfile().catch(() => null),
  ]);
  return { badges, profile };
};
