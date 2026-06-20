import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import en from '$lib/i18n/en';
import es from '$lib/i18n/es';
import fr from '$lib/i18n/fr';

type DeepRecord = { [key: string]: string | DeepRecord };

const translations: Record<string, DeepRecord> = { en, es, fr };

export type SupportedLocale = 'en' | 'es' | 'fr';
export const locales: { code: SupportedLocale; label: string; native: string }[] = [
  { code: 'en', label: 'English', native: 'English' },
  { code: 'es', label: 'Spanish', native: 'Español' },
  { code: 'fr', label: 'French', native: 'Français' },
];

function getInitialLocale(): SupportedLocale {
  if (browser) {
    try {
      const stored = localStorage.getItem('locale');
      if (stored && ['en', 'es', 'fr'].includes(stored)) return stored as SupportedLocale;
      const lang = navigator.language?.split('-')[0];
      if (lang && ['en', 'es', 'fr'].includes(lang)) return lang as SupportedLocale;
    } catch {
      // ignore
    }
  }
  return 'en';
}

function createLocaleStore() {
  const { subscribe, set, update } = writable<SupportedLocale>(getInitialLocale());

  return {
    subscribe,
    set: (locale: SupportedLocale) => {
      if (browser) localStorage.setItem('locale', locale);
      set(locale);
    },
  };
}

export const locale = createLocaleStore();

function resolve(obj: DeepRecord, path: string, params?: Record<string, any>): string {
  const keys = path.split('.');
  let current: any = obj;
  for (const key of keys) {
    if (current && typeof current === 'object' && key in current) {
      current = current[key];
    } else {
      return path;
    }
  }
  let result = typeof current === 'string' ? current : path;
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      result = result.replace(new RegExp(`\\{${key}\\}`, 'g'), String(value));
    }
  }
  return result;
}

export function t(path: string, locale: SupportedLocale = 'en', params?: Record<string, any>): string {
  const lang = translations[locale] || translations.en;
  return resolve(lang, path, params);
}

export function createT(locale: SupportedLocale) {
  return (path: string, params?: Record<string, any>) => t(path, locale, params);
}

export const translate = derived(locale, ($locale) => (path: string, params?: Record<string, any>) => t(path, $locale, params));

export function setHtmlLang(lang: SupportedLocale) {
  if (browser) {
    document.documentElement.lang = lang;
  }
}
