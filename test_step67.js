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
  results.push('✅ 登录成功');

  // ====== Step 6: 业务专题 ======
  await page.click('[data-route="/topic"]');
  await page.waitForTimeout(1500);
  const topicTitle = await page.$eval('.page-title', el => el.textContent);
  results.push('✅ 业务专题: ' + topicTitle.slice(0, 40));

  const indCards = await page.$$eval('.tp-ind-card', els => els.length);
  results.push('✅ 指标卡片: ' + indCards + ' 个');

  // 切换专题
  await page.click('.subtab:nth-child(2)'); // 交通运输
  await page.waitForTimeout(1000);
  const indCards2 = await page.$$eval('.tp-ind-card', els => els.length);
  results.push('✅ 切换交通专题: ' + indCards2 + ' 个指标');

  // ====== Step 7: 智能体 ======
  await page.click('[data-route="/ai"]');
  await page.waitForTimeout(800);
  const aiTitle = await page.$eval('.page-title', el => el.textContent);
  results.push('✅ 智能体: ' + aiTitle.slice(0, 30));

  // 智能预警
  await page.click('.subtab:nth-child(2)'); // 智能预警
  await page.waitForTimeout(1200);
  const warnItems = await page.$$eval('.ai-alert-item', els => els.length);
  results.push('✅ 智能预警: ' + warnItems + ' 项');

  // 智能分析
  await page.click('.subtab:nth-child(3)'); // 智能分析
  await page.waitForTimeout(1200);
  const analysisBlocks = await page.$$eval('.ai-analysis-block', els => els.length);
  results.push('✅ 智能分析: ' + analysisBlocks + ' 领域');

  // 智能决策
  await page.click('.subtab:nth-child(4)'); // 智能决策
  await page.waitForTimeout(800);
  const actionItems = await page.$$eval('.ai-action-item', els => els.length);
  results.push('✅ 智能决策: ' + actionItems + ' 步');

  // 智能对话
  await page.click('.subtab:nth-child(1)'); // 智能对话
  await page.waitForTimeout(400);
  const quickBtns = await page.$$eval('.ai-quick-actions button', els => els.length);
  results.push('✅ 智能对话: ' + quickBtns + ' 快捷入口');

  // 经办人权限
  await page.click('.btn-logout');
  await page.waitForSelector('#loginView', { timeout: 3000 });
  await page.fill('#username', 'wangjing');
  await page.fill('#password', 'wangjing123');
  await page.click('button');
  await page.waitForSelector('#portalView', { timeout: 5000 });

  const topicBtn = await page.$$eval('[data-route="/topic"]', els => els.length);
  const aiBtn = await page.$$eval('[data-route="/ai"]', els => els.length);
  const sysBtn = await page.$$eval('[data-route="/system"]', els => els.length);
  results.push('✅ 经办人权限: 专题=' + (topicBtn>0?'有':'无') + ' AI=' + (aiBtn>0?'有':'无') + ' 系统=' + (sysBtn===0?'无':'异常'));

  results.push(errors.length === 0 ? '✅ 控制台零错误' : '❌ ' + errors.join('; '));
  console.log(results.join('\n'));
  await browser.close();
})();
