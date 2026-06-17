import '@testing-library/jest-dom';
import { vi } from 'vitest';

Object.defineProperty(globalThis, 'localStorage', {
  value: {
    store: {} as Record<string, string>,
    getItem(key: string) { return this.store[key] ?? null; },
    setItem(key: string, value: string) { this.store[key] = value; },
    removeItem(key: string) { delete this.store[key]; },
    clear() { this.store = {}; },
  },
});

vi.mock('$app/navigation', () => ({
  goto: vi.fn(),
}));

vi.mock('$app/environment', () => ({
  browser: true,
  dev: true,
  building: false,
  version: 'test',
}));

vi.mock('$app/stores', () => ({
  page: { subscribe: vi.fn() },
  navigating: { subscribe: vi.fn() },
  updated: { subscribe: vi.fn() },
}));
