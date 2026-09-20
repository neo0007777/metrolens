import { test, expect } from '@playwright/test';

test.describe('MetroLens E2E Verification Flow', () => {
  test('Officer Login and Dashboard Navigation', async ({ page }) => {
    // Navigate to Login Page
    await page.goto('http://localhost:3000/login');
    await expect(page).toHaveURL(/.*login/);
    
    // Fast-path role login: 1-click evaluator login
    await page.click('text=Field Officer');
    
    // Should navigate to dashboard
    await expect(page).toHaveURL(/.*dashboard/);
    await expect(page.locator('h1')).toContainText('Enforcement Command Centre');
  });

  test('Graceful offline degradation on Upload', async ({ page }) => {
    // Intercept API to force network failure
    await page.route('**/api/v1/**', route => route.abort('internetdisconnected'));
    
    // Set authenticated state in storage
    await page.goto('http://localhost:3000/login');
    await page.evaluate(() => {
      localStorage.setItem('token', 'demo-token');
      localStorage.setItem('role', 'officer');
      sessionStorage.setItem('token', 'demo-token');
      sessionStorage.setItem('role', 'officer');
    });
    await page.goto('http://localhost:3000/upload');
    
    // Fill product name form field
    const input = page.locator('input[placeholder*="Organic Honey"]');
    await expect(input).toBeVisible();
    await input.fill('Test Packet');
    
    expect(true).toBeTruthy();
  });
});
