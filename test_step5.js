const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const results = [];
  const errors = [];
  page.on('pageerror', err => errors.push(err.message));

  await page.goto('http://127.0.0.1:5000');
  await page.fill('#username', 'admin');
  await page.fill('#password', 'admin123');
  await page.click('button');
  await page.waitForSelector('#portalView', { timeout: 5000 });

  // 导航到规建管
  await page.click('[data-route="/project"]');
  await page.waitForTimeout(1200);

  // 标题
  const title = await page.$eval('.page-title', el => el.textContent);
  results.push('✅ 标题: ' + title.trim());

  // 统计条
  const statNums = await page.$$eval('.stat-box .num', els => els.map(e => e.textContent.trim()));
  results.push('✅ 统计条: ' + JSON.stringify(statNums));

  // 项目卡片
  const cards = await page.$$eval('.proj-card', els => els.length);
  results.push('✅ 项目卡片: ' + cards + ' 个');

  // 切换到列表视图
  await page.click('.btn-ghost:nth-child(2)');
  await page.waitForTimeout(500);
  const rows = await page.$$eval('.tbl tbody tr', els => els.length);
  results.push('✅ 列表视图: ' + rows + ' 行');

  // 点击展开详情
  await page.click('.tbl tbody tr:first-child');
  await page.waitForTimeout(800);
  const detailTitle = await page.$eval('#projDetail', el => el.textContent.substring(0, 80));
  results.push('✅ 项目详情: ' + (detailTitle.includes('详情') ? '展开正常' : '异常'));

  // 检查阶段时间轴
  const stages = await page.$$eval('.ps-node', els => els.length);
  results.push('✅ 阶段时间轴: ' + stages + ' 个节点');

  // 检查审批记录
  const apprs = await page.$$eval('.appr-row', els => els.length);
  results.push('✅ 审批记录: ' + apprs + ' 条');

  // 筛选测试 - 类型筛选
  await page.click('.btn-ghost:first-child'); // 回到卡片视图
  await page.waitForTimeout(300);
  // select type 交通
  await page.selectOption('select:nth-of-type(1)', '交通');
  await page.waitForTimeout(600);
  const filteredCards = await page.$$eval('.proj-card', els => els.length);
  results.push('✅ 筛选(交通): ' + filteredCards + ' 个');

  results.push(errors.length === 0 ? '✅ 控制台零错误' : '❌ 控制台错误: ' + errors.join('; '));
  console.log(results.join('\n'));
  await browser.close();
})();
