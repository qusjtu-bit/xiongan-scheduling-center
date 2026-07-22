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

    await page.click('text=建交数据中枢');
    await page.waitForTimeout(4000);

    // 通过 JS 获取页面中实际渲染的 HTML
    const renderedHtml = await page.evaluate(() => {
      const el = document.getElementById('dcBody');
      return el ? el.innerHTML : 'null';
    });

    // 检查是否包含 dc-stat-click
    console.log('Rendered HTML includes dc-stat-click:', renderedHtml.includes('dc-stat-click'));

    // 获取第一个 stat-box 的完整 outerHTML
    const firstBox = await page.evaluate(() => {
      const box = document.querySelector('#dcBody .stat-box');
      return box ? box.outerHTML : 'not found';
    });
    console.log('First stat-box:', firstBox.substring(0, 200));

    // 直接检查网络请求返回的 portal.js 内容
    const [response] = await Promise.all([
      page.waitForResponse(resp => resp.url().includes('portal.js')),
      page.reload({ waitUntil: 'networkidle' })
    ]);
    const jsText = await response.text();
    console.log('Network portal.js includes dc-stat-click:', jsText.includes('dc-stat-click'));

  } catch (e) {
    console.error('失败:', e.message);
  } finally {
    await browser.close();
  }
})();
