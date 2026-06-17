import { writable } from 'svelte/store';
import { browser } from '$app/environment';

type Theme = 'dark' | 'light' | 'night';

function createThemeStore() {
  let initial: Theme = 'dark';
  if (browser) {
    try {
      const stored = localStorage.getItem('theme') as Theme | null;
      if (stored && ['dark', 'light', 'night'].includes(stored)) {
        initial = stored;
      }
    } catch {
      // ignore
    }
  }

  const { subscribe, set } = writable<Theme>(initial);

  return {
    subscribe,
    toggle: () => {
      let current: Theme = 'dark';
      subscribe((v) => (current = v))();
      const next: Theme = current === 'dark' ? 'light' : current === 'light' ? 'night' : 'dark';
      if (browser) localStorage.setItem('theme', next);
      if (browser) document.documentElement.setAttribute('data-theme', next);
      set(next);
    },
    init: () => {
      let current: Theme = 'dark';
      subscribe((v) => (current = v))();
      if (browser) document.documentElement.setAttribute('data-theme', current);
    },
  };
}

export const theme = createThemeStore();
