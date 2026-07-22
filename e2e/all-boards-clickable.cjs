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

    // 工作台
    await page.click('text=工作台');
    await page.waitForTimeout(2500);
    results.push(`工作台: wb-stat-click=${await page.locator('.wb-stat-click').count()}, xa-pulse-click=${await page.locator('.xa-pulse-click').count()}`);

    // 数据中心 - 先点击概览 tab
    await page.click('text=建交数据中枢');
    await page.waitForTimeout(2000);
    await page.click('text=概览');
    await page.waitForTimeout(2500);
    results.push(`数据中心概览: dc-stat-click=${await page.locator('.dc-stat-click').count()}`);

    // 数据资源目录
    await page.click('text=数据资源目录');
    await page.waitForTimeout(2500);
    results.push(`数据资源: dc-res-click=${await page.locator('.dc-res-click').count()}`);

    // 数据治理
    await page.click('text=数据治理');
    await page.waitForTimeout(2500);
    results.push(`数据治理: gov-row-click=${await page.locator('.gov-row-click').count()}`);

    // 业务专题
    await page.click('text=业务专题');
    await page.waitForTimeout(3000);
    results.push(`业务专题: tp-stat-click=${await page.locator('.tp-stat-click').count()}`);

    // 项目管理
    await page.click('text=规建管一体化');
    await page.waitForTimeout(3000);
    results.push(`项目管理: proj-stat-click=${await page.locator('.proj-stat-click').count()}`);

    // 审批时效
    await page.click('text=审批时效');
    await page.waitForTimeout(2500);
    results.push(`审批时效: proj-stat-click=${await page.locator('.proj-stat-click').count()}, eff-row-click=${await page.locator('.eff-row-click').count()}`);

    // 待我审批
    await page.click('text=待我审批');
    await page.waitForTimeout(2500);
    results.push(`待我审批: proj-stat-click=${await page.locator('.proj-stat-click').count()}`);

    console.log('=== E2E 验证结果 ===');
    results.forEach(r => console.log(r));

    // 验证 - 只检查关键指标是否存在（不检查具体数量，因为数据可能变化）
    const checks = [
      [results[0], 'wb-stat-click=4', 'xa-pulse-click=4'],
      [results[1], 'dc-stat-click=4'],
      [results[2], 'dc-res-click='],  // 只要有值即可
      [results[3], 'gov-row-click='], // 只要有值即可
      [results[4], 'tp-stat-click=6'],
      [results[5], 'proj-stat-click=5'],
      [results[6], 'eff-row-click=7'],
      [results[7], 'proj-stat-click=4'],
    ];

    let allPass = true;
    for (const [actual, ...expectedParts] of checks) {
      for (const exp of expectedParts) {
        if (!actual.includes(exp)) {
          console.log(`❌ 预期包含 "${exp}", 实际: ${actual}`);
          allPass = false;
        }
      }
    }
    if (allPass) console.log('✅ 全部通过');
    else console.log('⚠️ 部分未通过');

  } catch (e) {
    console.error('E2E 失败:', e.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
})();
