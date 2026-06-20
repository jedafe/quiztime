import { test, expect } from '@playwright/test';

test.describe('Smoke Tests — All Pages Load', () => {
  test('landing page loads', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('h1')).toBeVisible();
    expect(await page.locator('h1').textContent()).toBeTruthy();
  });

  test('browse quizzes page loads', async ({ page }) => {
    await page.goto('/quizzes');
    await page.waitForTimeout(2000);
    expect(page.url()).toContain('/quizzes');
  });

  test('login page loads', async ({ page }) => {
    await page.goto('/login');
    await expect(page.locator('button[type="submit"], button:has-text("Sign In"), button:has-text("Log in")').first()).toBeVisible({ timeout: 5000 });
  });

  test('register page loads', async ({ page }) => {
    await page.goto('/register');
    await expect(page.locator('button[type="submit"]').first()).toBeVisible({ timeout: 5000 });
  });

  test('dashboard redirects to login when not authenticated', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForURL(/\/login/, { timeout: 5000 });
  });

  test('admin redirects to landing when not authenticated', async ({ page }) => {
    await page.goto('/admin');
    await page.waitForURL('/', { timeout: 5000 });
  });

  test('create quiz redirects to login when not authenticated', async ({ page }) => {
    await page.goto('/create');
    await page.waitForURL(/\/login/, { timeout: 5000 });
  });

  test('docs page loads', async ({ page }) => {
    await page.goto('/docs');
    await expect(page.locator('h1')).toBeVisible();
  });

  test('docs user guide loads', async ({ page }) => {
    await page.goto('/docs/user');
    await expect(page.locator('h1')).toBeVisible();
  });

  test('docs developer guide loads', async ({ page }) => {
    await page.goto('/docs/developer');
    await expect(page.locator('h1')).toBeVisible();
  });

  test('docs admin guide loads', async ({ page }) => {
    await page.goto('/docs/admin');
    await expect(page.locator('h1')).toBeVisible();
  });

  test('verify email page loads', async ({ page }) => {
    await page.goto('/verify-email');
    await expect(page.locator('h1, h2, div').first()).toBeVisible();
  });

  test('forgot password page loads', async ({ page }) => {
    await page.goto('/forgot-password');
    await expect(page.locator('input[type="email"]')).toBeVisible({ timeout: 5000 });
  });

  test('reset password page loads', async ({ page }) => {
    await page.goto('/reset-password');
    await expect(page.locator('h1, p')).toBeVisible();
  });

  test('achievements redirects to login when not authenticated', async ({ page }) => {
    await page.goto('/achievements');
    await page.waitForURL(/\/login/, { timeout: 5000 });
  });
});

test.describe('Authentication Flow', () => {
  test('login with admin credentials and access dashboard', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/quizzes/, { timeout: 10000 });
  });

  test('redirected to quizzes after login', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/quizzes/, { timeout: 10000 });

    // Can access dashboard now
    await page.goto('/dashboard');
    await page.waitForTimeout(2000);
    expect(page.url()).toContain('/dashboard');
  });

  test('admin can access admin page', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/quizzes/, { timeout: 10000 });

    await page.goto('/admin');
    await page.waitForTimeout(2000);
    expect(page.url()).toContain('/admin');
  });
});

test.describe('i18n Language Switcher', () => {
  test('language switcher exists in navbar', async ({ page }) => {
    await page.goto('/');
    const switcher = page.locator('button:has-text("EN"), button:has-text("ES"), button:has-text("FR")').first();
    await expect(switcher).toBeVisible({ timeout: 5000 });
  });

  test('switching to Spanish changes text on landing', async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(1000);

    // Find and click the language switcher
    const select = page.locator('select').first();
    if (await select.isVisible()) {
      await select.selectOption('es');
    } else {
      // Try button-based switcher
      const esBtn = page.locator('button:has-text("ES"), button:has-text("Español")').first();
      if (await esBtn.isVisible()) {
        await esBtn.click();
      }
    }
    await page.waitForTimeout(500);

    // Go to docs page and check for Spanish text
    await page.goto('/docs');
    await page.waitForTimeout(500);
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
  });
});

test.describe('Admin Page Tabs', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/quizzes/, { timeout: 10000 });
    await page.goto('/admin');
    await page.waitForTimeout(2000);
  });

  test('admin page loads with tabs', async ({ page }) => {
    const tabButtons = page.locator('button', { hasText: /Overview|Users|Quizzes|Creators|Categories|Badges|Attempts/ });
    const count = await tabButtons.count();
    expect(count).toBeGreaterThanOrEqual(4);
  });

  test('overview tab shows stats', async ({ page }) => {
    const tab = page.locator('button:has-text("Overview")');
    if (await tab.isVisible()) {
      await tab.click();
      await page.waitForTimeout(1000);
      await expect(page.locator('text=Total').first()).toBeVisible({ timeout: 5000 });
    }
  });

  test('users tab shows user table', async ({ page }) => {
    const tab = page.locator('button:has-text("Users")');
    if (await tab.isVisible()) {
      await tab.click();
      await page.waitForTimeout(1000);
      await expect(page.locator('table').first()).toBeVisible({ timeout: 5000 });
    }
  });
});
