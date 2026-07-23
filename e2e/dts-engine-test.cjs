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

    // 切换到态势大屏
    await page.evaluate(() => navTo('/overview'));
    await page.waitForTimeout(3000);

    // 检查地图切换按钮是否存在
    const switchBtns = await page.locator('.ov-map-btn').count();
    results.push(`视图切换按钮: ${switchBtns}`);

    // 检查二维地图容器
    const c2d = await page.locator('#ovMapContainer2d').count();
    results.push(`二维地图容器: ${c2d}`);

    // 检查三维引擎容器
    const c3d = await page.locator('#ovMapContainer3d').count();
    results.push(`三维引擎容器: ${c3d}`);

    // 检查三维引擎状态
    const dtsStatus = await page.locator('#ovDtsStatus').count();
    results.push(`DTS状态元素: ${dtsStatus}`);

    // 检查 DTS_ENGINE 全局对象
    const dtsAvailable = await page.evaluate(() => typeof DTS_ENGINE !== 'undefined');
    results.push(`DTS_ENGINE 全局对象: ${dtsAvailable}`);

    // 点击三维按钮切换
    await page.click('.ov-map-btn[data-mode="3d"]');
    await page.waitForTimeout(1500);

    // 检查切换后状态
    const c2dHidden = await page.evaluate(() => document.getElementById('ovMapContainer2d').style.display);
    const c3dVisible = await page.evaluate(() => document.getElementById('ovMapContainer3d').style.display);
    results.push(`切换后: 2d=${c2dHidden}, 3d=${c3dVisible}`);

    // 检查三维引擎状态文本
    const dtsStatusText = await page.evaluate(() => {
      const el = document.getElementById('ovDtsStatus');
      return el ? el.textContent.trim().substring(0, 30) : 'not found';
    });
    results.push(`DTS状态文本: "${dtsStatusText}"`);

    // 切回二维
    await page.click('.ov-map-btn[data-mode="2d"]');
    await page.waitForTimeout(1500);

    const c2dBack = await page.evaluate(() => document.getElementById('ovMapContainer2d').style.display);
    const c3dBack = await page.evaluate(() => document.getElementById('ovMapContainer3d').style.display);
    results.push(`切回二维: 2d=${c2dBack}, 3d=${c3dBack}`);

    console.log('=== E2E 验证结果 ===');
    results.forEach(r => console.log(r));

    const allPass = switchBtns === 2 && c2d === 1 && c3d === 1 && dtsAvailable;
    if (allPass) console.log('✅ 全部通过');
    else console.log('⚠️ 部分未通过');

  } catch (e) {
    console.error('E2E 失败:', e.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
})();
