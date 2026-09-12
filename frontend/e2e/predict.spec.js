import { expect, test } from "@playwright/test";

test("predicting Aspirin via the example chip shows a result", async ({ page }) => {
  await page.goto("/");

  await page.getByRole("button", { name: "Aspirin" }).click();

  await expect(page.getByText(/Predicted solubility:/)).toBeVisible({ timeout: 15_000 });
  await expect(page.getByRole("img", { name: "2D structure of the input molecule" })).toBeVisible();
});

test("submitting an invalid SMILES string shows the error banner", async ({ page }) => {
  await page.goto("/");

  await page.getByLabel("SMILES string").fill("not a smiles $$$");
  await page.getByRole("button", { name: "Predict" }).click();

  await expect(page.getByRole("alert")).toBeVisible({ timeout: 15_000 });
});
