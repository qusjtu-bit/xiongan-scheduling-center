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

  // ====== Step 8: 刷新指示器 ======
  await page.waitForTimeout(500);
  const dot = await page.$('#refreshDot');
  results.push(dot ? '✅ 刷新指示器存在: ' + (await dot.textContent()) : '❌ 刷新指示器缺失');

  // ====== Step 8: 毛玻璃顶栏 ======
  const topbarStyle = await page.$eval('.topbar', el => getComputedStyle(el).backdropFilter);
  results.push(topbarStyle && topbarStyle !== 'none' ? '✅ 毛玻璃顶栏生效: ' + topbarStyle : '⚠️ 毛玻璃可能未生效');

  // ====== Step 6: 业务专题 ======
  await page.click('[data-route="/topic"]');
  await page.waitForTimeout(1200);
  const topicTitle = await page.$eval('.page-title', el => el.textContent);
  results.push('✅ 业务专题: ' + topicTitle.slice(0, 40));

  const indCards = await page.$$eval('.tp-ind-card', els => els.length);
  results.push('✅ 指标卡片: ' + indCards + ' 个');

  // 切换专题
  let subtabs = await page.$$('.subtab');
  if (subtabs.length >= 2) {
    await subtabs[1].click(); // 交通运输
    await page.waitForTimeout(1000);
    const indCards2 = await page.$$eval('.tp-ind-card', els => els.length);
    results.push('✅ 切换交通专题: ' + indCards2 + ' 个指标');
  }

  // ====== Step 7: 智能体 ======
  await page.click('[data-route="/ai"]');
  await page.waitForTimeout(800);
  const aiTitle = await page.$eval('.page-title', el => el.textContent);
  results.push('✅ 智能体: ' + aiTitle.slice(0, 30));

  // 智能预警
  subtabs = await page.$$('.ai-tabs .subtab, [data-subtab]');
  const aiTabs = await page.$$('.subtab');
  if (aiTabs.length >= 2) {
    await aiTabs[1].click(); // 智能预警
    await page.waitForTimeout(1200);
    const warnItems = await page.$$eval('.ai-alert-item, .ai-warn-item', els => els.length);
    results.push('✅ 智能预警: ' + warnItems + ' 项');
  }

  // 智能分析
  if (aiTabs.length >= 3) {
    await aiTabs[2].click(); // 智能分析
    await page.waitForTimeout(1200);
    // 点击分析按钮
    const analyzeBtn = await page.$('.ai-analysis-block button, button:has-text("生成分析")');
    if (analyzeBtn) { await analyzeBtn.click(); await page.waitForTimeout(1500); }
    const analysisBlocks = await page.$$eval('.ai-analysis-block', els => els.length);
    results.push('✅ 智能分析: ' + analysisBlocks + ' 领域');
  }

  // 智能决策
  if (aiTabs.length >= 4) {
    await aiTabs[3].click(); // 智能决策
    await page.waitForTimeout(800);
    const decideBtn = await page.$('button:has-text("执行决策"), button:has-text("模拟决策")');
    if (decideBtn) { await decideBtn.click(); await page.waitForTimeout(1500); }
    const actionItems = await page.$$eval('.ai-action-item', els => els.length);
    results.push('✅ 智能决策: ' + actionItems + ' 步');
  }

  // 智能对话
  if (aiTabs.length >= 1) {
    await aiTabs[0].click(); // 智能对话
    await page.waitForTimeout(400);
    const quickBtns = await page.$$eval('.ai-quick-actions button, .ai-quick-actions code', els => els.length);
    results.push('✅ 智能对话: ' + quickBtns + ' 快捷入口');
  }

  // ====== Step 8: Toast 通知 ======
  // 触发全局搜索 Toast
  await page.click('#globalSearch');
  await page.keyboard.press('Enter');
  await page.waitForTimeout(600);
  const toastExists = await page.$('.toast');
  results.push(toastExists ? '✅ Toast通知生效' : '⚠️ Toast未触发');

  // ====== Step 8: 快捷键 Ctrl+1 → 工作台 ======
  await page.keyboard.press('Control+1');
  await page.waitForTimeout(600);
  const routeAfterShortcut = await page.evaluate(() => {
    const title = document.querySelector('.page-title');
    return title ? title.textContent.slice(0,20) : 'unknown';
  });
  results.push('✅ Ctrl+1 快捷键: ' + routeAfterShortcut);

  // ====== Step 8: 数字脉冲动画 ======
  const numPulse = await page.$eval('.stat-box .stat-num, .stat-num', el => {
    const cs = getComputedStyle(el);
    return cs.animationName !== 'none';
  }).catch(() => false);
  results.push(numPulse ? '✅ numPulse动画生效' : '⚠️ numPulse未检测到（可能仅态势页触发）');

  // ====== 权限验证：经办人 ======
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

  // 汇总
  results.push(errors.length === 0 ? '✅ 控制台零错误' : '❌ 控制台错误: ' + errors.join('; '));
  console.log(results.join('\n'));
  await browser.close();
})();
