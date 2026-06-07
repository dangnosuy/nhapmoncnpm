import { expect, test } from '@playwright/test';

const baseURL = 'http://127.0.0.1:5173';

async function login(page, email, password) {
  await page.goto(`${baseURL}/login`);
  await page.locator('input[type="email"]').fill(email);
  await page.locator('input[type="password"]').fill(password);
  const [response] = await Promise.all([
    page.waitForResponse((response) => response.url().includes('/api/auth/login')),
    page.locator('form button[type="submit"]').click(),
  ]);
  expect(response.ok(), await response.text()).toBeTruthy();
}

test('customer, staff, and admin role flows are usable', async ({ page }) => {
  test.setTimeout(90000);
  const stamp = Date.now();
  const customerName = `E2E Customer ${stamp}`;
  const customerEmail = `e2e_${stamp}@test.local`;
  const customerPassword = 'Password123!';
  const jsErrors = [];
  const failedRequests = [];

  page.on('pageerror', (error) => jsErrors.push(error.message));
  page.on('requestfailed', (request) => {
    const url = new URL(request.url());
    const isAppRequest = url.hostname === '127.0.0.1' || url.hostname === 'localhost';
    if (isAppRequest && !url.pathname.includes('/api/events')) {
      failedRequests.push(`${request.method()} ${request.url()}`);
    }
  });

  await page.goto(`${baseURL}/login`);
  await page.getByRole('button', { name: 'Đăng ký khách hàng' }).click();
  const registerInputs = page.locator('form input');
  await registerInputs.nth(0).fill(customerName);
  await registerInputs.nth(1).fill(`9${stamp}`.slice(0, 12));
  await registerInputs.nth(2).fill(customerEmail);
  await registerInputs.nth(3).fill(customerPassword);
  await registerInputs.nth(4).fill(customerPassword);
  const [registerResponse] = await Promise.all([
    page.waitForResponse((response) => response.url().includes('/api/auth/register')),
    page.getByRole('button', { name: 'Đăng ký', exact: true }).click(),
  ]);
  expect(registerResponse.ok(), await registerResponse.text()).toBeTruthy();
  await expect(page.locator('form').getByRole('button', { name: 'Đăng nhập' })).toBeVisible();

  await login(page, customerEmail, customerPassword);
  await page.waitForTimeout(800);
  await expect(page).toHaveURL(/\/client\/$/);
  await expect(page.getByText('Tiện ích tài khoản')).toBeVisible();
  await expect(page.locator('#heroName')).toContainText(customerName);

  await page.getByRole('button', { name: 'Tiết kiệm của tôi' }).click();
  await expect(page.locator('#productsGrid')).toContainText('Không kỳ hạn');
  await page.locator('#openSavingsAmount').fill('1000000');
  await page.locator('#openSavingsBtn').click();
  await expect(page.locator('#transactionsList')).toContainText('PENDING');

  await page.locator('#logoutBtn').click();
  await page.waitForURL('**/login');

  await login(page, 'staff@gmail.com', 'staff123');
  await page.waitForTimeout(800);
  await expect(page).toHaveURL(/\/staff\/$/);
  await expect(page.getByText('Duyệt giao dịch')).toBeVisible();
  const customerRow = page.locator('tr', { hasText: customerName }).filter({ hasText: 'Mở sổ' }).first();
  await expect(customerRow).toBeVisible();
  await customerRow.getByRole('button', { name: 'Duyệt' }).click();
  await page.locator('#submitConfirmBtn').click();
  await expect(page.locator('tr', { hasText: customerName }).filter({ hasText: 'Mở sổ' })).toHaveCount(0);

  await page.locator('#logoutBtn').click();
  await page.waitForURL('**/login');

  await login(page, customerEmail, customerPassword);
  await page.waitForTimeout(800);
  await expect(page).toHaveURL(/\/client\/$/);
  await page.getByRole('button', { name: 'Tiết kiệm của tôi' }).click();
  await expect(page.locator('#accountsGrid')).toContainText('Mã sổ');
  await expect(page.locator('#accountsGrid')).toContainText('1.000.000');

  await page.locator('#logoutBtn').click();
  await page.waitForURL('**/login');

  await login(page, 'admin@gmail.com', 'admin123');
  await page.waitForTimeout(800);
  await expect(page).toHaveURL(/\/admin$/);
  await expect(page.getByText('Dashboard tổng quan')).toBeVisible();
  await expect(page.getByRole('link', { name: /Duyệt giao dịch/ })).toHaveCount(0);
  await page.getByRole('link', { name: /Nhân sự/ }).click();
  await expect(page.getByText('Quản lý Nhân sự')).toBeVisible();
  await page.getByRole('link', { name: /Gói tiết kiệm/ }).click();
  await expect(page.getByText('Quản lý Gói Tiết Kiệm')).toBeVisible();
  await page.getByRole('link', { name: /Tham số/ }).click();
  await expect(page.getByText('Tham số Hệ thống (QĐ6)')).toBeVisible();

  expect(jsErrors).toEqual([]);
  expect(failedRequests).toEqual([]);
});
