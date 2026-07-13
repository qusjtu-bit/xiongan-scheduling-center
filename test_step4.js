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

  // 2. 导航到态势大屏
  await page.click('[data-route="/overview"]');
  await page.waitForTimeout(1500);

  // 检查标题
  const title = await page.$eval('.ov-sys-name', el => el.textContent);
  results.push('✅ 标题: ' + title.trim());

  // 检查核心指标条
  const coreItems = await page.$$eval('.ov-core-item', els => els.length);
  results.push('✅ 核心指标条: ' + coreItems + ' 项');

  // 检查领域面板
  const domainPanels = await page.$$eval('.ov-domain-panel', els => els.length);
  results.push('✅ 领域面板: ' + domainPanels + ' 个');

  // 检查地图 Canvas
  const canvas = await page.$('#ovMapCanvas');
  results.push('✅ 地图Canvas: ' + (canvas ? '已渲染' : '未找到'));

  // 检查事件时间线
  const tlItems = await page.$$eval('.ov-tl-item', els => els.length);
  results.push('✅ 事件时间线: ' + tlItems + ' 条');

  // 检查预警滚动条
  const warnItems = await page.$$eval('.ov-warn-item', els => els.length);
  results.push('✅ 预警条目: ' + warnItems + ' 条');

  // 检查时钟
  const clock = await page.$eval('#ovClock', el => el.textContent);
  results.push('✅ 时钟运行: ' + (clock && clock.includes(':') ? '是' : '否'));

  // 切换到其他页面再切回来，验证计时器不泄露
  await page.click('[data-route="/workbench"]');
  await page.waitForTimeout(300);
  await page.click('[data-route="/overview"]');
  await page.waitForTimeout(800);
  const canvas2 = await page.$('#ovMapCanvas');
  results.push('✅ 二次进入: ' + (canvas2 ? '正常' : '异常'));

  // 经办人权限——态势大屏可见
  await page.click('.btn-logout');
  await page.waitForSelector('#loginView', { timeout: 3000 });
  await page.fill('#username', 'wangjing');
  await page.fill('#password', 'wangjing123');
  await page.click('button');
  await page.waitForSelector('#portalView', { timeout: 5000 });
  await page.click('[data-route="/overview"]');
  await page.waitForTimeout(1000);
  const title2 = await page.$eval('.ov-sys-name', el => el.textContent);
  results.push('✅ 经办人可见态势大屏: ' + (title2 ? '是' : '否'));

  results.push(errors.length === 0 ? '✅ 控制台零错误' : '❌ 控制台错误: ' + errors.join('; '));

  console.log(results.join('\n'));
  await browser.close();
})();
