const { chromium } = require('/root/.nvm/versions/node/v22.13.1/lib/node_modules/playwright/index.mjs');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();

  try {
    await page.goto('http://localhost:5000/');
    await page.waitForSelector('#username', { timeout: 10000 });
    await page.fill('#username', 'admin');
    await page.fill('#password', 'admin123');
    await page.evaluate(() => doLogin());
    await page.waitForSelector('#content', { timeout: 15000 });
    await page.waitForTimeout(2000);

    const results = [];

    // 消息中心 - 通过evaluate导航
    await page.evaluate(() => navTo('/messages'));
    await page.waitForTimeout(2500);
    results.push(`消息中心: msg-row-click=${await page.locator('.msg-row-click').count()}`);

    // 待办中心
    await page.evaluate(() => navTo('/todos'));
    await page.waitForTimeout(2500);
    results.push(`待办中心: todo-row-click=${await page.locator('.todo-row-click').count()}`);

    console.log('=== E2E 验证结果 ===');
    results.forEach(r => console.log(r));

    const allPass = results.every(r => r.includes('=0') === false);
    if (allPass) console.log('✅ 全部通过');
    else console.log('⚠️ 部分未通过');

  } catch (e) {
    console.error('E2E 失败:', e.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
})();
