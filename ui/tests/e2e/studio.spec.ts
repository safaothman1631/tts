import { test, expect } from '@playwright/test';

test('app renders the Studio', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: /TTS Studio/i })).toBeVisible();
  await expect(page.getByPlaceholder(/Type or paste/i)).toBeVisible();
});

test('opens command palette with ⌘K', async ({ page }) => {
  await page.goto('/');
  await page.keyboard.press('ControlOrMeta+k');
  await expect(page.getByPlaceholder(/Search/i)).toBeVisible();
});

test('degraded mode disables synth in Studio', async ({ page }) => {
  await page.route('**/api/v1/health', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ status: 'down' }),
    });
  });

  await page.goto('/');
  await page.getByLabel('TTS input').fill('Test sentence for degraded mode.');

  const synthButton = page.getByRole('button', { name: /synthesize/i });
  await expect(synthButton).toBeDisabled();
  await expect(page.getByText(/Backend unavailable/i)).toBeVisible();
  await expect(page.getByText(/Start API on port 8765/i)).toBeVisible();
});

test('degraded mode disables preview in Voices', async ({ page }) => {
  await page.route('**/api/v1/health', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ status: 'down' }),
    });
  });

  await page.route('**/api/v1/voices', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 'demo-voice-1',
          name: 'Demo Voice',
          gender: 'neutral',
          language: 'en',
          backend: 'local',
          tags: [],
          custom: false,
        },
      ]),
    });
  });

  await page.goto('/voices');
  await expect(page.getByText('Demo Voice')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Preview', exact: true })).toBeDisabled();
});

test('VoiceLab route remains accessible when backend is down', async ({ page }) => {
  await page.route('**/api/v1/health', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ status: 'down' }),
    });
  });

  await page.goto('/voice-lab');
  await expect(page.getByRole('button', { name: /next/i })).toBeVisible();
});
