import { test, expect } from "@playwright/test";

test.describe("Marketplace page", () => {
  test("redirects unauthenticated users to login", async ({ page }) => {
    await page.goto("/marketplace");
    await expect(page).toHaveURL(/login/, { timeout: 5000 });
  });
});

test.describe("Scenarios page", () => {
  test("redirects unauthenticated users to login", async ({ page }) => {
    await page.goto("/scenarios");
    await expect(page).toHaveURL(/login/, { timeout: 5000 });
  });
});

test.describe("Settings page", () => {
  test("redirects unauthenticated users to login", async ({ page }) => {
    await page.goto("/settings");
    await expect(page).toHaveURL(/login/, { timeout: 5000 });
  });
});

test.describe("Upload page", () => {
  test("redirects unauthenticated users to login", async ({ page }) => {
    await page.goto("/upload");
    await expect(page).toHaveURL(/login/, { timeout: 5000 });
  });
});
