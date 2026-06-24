import { test, expect } from '@playwright/test';

test.describe('DementiaCare Coach E2E Tests', () => {
  test('should load application dashboard and switch patients', async ({ page }) => {
    // Navigate to local Vite dev server
    await page.goto('/');

    // 1. Verify main header title is loaded
    const headerTitle = page.locator('h1.logo-title');
    await expect(headerTitle).toContainText('DementiaCare Coach');

    // 2. Verify default patient selected in header is Maria
    const patientSelect = page.locator('header select');
    await expect(patientSelect).toHaveValue('Maria');

    // 3. Switch to Arthur in the dropdown
    await patientSelect.selectOption({ label: 'Arthur' });
    await expect(patientSelect).toHaveValue('Arthur');

    // 4. Verify caregiver role changes dynamically (no "Daughter" tag for Arthur)
    const roleLabel = page.locator('header strong').nth(0);
    await expect(roleLabel).toContainText('Primary Caregiver');
    await expect(roleLabel).not.toContainText('Daughter');

    // 5. Switch to Patient Profile tab and check profile details
    await page.click('nav button:has-text("Patient Profile")');
    const nameInput = page.locator('input[value="Arthur"]');
    await expect(nameInput).toBeVisible();

    const dementiaInput = page.locator('input[value*="Lewy Body"]');
    await expect(dementiaInput).toBeVisible();

    // 6. Switch back to Maria and verify changes reflect
    await page.click('nav button:has-text("Interaction Coach")');
    await patientSelect.selectOption({ label: 'Maria' });
    await expect(patientSelect).toHaveValue('Maria');
  });

  test('should open simulator and send a message', async ({ page }) => {
    await page.goto('/');

    // 1. Navigate to Simulator Tab
    await page.click('nav button:has-text("Care Simulator")');

    // 2. Assert scenario heading is loaded dynamically
    const simulatorHeading = page.locator('h3:has-text("Training Chat with")');
    await expect(simulatorHeading).toContainText('Training Chat with Maria');

    // 3. Send validation message to patient
    const input = page.locator('input[placeholder*="Type your response"]');
    await input.fill('I have some chamomile tea for you, Maria.');
    await input.press('Enter');

    // 4. Verify that the sent message appears in chat bubbles
    const caregiverBubble = page.locator('.chat-bubble.caregiver');
    await expect(caregiverBubble).toContainText('chamomile tea');

    // 5. Verify patient response bubble appears (handling async API delay)
    const patientBubble = page.locator('.chat-bubble.patient').nth(1);
    await expect(patientBubble).toBeVisible({ timeout: 12000 });
  });
});
