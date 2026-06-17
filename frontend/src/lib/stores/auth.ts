import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

interface User {
  id: string;
  username: string;
  email: string;
  role: string;
}

function createAuthStore() {
  let initial = { token: null as string | null, user: null as User | null };

  if (browser) {
    try {
      const stored = localStorage.getItem('auth');
      if (stored) {
        initial = JSON.parse(stored);
      }
    } catch {
      localStorage.removeItem('auth');
    }
  }

  const { subscribe, set, update } = writable<{ token: string | null; user: User | null }>(initial);

  return {
    subscribe,
    login: (token: string, user: User) => {
      const data = { token, user };
      if (browser) localStorage.setItem('auth', JSON.stringify(data));
      set(data);
    },
    logout: () => {
      if (browser) localStorage.removeItem('auth');
      set({ token: null, user: null });
    },
    getToken: () => {
      let val: { token: string | null } = { token: null };
      subscribe((s) => (val = s))();
      return val.token;
    },
  };
}

export const auth = createAuthStore();
export const isLoggedIn = derived(auth, ($auth) => !!$auth.token);
export const currentUser = derived(auth, ($auth) => $auth.user);
export const isAdmin = derived(auth, ($auth) => $auth.user?.role === 'admin');
