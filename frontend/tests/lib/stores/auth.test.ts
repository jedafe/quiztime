import { describe, it, expect, beforeEach, vi } from 'vitest';

describe('Auth Store', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.resetModules();
  });

  it('has null token initially', async () => {
    const { auth } = await import('$lib/stores/auth');
    let value: any;
    auth.subscribe((s) => (value = s))();
    expect(value.token).toBeNull();
    expect(value.user).toBeNull();
  });

  it('login stores token and user', async () => {
    const { auth } = await import('$lib/stores/auth');
    const user = { id: '1', username: 'test', email: 't@t.com', role: 'user' };
    auth.login('fake-jwt', user);

    let value: any;
    auth.subscribe((s) => (value = s))();
    expect(value.token).toBe('fake-jwt');
    expect(value.user).toEqual(user);
    expect(JSON.parse(localStorage.getItem('auth')!)).toEqual({ token: 'fake-jwt', user });
  });

  it('logout clears state', async () => {
    const { auth } = await import('$lib/stores/auth');
    auth.login('token', { id: '1', username: 'x', email: 'x@x.com', role: 'user' });
    auth.logout();

    let value: any;
    auth.subscribe((s) => (value = s))();
    expect(value.token).toBeNull();
    expect(value.user).toBeNull();
    expect(localStorage.getItem('auth')).toBeNull();
  });

  it('getToken returns current token', async () => {
    const { auth } = await import('$lib/stores/auth');
    expect(auth.getToken()).toBeNull();
    auth.login('abc', { id: '1', username: 'x', email: 'x@x.com', role: 'user' });
    expect(auth.getToken()).toBe('abc');
  });

  it('isLoggedIn derived is true when token set', async () => {
    const { auth, isLoggedIn } = await import('$lib/stores/auth');
    let val: boolean | undefined;
    isLoggedIn.subscribe((s) => (val = s))();
    expect(val).toBe(false);

    auth.login('tok', { id: '1', username: 'x', email: 'x@x.com', role: 'user' });
    isLoggedIn.subscribe((s) => (val = s))();
    expect(val).toBe(true);
  });

  it('isAdmin derived is true for admin role', async () => {
    const { auth, isAdmin } = await import('$lib/stores/auth');
    let val: boolean | undefined;
    isAdmin.subscribe((s) => (val = s))();
    expect(val).toBe(false);

    auth.login('tok', { id: '1', username: 'x', email: 'x@x.com', role: 'admin' });
    isAdmin.subscribe((s) => (val = s))();
    expect(val).toBe(true);
  });
});
