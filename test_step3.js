const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const results = [];
  const errors = [];
  page.on('pageerror', err => errors.push(err.message));

  // 1. 登录
  await page.goto('http://127.0.0.1:5000');
  await page.fill('#username', 'admin');
  await page.fill('#password', 'admin123');
  await page.click('button');
  await page.waitForSelector('#portalView', { timeout: 5000 });
  results.push('✅ 登录成功');

  // 2. 导航到数据中枢 (概览 tab)
  await page.click('[data-route="/data"]');
  await page.waitForTimeout(1500);

  const title = await page.textContent('.page-title');
  results.push('✅ 标题: ' + title.trim());

  // 检查 dcBody 内容
  const dcBodyHTML = await page.$eval('#dcBody', el => el.innerHTML.substring(0, 300));
  results.push('📋 dcBody HTML前300字: ' + dcBodyHTML);

  // 重新找 stat-box
  const statBoxes = await page.$$('#dcBody .stat-box');
  results.push('📊 stat-box数量: ' + statBoxes.length);
  if (statBoxes.length > 0) {
    const nums = await page.$$eval('#dcBody .stat-box .num', els => els.map(e => e.textContent));
    results.push('✅ 统计数字: ' + JSON.stringify(nums));
  }

  // 领域卡片
  const dcCards = await page.$$('#dcBody .dc-domain-card');
  results.push('📊 领域卡片数: ' + dcCards.length);

  // 3. 数据资源目录
  await page.click('.subtab:nth-child(2)');
  await page.waitForTimeout(800);
  const resCards = await page.$$eval('.dc-res-card', els => els.length);
  results.push('✅ 资源目录: ' + resCards + ' 卡片');

  // 4. 指标看板
  await page.click('.subtab:nth-child(3)');
  await page.waitForTimeout(1500);
  const indRows = await page.$$eval('.tbl tbody tr', els => els.length);
  results.push('✅ 指标看板: ' + indRows + ' 行');

  // 5. 趋势图
  await page.click('.tbl tbody tr:first-child');
  await page.waitForTimeout(1000);
  const chartHTML = await page.$eval('#indChart', el => el.innerHTML.substring(0, 200));
  results.push('📈 趋势图HTML: ' + chartHTML);

  // 6. 权限
  await page.click('.btn-logout');
  await page.waitForSelector('#loginView', { timeout: 3000 });
  await page.fill('#username', 'wangjing');
  await page.fill('#password', 'wangjing123');
  await page.click('button');
  await page.waitForSelector('#portalView', { timeout: 5000 });

  const dataMenu = await page.$$eval('[data-route="/data"]', els => els.length);
  results.push('✅ 经办人可见数据中枢: ' + (dataMenu > 0 ? '是' : '否'));
  const sysMenu = await page.$$eval('[data-route="/system"]', els => els.length);
  results.push('✅ 经办人不可见系统管理: ' + (sysMenu === 0 ? '正确' : '异常'));

  results.push(errors.length === 0 ? '✅ 控制台零错误' : '❌ 控制台错误: ' + errors.join('; '));

  console.log(results.join('\n'));
  await browser.close();
})();
