import { test, expect } from "@playwright/test";
test("renders ledger dashboard", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "LedgerGuard" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Record transaction" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Compare balances" })).toBeVisible();
});
