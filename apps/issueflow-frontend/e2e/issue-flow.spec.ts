import { expect, test } from "@playwright/test";

test("basic issue workflow: list, detail, status update, comment", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Engineering issue dashboard" })).toBeVisible();
  await expect(page.getByTestId("issue-list-loading")).toBeHidden({ timeout: 15_000 });

  const firstIssue = page.locator("[data-testid^='issue-row-']").first();
  await expect(firstIssue).toBeVisible({ timeout: 15_000 });

  const issueTitle = await firstIssue.locator("h3").innerText();
  await firstIssue.click();

  await expect(page.getByTestId("issue-detail-panel")).toBeVisible();
  await expect(page.getByTestId("issue-detail-panel").getByRole("heading", { level: 2 })).toHaveText(
    issueTitle,
  );

  const statusSelect = page.getByTestId("detail-status-select");
  const options = statusSelect.locator("option");
  const optionCount = await options.count();
  if (optionCount > 1) {
    const nextStatusValue = await options.nth(1).getAttribute("value");
    if (nextStatusValue) {
      await statusSelect.selectOption(nextStatusValue);
      await expect(
        page.getByTestId("issue-detail-panel").getByTestId("status-badge"),
      ).toContainText(nextStatusValue.replace(/_/g, " "), { timeout: 10_000 });
    }
  }

  await page.getByTestId("comment-author").selectOption({ index: 1 });
  const commentText = `E2E comment ${Date.now()}`;
  await page.getByTestId("comment-body").fill(commentText);
  await page.getByTestId("comment-submit").click();

  await expect(page.getByText(commentText)).toBeVisible({ timeout: 10_000 });

  await page.getByTestId("issue-detail-close").click();
  await expect(page.getByTestId("issue-detail-panel")).toBeHidden();
});
