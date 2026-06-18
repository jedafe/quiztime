import { writable } from 'svelte/store';
import { browser } from '$app/environment';

type Theme = 'cerberus' | 'modern';

function createThemeStore() {
  let initial: Theme = 'cerberus';
  if (browser) {
    try {
      const stored = localStorage.getItem('theme') as Theme | null;
      if (stored === 'cerberus' || stored === 'modern') {
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
      let current: Theme = 'cerberus';
      subscribe((v) => (current = v))();
      const next: Theme = current === 'cerberus' ? 'modern' : 'cerberus';
      if (browser) {
        localStorage.setItem('theme', next);
        document.documentElement.setAttribute('data-theme', next);
        document.documentElement.style.colorScheme = next === 'cerberus' ? 'dark' : 'light';
      }
      set(next);
    },
    init: () => {
      let current: Theme = 'cerberus';
      subscribe((v) => (current = v))();
      if (browser) {
        document.documentElement.setAttribute('data-theme', current);
        document.documentElement.style.colorScheme = current === 'cerberus' ? 'dark' : 'light';
      }
    },
  };
}

export const theme = createThemeStore();
