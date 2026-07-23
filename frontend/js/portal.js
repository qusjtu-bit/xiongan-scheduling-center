/* ============================================================
   建交协同调度中心 · 统一工作门户（Step 2）
   ============================================================ */
'use strict';

let token = localStorage.getItem('token') || '';
let currentUser = null;
let currentRoute = '/workbench';
let msgUnreadOnly = false;
let dataTab = 'catalog';          // 建交数据中枢当前页签
let dataDomain = 0;                // 资源/指标领域筛选（0=全部）

/* ---------- 菜单：权限编码 → 前端路由 / 图标 ---------- */
const MENU_ROUTE = {
  dashboard: '/workbench', overview: '/overview', project: '/project',
  topic: '/topic', ai: '/ai', data: '/data', system: '/system',
  'system:user': '/system/users', 'system:dept': '/system/depts',
  'system:role': '/system/roles', 'system:perm': '/system/perms',
};
/* ---------- SVG 图标集（替换 emoji，更专业） ---------- */
const SVG_ICONS = {
  dashboard: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>',
  overview: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
  project: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>',
  topic: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>',
  ai: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a10 10 0 1 0 10 10h-10V2z"/><path d="M12 12 2 12a10 10 0 0 0 10 10V12z"/><path d="M12 2a10 10 0 0 1 10 10h-10V2z"/></svg>',
  data: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>',
  system: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
  'system:user': '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
  'system:dept': '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>',
  'system:role': '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>',
  'system:perm': '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
};

const MENU_ICON = {};
for (const [k, v] of Object.entries(SVG_ICONS)) {
  MENU_ICON[k] = v;
}

/* ---------- 快捷入口 SVG 图标映射 ---------- */
const QUICK_ICONS = {
  '全局总览': '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
  '态势大屏': '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>',
  '规建管一体化': '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/><line x1="12" y1="11" x2="12" y2="17"/><line x1="9" y1="14" x2="15" y2="14"/></svg>',
  '业务专题': '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>',
  '用户管理': '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
  '角色管理': '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>',
  '部门管理': '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>',
  '网关监控': '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
  '本处室专题': '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>',
  '审批中心': '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
  '消息中心': '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>',
  '我的待办': '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>',
  '备案中心': '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>',
};

/* ---------- API 封装（自动携带Token + 失效刷新） ---------- */
async function tryRefresh() {
  const rt = localStorage.getItem('refresh_token');
  if (!rt) return false;
  try {
    const res = await fetch('/api/auth/refresh', { method: 'POST', headers: { 'Authorization': 'Bearer ' + rt } });
    const data = await res.json();
    if (data.code === 200) { token = data.data.access_token; localStorage.setItem('token', token); return true; }
  } catch (e) {}
  return false;
}

async function api(path, opts = {}) {
  const doFetch = async () => {
    const h = Object.assign({ 'Content-Type': 'application/json' }, opts.headers || {});
    if (token) h['Authorization'] = 'Bearer ' + token;
    return await fetch(path, Object.assign({}, opts, { headers: h }));
  };
  let res = await doFetch();
  if (res.status === 401) {
    if (await tryRefresh()) res = await doFetch();
    else { doLogout(); return null; }
  }
  try { return await res.json(); } catch (e) { return { code: 500, message: '响应解析失败' }; }
}

function showLoading(v) { document.getElementById('loading').style.display = v ? 'flex' : 'none'; }

/* ---------- 登录 / 登出 ---------- */
function fillAccount(u, p) {
  document.getElementById('username').value = u;
  document.getElementById('password').value = p;
}

async function doLogin() {
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;
  if (!username || !password) { alert('请输入账号和密码'); return; }
  const data = await api('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
  if (data && data.code === 200) {
    token = data.data.access_token;
    localStorage.setItem('token', token);
    localStorage.setItem('refresh_token', data.data.refresh_token);
    currentUser = data.data.user;
    await enterPortal();
  } else {
    alert((data && data.message) || '登录失败');
  }
}

function doLogout() {
  token = ''; currentUser = null;
  localStorage.removeItem('token'); localStorage.removeItem('refresh_token');
  document.getElementById('portalView').style.display = 'none';
  document.getElementById('loginView').style.display = 'flex';
}

/* ---------- 进入门户 ---------- */
async function enterPortal() {
  document.getElementById('loginView').style.display = 'none';
  document.getElementById('portalView').style.display = 'flex';

  // 顶部用户信息
  document.getElementById('uName').textContent = currentUser.real_name;
  document.getElementById('uDept').textContent = (currentUser.dept_name || '') + ' · ' + currentUser.roles.map(r => r.name).join('/');
  document.getElementById('uAvatar').textContent = currentUser.real_name.charAt(0);

  // 系统时钟
  updateClock();
  setInterval(updateClock, 1000);

  await loadMenus();
  await updateMsgBadge();
  navTo('/workbench');
}

function updateClock() {
  const el = document.getElementById('sysClock');
  if (!el) return;
  const now = new Date();
  const pad = n => String(n).padStart(2, '0');
  el.textContent = now.getFullYear() + '/' + pad(now.getMonth()+1) + '/' + pad(now.getDate()) + ' ' + pad(now.getHours()) + ':' + pad(now.getMinutes()) + ':' + pad(now.getSeconds());
}

/* ---------- 侧边栏菜单 ---------- */
async function loadMenus() {
  const data = await api('/api/auth/menus');
  const menus = (data && data.data) || [];
  const sb = document.getElementById('sidebar');
  let html = '';
  menus.forEach(m => {
    const route = MENU_ROUTE[m.perm_code] || '#';
    const ico = MENU_ICON[m.perm_code] || '📄';
    html += `<div class="side-item" data-route="${route}" onclick="navTo('${route}')">
      <span class="ico">${ico}</span><span>${m.perm_name}</span></div>`;
    if (m.children && m.children.length) {
      m.children.forEach(c => {
        const cr = MENU_ROUTE[c.perm_code] || '#';
        const ci = MENU_ICON[c.perm_code] || '📄';
        html += `<div class="side-sub"><div class="side-item" data-route="${cr}" onclick="navTo('${cr}')">
          <span class="ico">${ci}</span><span>${c.perm_name}</span></div></div>`;
      });
    }
  });
  sb.innerHTML = html;
}

async function updateMsgBadge() {
  const data = await api('/api/messages?unread=1');
  const n = (data && data.data && data.data.unread) || 0;
  const badge = document.getElementById('msgBadge');
  if (n > 0) { badge.style.display = 'flex'; badge.textContent = n > 99 ? '99+' : n; }
  else badge.style.display = 'none';
}

/* ---------- 路由 ---------- */
function navTo(route) {
  currentRoute = route;
  // 高亮
  document.querySelectorAll('.side-item').forEach(el => el.classList.remove('active'));
  const active = document.querySelector(`.side-item[data-route="${route}"]`);
  if (active) active.classList.add('active');
  // 进入消息中心时隐藏角标
  if (route === '/messages') document.getElementById('msgBadge').style.display = 'none';
  renderContent(route);
}

async function renderContent(route) {
  if (overviewRefreshTimer) { clearInterval(overviewRefreshTimer); overviewRefreshTimer = null; }
  if (window._ovMap) { try { window._ovMap.remove(); } catch(e){} window._ovMap = null; }
  stopAutoRefresh();
  showLoading(true);
  try {
    if (route === '/workbench') await renderWorkbench();
    else if (route === '/messages') await renderMessages();
    else if (route === '/todos') await renderTodos();
    else if (route.startsWith('/system')) await renderSystem(route);
    else if (route === '/data') await renderDataCenter();
    else if (route === '/overview') await renderOverview();
    else if (route === '/project') await renderProject();
    else if (route === '/topic') await renderTopic();
    else if (route === '/ai') await renderAI();
    else document.getElementById('content').innerHTML = '<div class="empty">页面不存在</div>';
  } finally {
    showLoading(false);
  }
}

/* ---------- 工作台首页 ---------- */
async function renderWorkbench() {
  const data = await api('/api/workbench/overview');
  if (!data || data.code !== 200) { document.getElementById('content').innerHTML = '<div class="empty">数据加载失败</div>'; return; }
  const d = data.data;
  const stats = d.stats;
  const name = currentUser.real_name;
  const dept = currentUser.dept_name;
  const role = currentUser.roles.map(r => r.name).join('/');

  // 拉取项目态势（用于"雄安数说"面板）
  let projStats = null;
  try { const r = await api('/api/projects/stats'); if (r && r.code === 200) projStats = r.data; } catch (e) {}

  const now = new Date();
  const hour = now.getHours();
  const greeting = hour < 6 ? '凌晨好' : hour < 9 ? '早上好' : hour < 12 ? '上午好' : hour < 14 ? '中午好' : hour < 18 ? '下午好' : '晚上好';
  const dateStr = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}`;
  const weekdayCn = ['日','一','二','三','四','五','六'][now.getDay()];
  const seasonCn = ['严冬','晚冬','早春','仲春','暮春','初夏','盛夏','暮夏','初秋','金秋','深秋','初冬'][now.getMonth()];

  const total = projStats ? projStats.total : 0;
  const inProgress = projStats && projStats.stage_count ? (projStats.stage_count['建设'] || 0) : 0;
  const overdue = projStats && projStats.risk_summary ? projStats.risk_summary.overdue : 0;
  // invest 字段单位是万元，转换为亿元
  const totalInvestYi = projStats ? (projStats.total_invest / 10000).toFixed(1) : '0.0';

  let html = `
    <div class="welcome">
      <h2>${greeting}，<span>${name}</span></h2>
      <p>${dept} · ${role}　|　欢迎使用协同调度中心统一工作门户</p>
    </div>
    <div class="stat-row">
      <div class="stat-box wb-stat-click" onclick="navTo('/project')"><div class="lab">本月办件量</div><div class="num">${stats.month_handled}</div><div class="unit">件</div><div class="sub">较上月 +12%</div></div>
      <div class="stat-box wb-stat-click" onclick="navTo('/project')"><div class="lab">平均审批时效</div><div class="num">${stats.avg_duration}</div><div class="sub">承诺时限内办结</div></div>
      <div class="stat-box wb-stat-click" onclick="navTo('/project')"><div class="lab">按时办结率</div><div class="num">${stats.on_time_rate}</div><div class="sub">保持稳定</div></div>
      <div class="stat-box wb-stat-click" onclick="navTo('/todos')"><div class="lab">在办事项</div><div class="num">${stats.pending}</div><div class="unit">项</div><div class="sub">含紧急 ${d.urgent_todo_count} 项</div></div>
    </div>
    <div class="work-grid">
      <div class="panel">
        <div class="panel-head"><div class="t">我的待办 TOP</div><div class="more" onclick="navTo('/todos')">全部 →</div></div>
        ${d.todo_top.length ? d.todo_top.map(t => `
          <div class="list-item" onclick="navTo('${t.link || '/todos'}')" style="cursor:pointer">
            <span class="dot ${t.urgency >= 3 ? 'dot-red' : t.urgency >= 2 ? 'dot-orange' : 'dot-blue'}"></span>
            <div class="li-main"><div class="li-title">${t.title}</div>
              <div class="li-sub"><span class="tag tag-gray">${t.todo_type_name}</span> ${t.source_system || ''} · 截止 ${t.due_date}</div></div>
          </div>`).join('') : '<div class="empty">暂无待办</div>'}
      </div>
      <div class="panel">
        <div class="panel-head"><div class="t">⚠️ 最新预警 TOP5</div><div class="more" onclick="navTo('/topic')">前往处置 →</div></div>
        ${d.warning_list.length ? d.warning_list.map(w => `
          <div class="list-item" onclick="navTo('/topic')" style="cursor:pointer">
            <span class="dot dot-red"></span>
            <div class="li-main"><div class="li-title">${w.title}</div>
              <div class="li-sub">${w.sender} · ${w.created_at}</div></div>
            <span class="tag tag-red">${w.level_name}</span>
          </div>`).join('') : '<div class="empty">暂无预警 🎉</div>'}
      </div>
      <div class="panel xa-pulse">
        <div class="xa-pulse-head">
          <div class="xa-pulse-title"><span class="pulse-dot"></span>雄安数说</div>
          <div class="xa-pulse-date">${dateStr} · 周${weekdayCn} · ${seasonCn}</div>
        </div>
        <div class="xa-pulse-body">
          <div class="xa-pulse-grid">
            <div class="xa-pulse-cell xa-pulse-click" onclick="openCoreDetail('cj01')">
              <div class="pl">在建项目</div>
              <div><span class="pv">${inProgress}</span><span class="pu">个</span></div>
            </div>
            <div class="xa-pulse-cell xa-pulse-click" onclick="navTo('/project')">
              <div class="pl">累计立项</div>
              <div><span class="pv">${total}</span><span class="pu">个</span></div>
            </div>
            <div class="xa-pulse-cell xa-pulse-click" onclick="openCoreDetail('cj14')">
              <div class="pl">投资总额</div>
              <div><span class="pv">${totalInvestYi}</span><span class="pu">亿元</span></div>
            </div>
            <div class="xa-pulse-cell xa-pulse-click" onclick="navTo('/project')">
              <div class="pl">逾期预警</div>
              <div><span class="pv">${overdue}</span><span class="pu">项</span></div>
            </div>
          </div>
          <div class="xa-pulse-extra">
            <div class="ex-row"><span>今日待办</span><span class="ex-tag">${d.todo_count} 项</span></div>
            <div class="ex-row"><span>未读消息</span><span class="ex-tag">${d.unread_count} 条</span></div>
            <div class="ex-row"><span>当前季节</span><span class="ex-tag">${seasonCn} · 蓝绿交织</span></div>
          </div>
        </div>
        <svg class="xa-pulse-skyline" viewBox="0 0 800 50" preserveAspectRatio="xMidYMax meet" xmlns="http://www.w3.org/2000/svg">
          <g fill="#06b6d4" opacity=".7">
            <rect x="0"   y="22" width="34" height="28"/>
            <rect x="38"  y="14" width="22" height="36"/>
            <rect x="64"  y="28" width="28" height="22"/>
            <rect x="96"  y="10" width="18" height="40"/>
            <rect x="118" y="20" width="26" height="30"/>
            <rect x="148" y="6"  width="22" height="44"/>
            <rect x="174" y="18" width="20" height="32"/>
            <rect x="198" y="26" width="30" height="24"/>
            <rect x="232" y="14" width="24" height="36"/>
            <rect x="260" y="22" width="20" height="28"/>
            <rect x="284" y="8"  width="22" height="42"/>
            <rect x="310" y="20" width="28" height="30"/>
            <rect x="342" y="14" width="20" height="36"/>
            <rect x="366" y="26" width="26" height="24"/>
            <rect x="396" y="18" width="22" height="32"/>
            <rect x="422" y="6"  width="18" height="44"/>
            <rect x="444" y="22" width="28" height="28"/>
            <rect x="476" y="12" width="22" height="38"/>
            <rect x="502" y="20" width="20" height="30"/>
            <rect x="526" y="28" width="30" height="22"/>
            <rect x="560" y="16" width="24" height="34"/>
            <rect x="588" y="8"  width="20" height="42"/>
            <rect x="612" y="22" width="26" height="28"/>
            <rect x="642" y="14" width="22" height="36"/>
            <rect x="668" y="26" width="30" height="24"/>
            <rect x="702" y="18" width="20" height="32"/>
            <rect x="726" y="10" width="24" height="40"/>
            <rect x="754" y="22" width="46" height="28"/>
          </g>
        </svg>
      </div>
    </div>
    <div class="panel">
      <div class="panel-head"><div class="t">快捷入口</div></div>
      <div class="quick-grid">
        ${d.quick_entries.map(q => `
          <div class="quick-card" onclick="navTo('${q.route}')">
            <span class="qc-ico">${QUICK_ICONS[q.name] || '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>'}</span><span class="qc-name">${q.name}</span>
          </div>`).join('')}
      </div>
    </div>`;
  document.getElementById('content').innerHTML = html;
  startAutoRefresh();
}

/* ---------- 消息中心 ---------- */
async function renderMessages() {
  const q = msgUnreadOnly ? '?unread=1' : '';
  const data = await api('/api/messages' + q);
  if (!data || data.code !== 200) { document.getElementById('content').innerHTML = '<div class="empty">数据加载失败</div>'; return; }
  const list = data.data.list || [];
  const typeColor = { 1: 'tag-blue', 2: 'tag-red', 3: 'tag-orange', 4: 'tag-gray' };
  const iconMap = { 1: '📢', 2: '⚠️', 3: '📋', 4: '⚙️' };

  let html = `
    <div class="page-head"><div class="page-title">消息中心<small>共 ${data.data.total} 条，未读 ${data.data.unread}</small></div></div>
    <div class="toolbar">
      <div class="tab ${!msgUnreadOnly ? 'active' : ''}" onclick="setMsgFilter(false)">全部</div>
      <div class="tab ${msgUnreadOnly ? 'active' : ''}" onclick="setMsgFilter(true)">未读</div>
      <button class="btn-ghost" onclick="renderMessages()">↻ 刷新</button>
    </div>
    ${list.length ? list.map(m => `
      <div class="msg-row ${m.is_read ? 'read' : 'unread'} msg-row-click" onclick="showMsgDetail(${m.id},'${_esc(m.title)}','${_esc(m.content || '')}','${_esc(m.sender)}','${m.created_at}','${m.msg_type_name}')">
        <div class="msg-ico" style="background:rgba(30,58,111,.4)">${iconMap[m.msg_type] || '📢'}</div>
        <div class="msg-body">
          <div class="msg-title">${m.title} <span class="tag ${typeColor[m.msg_type] || 'tag-gray'}">${m.msg_type_name}</span> ${m.level >= 3 ? '<span class="tag tag-red">紧急</span>' : ''}</div>
          <div class="msg-content">${m.content || ''}</div>
          <div class="msg-foot"><span>${m.sender}</span><span>${m.created_at}</span></div>
        </div>
        <div class="msg-actions">
          ${m.is_read ? '' : `<span class="mini-btn" onclick="event.stopPropagation();markRead(${m.id})">标记已读</span>`}
          <span class="mini-btn danger" onclick="event.stopPropagation();delMsg(${m.id})">删除</span>
        </div>
      </div>`).join('') : '<div class="empty">暂无消息</div>'}
  `;
  document.getElementById('content').innerHTML = html;
  if (!msgUnreadOnly) await updateMsgBadge();
}

function setMsgFilter(unread) { msgUnreadOnly = unread; renderMessages(); }

async function markRead(id) {
  await api('/api/messages/' + id + '/read', { method: 'PUT' });
  await renderMessages();
}

async function delMsg(id) {
  if (!confirm('确定删除该消息？')) return;
  await api('/api/messages/' + id, { method: 'DELETE' });
  await renderMessages();
}

/* 消息详情弹窗 */
function showMsgDetail(id, title, content, sender, createdAt, typeName) {
  showOvModal(title, `
    <div class="ov-summary-card">
      <div><strong>发送人</strong><div>${sender}</div></div>
      <div><strong>时间</strong><div>${createdAt}</div></div>
      <div><strong>类型</strong><div><span class="tag tag-blue">${typeName}</span></div></div>
    </div>
    <div class="ov-section-title">📝 消息内容</div>
    <p style="color:var(--text-2);font-size:13px;line-height:1.7">${content || '暂无内容'}</p>
  `, { width: 560 });
  // 标记已读
  api('/api/messages/' + id + '/read', { method: 'PUT' }).then(() => updateMsgBadge());
}

/* 待办详情弹窗 */
function showTodoDetail(id, title, todoType, dueDate, urgency, source) {
  showOvModal(title, `
    <div class="ov-summary-card">
      <div><strong>待办类型</strong><div><span class="tag tag-gray">${todoType}</span></div></div>
      <div><strong>紧急程度</strong><div><span class="tag ${urgency === '紧急' ? 'tag-red' : urgency === '高' ? 'tag-orange' : 'tag-blue'}">${urgency}</span></div></div>
      <div><strong>截止时间</strong><div>${dueDate}</div></div>
      <div><strong>来源系统</strong><div>${source || '-'}</div></div>
    </div>
    <div class="ov-section-title">📝 待办说明</div>
    <p style="color:var(--text-2);font-size:13px;line-height:1.7">该待办事项需要您及时处理，点击"去处理"按钮可跳转至对应业务系统进行操作。</p>
  `, { width: 560 });
}

/* ---------- 待办中心 ---------- */
async function renderTodos() {
  const data = await api('/api/todos');
  if (!data || data.code !== 200) { document.getElementById('content').innerHTML = '<div class="empty">数据加载失败</div>'; return; }
  const list = data.data.list || [];
  const today = new Date().toISOString().slice(0, 10);

  let html = `<div class="page-head"><div class="page-title">待办中心<small>共 ${data.data.total} 项</small></div></div>`;
  if (!list.length) html += '<div class="empty">暂无待办 🎉</div>';
  else html += list.map(t => {
    const overdue = t.status === 2 || (t.due_date && t.due_date < today && t.status === 0);
    const urgencyTag = t.urgency >= 3 ? 'tag-red' : t.urgency >= 2 ? 'tag-orange' : 'tag-blue';
    return `
      <div class="todo-row ${t.urgency >= 2 ? 'urgent' : ''} todo-row-click" onclick="showTodoDetail(${t.id},'${_esc(t.title)}','${_esc(t.todo_type_name)}','${t.due_date || '-'}','${t.urgency_name}','${_esc(t.source_system || '')}')">
        <div class="todo-main">
          <div class="todo-title">${t.title}</div>
          <div class="todo-meta">
            <span class="tag ${urgencyTag}">${t.urgency_name}</span>
            <span class="tag tag-gray">${t.todo_type_name}</span>
            <span>来源：${t.source_system || '-'}</span>
            <span class="todo-due ${overdue ? 'over' : ''}">截止：${t.due_date || '-'} ${overdue ? '· 已逾期' : ''}</span>
          </div>
        </div>
        <button class="btn-go" onclick="event.stopPropagation();navTo('${t.link || '/todos'}')">去处理</button>
      </div>`;
  }).join('');
  document.getElementById('content').innerHTML = html;
}

/* ---------- 系统管理 ---------- */
async function renderSystem(route) {
  const tab = route.split('/')[2] || 'users';
  const tabs = [['users', '用户管理'], ['depts', '部门管理'], ['roles', '角色管理'], ['perms', '权限管理']];
  let html = `<div class="page-head"><div class="page-title">系统管理</div></div><div class="tabs">`;
  tabs.forEach(([k, name]) => {
    html += `<div class="subtab ${k === tab ? 'active' : ''}" onclick="navTo('/system/${k}')">${name}</div>`;
  });
  html += `</div><div id="sysBody"></div>`;
  document.getElementById('content').innerHTML = html;

  const body = document.getElementById('sysBody');
  if (tab === 'users') {
    const d = await api('/api/users?size=100');
    if (!d || d.code !== 200) { body.innerHTML = '<div class="empty">无权限或加载失败（仅系统管理员可访问）</div>'; return; }
    const rows = (d.data.list || []).map(u => `
      <tr><td>${u.username}</td><td>${u.real_name}</td><td>${u.dept_name || '-'}</td>
      <td>${(u.roles || []).map(r => r.name).join('、') || '-'}</td>
      <td>${u.phone || '-'}</td>
      <td><span class="tag ${u.status === 0 ? 'tag-green' : 'tag-red'}">${u.status === 0 ? '启用' : '禁用'}</span></td></tr>`).join('');
    body.innerHTML = `<table class="tbl"><thead><tr><th>账号</th><th>姓名</th><th>部门</th><th>角色</th><th>手机号</th><th>状态</th></tr></thead><tbody>${rows}</tbody></table>
      <div class="empty">共 ${d.data.total} 个用户（覆盖全部12个处室）</div>`;
  } else if (tab === 'depts') {
    const d = await api('/api/depts');
    if (!d || d.code !== 200) { body.innerHTML = '<div class="empty">无权限或加载失败</div>'; return; }
    const flat = [];
    (function walk(ns, prefix) { ns.forEach(n => { flat.push({ ...n, path: prefix + n.dept_name }); if (n.children) walk(n.children, prefix + n.dept_name + ' / '); }); })(d.data || [], '');
    const rows = flat.map(n => `
      <tr><td>${n.path}</td><td>${n.dept_type === 1 ? '局' : n.dept_type === 2 ? '局领导' : n.dept_type === 3 ? '处室' : '科室'}</td>
      <td>${n.sort}</td><td><span class="tag tag-green">正常</span></td></tr>`).join('');
    body.innerHTML = `<table class="tbl"><thead><tr><th>部门名称</th><th>类型</th><th>排序</th><th>状态</th></tr></thead><tbody>${rows}</tbody></table>`;
  } else if (tab === 'roles') {
    const d = await api('/api/roles');
    if (!d || d.code !== 200) { body.innerHTML = '<div class="empty">无权限或加载失败</div>'; return; }
    const scopeMap = { 1: '全部', 2: '本处室', 3: '本片区', 4: '本人' };
    const rows = (d.data || []).map(r => `
      <tr><td>${r.role_name}</td><td><code>${r.role_code}</code></td>
      <td>${scopeMap[r.data_scope] || r.data_scope}</td>
      <td>${(r.permissions || []).length} 项</td>
      <td><span class="tag tag-green">正常</span></td></tr>`).join('');
    body.innerHTML = `<table class="tbl"><thead><tr><th>角色名称</th><th>编码</th><th>数据范围</th><th>权限数</th><th>状态</th></tr></thead><tbody>${rows}</tbody></table>`;
  } else if (tab === 'perms') {
    const d = await api('/api/permissions');
    if (!d || d.code !== 200) { body.innerHTML = '<div class="empty">无权限或加载失败</div>'; return; }
    body.innerHTML = `<div class="panel"><div class="panel-head"><div class="t">权限树（菜单 + 按钮/API）</div></div>
      <pre style="font-size:12px;line-height:1.9;color:#9fd;">${JSON.stringify(d.data, null, 2)}</pre></div>`;
  }
}

/* ---------- 建交数据中枢 ---------- */
async function renderDataCenter() {
  const tabs = [['overview', '概览'], ['catalog', '数据清单'], ['resources', '数据资源目录'], ['indicators', '指标看板'], ['governance', '数据治理']];
  let html = `
    <div class="page-head"><div class="page-title">建交数据中枢<small>一数一源头 · 统一数据资源管理与指标监控</small></div>
      <div style="display:flex;gap:8px">
        <button class="btn-ghost" onclick="exportDataCatalog()"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:4px"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>导出数据清单</button>
      </div></div></div>
    <div class="tabs">${tabs.map(([k, name]) => `<div class="tab ${k === dataTab ? 'active' : ''}" onclick="switchDataTab('${k}')">${name}</div>`).join('')}</div>
    <div id="dcBody"></div>`;
  document.getElementById('content').innerHTML = html;

  if (dataTab === 'overview') await renderDataOverview();
  else if (dataTab === 'catalog') await renderDataCatalog();
  else if (dataTab === 'resources') await renderDataResources();
  else if (dataTab === 'indicators') await renderDataIndicators();
  else if (dataTab === 'governance') await renderDataGovernance();
}

function switchDataTab(tab) { dataTab = tab; renderDataCenter(); }

/* -- 数据清单（一数一源头详表） -- */
let catalogFilter = { domain: 0, keyword: '' };
async function renderDataCatalog() {
  const body = document.getElementById('dcBody');
  body.innerHTML = '<div class="loading">加载数据清单...</div>';

  let url = '/api/data-catalog';
  const params = [];
  if (catalogFilter.domain) params.push('domain=' + catalogFilter.domain);
  if (catalogFilter.keyword) params.push('keyword=' + encodeURIComponent(catalogFilter.keyword));
  if (params.length) url += '?' + params.join('&');

  const res = await api(url);
  if (!res || res.code !== 200) { body.innerHTML = '<div class="empty">加载失败</div>'; return; }
  const d = res.data;

  const domNames = { 1: '城乡建设', 2: '交通运输', 3: '水利水务', 4: '城市管理', 5: '综合' };
  const typeLabels = { resource: '数据资源', indicator: '指标数据' };

  let html = '';

  // 领域统计卡
  html += `<div class="stat-row" style="grid-template-columns:repeat(${d.domain_stats.length},1fr);margin-bottom:18px">`;
  for (const ds of d.domain_stats) {
    html += `<div class="stat-box"><div class="lab">${ds.name}</div><div class="num">${ds.resources + ds.indicators}</div><div class="sub">资源${ds.resources} · 指标${ds.indicators}</div></div>`;
  }
  html += `</div>`;

  // 筛选工具栏
  html += `<div class="toolbar" style="flex-wrap:wrap;gap:8px;margin-bottom:14px">
    <input class="proj-search" placeholder="搜索数据名称或描述..." value="${catalogFilter.keyword}" onkeyup="catalogFilter.keyword=this.value;catalogDebounced()" style="min-width:220px">
    ${[[0,'全部'],[1,'城乡建设'],[2,'交通运输'],[3,'水利水务'],[4,'城市管理'],[5,'综合']].map(([v, l]) =>
      `<div class="tab ${catalogFilter.domain === v ? 'active' : ''}" onclick="catalogFilter.domain=${v};renderDataCatalog()">${l}</div>`
    ).join('')}
  </div>`;

  // 表格
  html += `<div style="overflow-x:auto"><table class="tbl" style="min-width:1400px"><thead><tr>
    <th style="width:40px">#</th>
    <th style="width:60px">类型</th>
    <th style="width:60px">编码</th>
    <th style="min-width:140px">数据名称</th>
    <th style="width:90px">数据值</th>
    <th style="width:80px">更新频率</th>
    <th style="width:80px">更新时间</th>
    <th style="min-width:120px">责任处室</th>
    <th style="width:60px">责任人</th>
    <th style="min-width:160px">所属系统（唯一源头）</th>
    <th style="min-width:140px">统计口径</th>
    <th style="width:50px">存储</th>
  </tr></thead><tbody>`;

  d.list.forEach((item, i) => {
    const typeCls = item.item_type === 'resource' ? 'tag-blue' : 'tag-green';
    const typeLabel = item.item_type === 'resource' ? '资源' : '指标';
    html += `<tr>
      <td style="color:var(--txt-3)">${i + 1}</td>
      <td><span class="tag ${typeCls}" style="font-size:10px">${typeLabel}</span></td>
      <td><code style="font-size:11px">${item.code}</code></td>
      <td style="font-weight:500" title="${item.description}">${item.name}</td>
      <td style="font-weight:600;color:var(--primary)">${item.data_value}</td>
      <td><span class="tag tag-gray" style="font-size:10px">${item.update_freq}</span></td>
      <td style="font-size:12px;color:var(--txt-3)">${item.last_update}</td>
      <td><span class="dept-chip">${item.owner_dept}</span></td>
      <td>${item.owner_person}</td>
      <td style="font-size:12px" title="${item.source_system}">${item.source_system}</td>
      <td style="font-size:11px;color:var(--txt-3)" title="${item.calc_expr}">${(item.calc_expr || '').slice(0, 40)}</td>
      <td><span class="tag tag-gray" style="font-size:10px">${item.retention_years}年</span></td>
    </tr>`;
  });

  html += `</tbody></table></div>`;
  html += `<div style="margin-top:12px;padding:10px 14px;background:var(--primary-bg);border-radius:8px;font-size:12px;color:var(--text-3)">
    📌 共 <strong style="color:var(--primary)">${d.total}</strong> 项数据 | 每项数据有且仅有一个权威来源系统 | 数据存储年限 <strong>3年</strong>
  </div>`;

  body.innerHTML = html;
}

let catalogTimer = null;
function catalogDebounced() {
  if (catalogTimer) clearTimeout(catalogTimer);
  catalogTimer = setTimeout(() => renderDataCatalog(), 400);
}

async function exportDataCatalog() {
  showToast('正在生成数据清单...', 'info');
  try {
    const res = await fetch('/api/data-catalog/export', {
      headers: { 'Authorization': 'Bearer ' + token },
    });
    if (!res.ok) throw new Error('导出失败');
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `建交数据清单_${new Date().toISOString().slice(0, 10)}.xlsx`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast('数据清单导出成功 ✓', 'success');
  } catch (e) {
    showToast('导出失败：' + e.message, 'warn');
  }
}

/* -- 概览 -- */
async function renderDataOverview() {
  const body = document.getElementById('dcBody');
  const data = await api('/api/data-overview');
  if (!data || data.code !== 200) { body.innerHTML = '<div class="empty">加载失败</div>'; return; }
  const d = data.data;
  const domNames = { 1: '城乡建设', 2: '交通运输', 3: '水利水务', 4: '城市管理' };

  let html = `<div class="stat-row" style="grid-template-columns:repeat(4,1fr);margin-bottom:24px">
    <div class="stat-box dc-stat-click" onclick="switchDataTab('resources')"><div class="lab">数据资源总数</div><div class="num">${d.resource_count}</div></div>
    <div class="stat-box dc-stat-click" onclick="switchDataTab('indicators')"><div class="lab">标准指标数</div><div class="num">${d.indicator_count}</div></div>
    <div class="stat-box dc-stat-click" onclick="switchDataTab('catalog')"><div class="lab">主题库记录数</div><div class="num">${d.total_records}</div></div>
    <div class="stat-box dc-stat-click" onclick="switchDataTab('governance')"><div class="lab">数据源状态</div><div class="num" style="color:var(--green)">正常</div></div>
  </div>`;

  html += `<div class="work-grid" style="grid-template-columns:repeat(4,1fr)">`;
  for (let i = 1; i <= 4; i++) {
    const s = (d.domain_resources || []).find(x => x.domain === i) || {};
    html += `<div class="dc-domain-card" style="cursor:pointer" onclick="dataDomain=${i};switchDataTab('resources')">
      <div class="dc-dom-ico">${['','🏗️','🚌','💧','🏙️'][i]}</div>
      <div class="dc-dom-name">${domNames[i]}</div>
      <div class="dc-dom-stats">
        <span>资源 <b>${s.resources || 0}</b> 项</span>
        <span>指标 <b>${s.indicators || 0}</b> 项</span>
      </div></div>`;
  }
  html += `</div>

  <div class="panel" style="margin-top:22px">
    <div class="panel-head"><div class="t">🔌 数据源接入状态</div></div>
    <div class="source-grid" id="sourceGrid"></div></div>`;

  body.innerHTML = html;

  // 数据源状态
  const srcs = await api('/api/data-sources');
  if (srcs && srcs.code === 200) {
    document.getElementById('sourceGrid').innerHTML = (srcs.data || []).map(s => `
      <div class="source-item">
        <span class="src-dot ${s.status === '在线' ? 'dot-green' : s.status === '异常' ? 'dot-red' : 'dot-gray'}"></span>
        <span class="src-name">${s.name}</span><span class="src-freq">${s.freq}</span>
        <span class="src-time">${s.last_update || '-'}</span>
      </div>`).join('');
  }
}

/* -- 数据资源目录 -- */
async function renderDataResources() {
  const body = document.getElementById('dcBody');
  const domLabels = ['全部', '城乡建设', '交通运输', '水利水务', '城市管理', '综合'];
  let fhtml = `<div class="toolbar">${domLabels.map((l, i) =>
    `<div class="tab ${dataDomain === i ? 'active' : ''}" onclick="dataDomain=${i};renderDataResources()">${l}</div>`).join('')}</div>`;
  fhtml += `<div id="resList"></div>`;
  body.innerHTML = fhtml;

  const q = dataDomain ? '?domain=' + dataDomain : '';
  const data = await api('/api/data-resources' + q);
  if (!data || data.code !== 200) { document.getElementById('resList').innerHTML = '<div class="empty">加载失败</div>'; return; }
  const list = data.data || [];

  if (!list.length) { document.getElementById('resList').innerHTML = '<div class="empty">暂无数据资源</div>'; return; }
  document.getElementById('resList').innerHTML = `<div class="dc-res-grid">${list.map(r => `
    <div class="dc-res-card dc-res-click" onclick="showResDetail(${r.id},'${_esc(r.name)}')">
      <div class="dc-res-head">
        <span class="dc-res-ico">${['','🏗️','🚌','💧','🏙️','📋'][r.domain] || '📋'}</span>
        <span class="dc-res-domain">${r.domain_name}</span>
      </div>
      <div class="dc-res-name">${r.name}</div>
      <div class="dc-res-meta">
        <span>来源：${r.source_system || '-'}</span>
        <span>表名：${r.table_name || '-'}</span>
        <span>更新：${r.update_freq || '-'}</span>
        <span>记录：${r.record_count ?? '-'}</span>
      </div>
      <div class="dc-res-desc">${r.description || ''}</div>
      ${r.fields_schema ? `<div class="dc-res-fields">${(function(){
        try { return JSON.parse(r.fields_schema).map(f => `<code>${f.name}</code>`).join(' '); }
        catch(e) { return ''; }
      })()}</div>` : ''}
    </div>`).join('')}</div>`;
}

/* -- 指标看板 -- */
async function renderDataIndicators() {
  const body = document.getElementById('dcBody');
  const domLabels = ['全部', '城乡建设', '交通运输', '水利水务', '城市管理'];
  let fhtml = `<div class="toolbar">${domLabels.map((l, i) =>
    `<div class="tab ${dataDomain === i ? 'active' : ''}" onclick="dataDomain=${i};renderDataIndicators()">${l}</div>`).join('')}
    <span style="margin-left:auto;color:var(--txt-3);font-size:13px">点击行查看趋势</span></div>`;
  fhtml += `<div id="indList"></div><div id="indDetail" style="display:none;margin-top:18px"></div>`;
  body.innerHTML = fhtml;

  const q = dataDomain ? '?domain=' + dataDomain : '';
  const data = await api('/api/indicators' + q);
  if (!data || data.code !== 200) { document.getElementById('indList').innerHTML = '<div class="empty">加载失败</div>'; return; }
  const list = data.data || [];

  if (!list.length) { document.getElementById('indList').innerHTML = '<div class="empty">暂无指标</div>'; return; }
  document.getElementById('indList').innerHTML = `
    <table class="tbl"><thead><tr>
      <th style="width:100px">编码</th><th>指标名称</th><th style="width:70px">领域</th>
      <th style="width:80px">单位</th><th style="width:100px">最新值</th>
      <th style="width:200px">计算口径</th>
    </tr></thead><tbody>${list.map(ind => `
      <tr style="cursor:pointer" onclick="showIndicatorTrend('${ind.code}','${ind.name}','${ind.unit}')">
        <td><code>${ind.code}</code></td><td>${ind.name}</td>
        <td><span class="tag tag-blue">${ind.domain_name}</span></td>
        <td>${ind.unit}</td>
        <td id="val_${ind.code}" style="font-weight:600">—</td>
        <td style="font-size:12px;color:var(--txt-3)">${(ind.calc_expr || '').slice(0, 40)}</td>
      </tr>`).join('')}</tbody></table>`;

  // 异步加载指标最新值
  for (const ind of list) {
    const vd = await api('/api/indicators/' + ind.code + '/data');
    if (vd && vd.code === 200) {
      const v = vd.data && vd.data.latest;
      if (v) document.getElementById('val_' + ind.code).textContent = v.value + ' ' + ind.unit;
    }
  }
}

async function showIndicatorTrend(code, name, unit) {
  const detail = document.getElementById('indDetail');
  detail.style.display = 'block';
  detail.innerHTML = `<div class="panel"><div class="panel-head"><div class="t">📈 ${name}（${code}）</div></div>
    <div id="indChart" style="color:var(--txt-3)">加载中...</div></div>`;
  const vd = await api('/api/indicators/' + code + '/data');
  if (!vd || vd.code !== 200) { document.getElementById('indChart').innerHTML = '加载失败'; return; }
  const vals = (vd.data && vd.data.trend) || [];
  if (!vals.length) { document.getElementById('indChart').innerHTML = '<div class="empty">暂无数据</div>'; return; }
  const max = Math.max(...vals.map(v => v.value));
  document.getElementById('indChart').innerHTML = `
    <div style="display:flex;gap:8px;align-items:flex-end;height:140px;padding-top:10px">${vals.map(v => {
      const h = Math.max(8, (v.value / max) * 120);
      return `<div style="flex:1;text-align:center;font-size:11px;color:var(--txt-3)">
        <div style="height:${h}px;background:linear-gradient(180deg,var(--cyan),rgba(0,212,255,.2));border-radius:6px 6px 0 0;margin-bottom:6px;position:relative" title="${v.value} ${unit}">
          <span style="position:absolute;top:-18px;left:50%;transform:translateX(-50%);color:var(--txt);font-weight:600;font-size:12px">${v.value}</span>
        </div>${v.period}</div>`;
    }).join('')}</div>`;
}

/* 数据资源详情弹窗 */
async function showResDetail(id, name) {
  const data = await api('/api/data-resources/' + id);
  if (!data || data.code !== 200) { showToast('加载失败', 'warn'); return; }
  const r = data.data;
  let fieldsHtml = '';
  if (r.fields_schema) {
    try {
      const fields = JSON.parse(r.fields_schema);
      fieldsHtml = `<div class="ov-section-title">📋 字段 schema</div>
        <div class="ov-detail-table"><table><thead><tr><th>字段名</th><th>类型</th><th>说明</th></tr></thead><tbody>
        ${fields.map(f => `<tr><td><code>${f.name}</code></td><td>${f.type || '-'}</td><td>${f.comment || '-'}</td></tr>`).join('')}
        </tbody></table></div>`;
    } catch(e) {}
  }
  showOvModal(name, `
    <div class="ov-summary-card">
      <div><strong>来源系统</strong><div>${r.source_system || '-'}</div></div>
      <div><strong>表名</strong><div>${r.table_name || '-'}</div></div>
      <div><strong>记录数</strong><div>${r.record_count ?? '-'}</div></div>
      <div><strong>更新频率</strong><div>${r.update_freq || '-'}</div></div>
    </div>
    <div class="ov-section-title">📝 数据描述</div>
    <p style="color:var(--text-2);font-size:13px;line-height:1.7">${r.description || '暂无描述'}</p>
    ${fieldsHtml}
  `, { width: 640 });
}

/* -- 数据治理：一个数据一个源头 -- */
async function renderDataGovernance() {
  const body = document.getElementById('dcBody');
  body.innerHTML = '<div class="loading">加载数据治理信息...</div>';

  const [gov, resList, indList] = await Promise.all([
    api('/api/data-governance'),
    api('/api/data-resources'),
    api('/api/indicators'),
  ]);

  if (!gov || gov.code !== 200) { body.innerHTML = '<div class="empty">加载失败</div>'; return; }
  const g = gov.data;

  const domNames = { 1: '城乡建设', 2: '交通运输', 3: '水利水务', 4: '城市管理', 5: '综合' };
  const deptIcon = {
    '办公室': '📋', '政策法规处': '⚖️', '政务服务处': '🏛️', '城乡发展处': '🏗️',
    '房屋管理处': '🏠', '工程质量安全处': '🛡️', '建筑市场处': '📐', '综合交通组': '🚌',
    '水利组': '💧', '城市管理处': '🏙️', '城市建设监察处': '🔍', '信息化处': '💻'
  };

  let html = '';

  // ===== 一、治理总览卡片 =====
  html += `<div class="gov-header">
    <div class="gov-badge">🔗 一个数据 · 一个源头</div>
    <div class="gov-sub">每项政务数据有且仅有一个权威来源系统、一个归属责任处室、一个明确责任人</div>
  </div>`;

  html += `<div class="stat-row" style="grid-template-columns:repeat(5,1fr);margin-bottom:20px">
    <div class="stat-box dc-stat-click" onclick="switchDataTab('catalog')"><div class="lab">数据资源总数</div><div class="num">${g.resource_count}</div></div>
    <div class="stat-box dc-stat-click" onclick="switchDataTab('indicators')"><div class="lab">标准指标数</div><div class="num">${g.indicator_count}</div></div>
    <div class="stat-box dc-stat-click" onclick="switchDataTab('governance')"><div class="lab">处室覆盖率</div><div class="num" style="color:${g.coverage.overall_pct >= 90 ? 'var(--green)' : 'var(--orange)'}">${g.coverage.overall_pct}%</div></div>
    <div class="stat-box dc-stat-click" onclick="switchDataTab('catalog')"><div class="lab">源头系统数</div><div class="num">${g.source_systems.length}</div></div>
    <div class="stat-box dc-stat-click" onclick="switchDataTab('governance')"><div class="lab">责任人明确率</div><div class="num" style="color:${g.coverage.resource_person_pct >= 90 ? 'var(--green)' : 'var(--orange)'}">${g.coverage.resource_person_pct}%</div></div>
  </div>`;

  // ===== 二、处室数据归属分布 =====
  html += `<div class="panel" style="margin-bottom:20px">
    <div class="panel-head"><div class="t">📊 处室数据归属分布（一处室一颜色，谁的数据谁负责）</div></div>
    <div class="gov-dept-grid">`;
  const sortedDepts = (g.dept_ownership || []).sort((a, b) => (b.resources + b.indicators) - (a.resources + a.indicators));
  for (const d of sortedDepts) {
    const total = d.resources + d.indicators;
    const pct = g.total_items > 0 ? Math.round(total / g.total_items * 100) : 0;
    html += `<div class="gov-dept-card">
      <div class="gov-dept-icon">${deptIcon[d.dept] || '📌'}</div>
      <div class="gov-dept-name">${d.dept}</div>
      <div class="gov-dept-bar-wrap"><div class="gov-dept-bar" style="width:${Math.max(pct, 2)}%"></div></div>
      <div class="gov-dept-nums"><span>资源 ${d.resources}</span><span>指标 ${d.indicators}</span><span class="gov-dept-pct">${pct}%</span></div>
    </div>`;
  }
  html += `</div></div>`;

  // ===== 三、数据资源源头详表 =====
  const resources = (resList && resList.code === 200) ? (resList.data || []) : [];
  html += `<div class="panel" style="margin-bottom:20px">
    <div class="panel-head"><div class="t">📁 数据资源源头详表<small style="font-weight:400;margin-left:8px;color:var(--txt-3)">每行 = 一条数据 + 一个源头</small></div></div>
    <div class="gov-table-wrap">
    <table class="tbl gov-tbl">
      <thead><tr>
        <th style="width:40px">#</th>
        <th style="width:130px">数据名称</th>
        <th style="width:64px">领域</th>
        <th style="width:60px">类型</th>
        <th style="width:140px">唯一源头系统</th>
        <th style="width:80px">责任处室</th>
        <th style="width:60px">责任人</th>
        <th style="width:56px">更新</th>
        <th style="width:52px">质量</th>
      </tr></thead>
      <tbody>`;

  if (resources.length === 0) {
    html += `<tr><td colspan="9" class="text-center" style="color:var(--txt-3);padding:24px">暂无数据资源</td></tr>`;
  } else {
    resources.forEach((r, i) => {
      const qCls = r.quality_status === '良好' ? 'q-good' : r.quality_status === '一般' ? 'q-ok' : 'q-bad';
      html += `<tr class="gov-row-click" onclick="showResDetail(${r.id},'${_esc(r.name)}')">
        <td style="color:var(--txt-3)">${i + 1}</td>
        <td class="gov-res-name" title="${r.description || ''}">${r.name}</td>
        <td><span class="tag tag-blue" style="font-size:11px">${r.domain_name}</span></td>
        <td><span class="gov-type-tag">${r.data_type || '-'}</span></td>
        <td class="gov-src-cell">${r.source_system || '-'}</td>
        <td><span class="dept-chip">${r.owner_dept || '—'}</span></td>
        <td style="font-weight:500">${r.owner_person || '—'}</td>
        <td><span class="gov-freq">${r.update_freq || '-'}</span></td>
        <td><span class="gov-qual ${qCls}">${r.quality_status || '-'}</span></td>
      </tr>`;
    });
  }
  html += `</tbody></table></div></div>`;

  // ===== 四、指标源头详表 =====
  const indicators = (indList && indList.code === 200) ? (indList.data || []) : [];
  html += `<div class="panel" style="margin-bottom:20px">
    <div class="panel-head"><div class="t">📊 标准指标源头详表<small style="font-weight:400;margin-left:8px;color:var(--txt-3)">${indicators.length}项指标，每项有唯一责任处室</small></div></div>
    <div class="gov-table-wrap">
    <table class="tbl gov-tbl">
      <thead><tr>
        <th style="width:40px">#</th>
        <th style="width:60px">编码</th>
        <th style="width:120px">指标名称</th>
        <th style="width:64px">领域</th>
        <th style="width:120px">数据源头</th>
        <th style="width:80px">责任处室</th>
        <th style="width:60px">责任人</th>
        <th style="width:56px">更新</th>
      </tr></thead>
      <tbody>`;

  if (indicators.length === 0) {
    html += `<tr><td colspan="8" class="text-center" style="color:var(--txt-3);padding:24px">暂无指标</td></tr>`;
  } else {
    indicators.forEach((ind, i) => {
      html += `<tr class="gov-row-click" onclick="showIndicatorTrend('${ind.code}','${_esc(ind.name)}','${ind.unit}')">
        <td style="color:var(--txt-3)">${i + 1}</td>
        <td><code>${ind.code}</code></td>
        <td class="gov-res-name">${ind.name} <span style="font-size:11px;color:var(--txt-3)">${ind.unit}</span></td>
        <td><span class="tag tag-blue" style="font-size:11px">${ind.domain_name}</span></td>
        <td class="gov-src-cell">${ind.source_system || '-'}</td>
        <td><span class="dept-chip">${ind.owner_dept || '—'}</span></td>
        <td style="font-weight:500">${ind.owner_person || '—'}</td>
        <td><span class="gov-freq">${ind.update_freq || '-'}</span></td>
      </tr>`;
    });
  }
  html += `</tbody></table></div></div>`;

  // ===== 五、源头系统清单 =====
  html += `<div class="panel">
    <div class="panel-head"><div class="t">🔌 数据源头系统清单<small style="font-weight:400;margin-left:8px;color:var(--txt-3)">共 ${g.source_systems.length} 个源头系统</small></div></div>
    <div class="source-grid">`;
  for (const s of g.source_systems) {
    html += `<div class="source-item">
      <span class="src-dot dot-green"></span>
      <span class="src-name">${s.system}</span>
      <span class="src-freq">${s.item_count} 项数据</span>
      <span class="src-time" style="color:var(--green)">◎ 唯一源头</span>
    </div>`;
  }
  html += `</div></div>`;

  body.innerHTML = html;
}

/* ---------- 专属智能体 ---------- */
let aiSubTab = 'chat';  // chat | warnings | analyze | decide
let chatHistory = [];

async function renderAI() {
  const subTabs = [
    ['chat', '💬 智能对话'],
    ['warnings', '⚠️ 智能预警'],
    ['analyze', '📝 智能分析'],
    ['decide', '🧠 智能决策'],
  ];

  let html = `<div class="page-head"><div class="page-title">🤖 专属智能体<small>AI赋能预警、分析、决策、处置</small></div></div>
    <div class="tabs">${subTabs.map(([k, name]) => `<div class="subtab ${k===aiSubTab?'active':''}" onclick="aiSubTab='${k}';renderAI()">${name}</div>`).join('')}</div>
    <div id="aiBody"></div>`;
  document.getElementById('content').innerHTML = html;

  if (aiSubTab === 'chat') renderAIChat();
  else if (aiSubTab === 'warnings') renderAIWarnings();
  else if (aiSubTab === 'analyze') renderAIAnalyze();
  else if (aiSubTab === 'decide') renderAIDecide();
}

/* -- 智能对话（自然语言版 v2） -- */
function renderAIChat() {
  const body = document.getElementById('aiBody');
  const hour = new Date().getHours();
  const greet = hour < 6 ? '夜深了' : hour < 12 ? '上午好' : hour < 14 ? '中午好' : hour < 18 ? '下午好' : '晚上好';
  const userName = (currentUser && (currentUser.real_name || currentUser.username)) || '您好';

  body.innerHTML = `
    <div class="ai-chat-wrap">
      <div class="ai-chat-list" id="aiChatList">
        <div class="ai-msg bot">
          <div class="ai-avatar">🤖</div>
          <div class="ai-bubble">
            <div class="ai-bubble-title">建交协同调度中心 · AI 智能体</div>
            <div class="ai-bubble-meta">v2.0 · 自然语言生成引擎 · ${new Date().toLocaleString('zh-CN', { hour12: false })}</div>
            <div class="ai-bubble-content">${greet}，${userName}！我是您的专属智能助手小安。融合了数据中枢、态势感知和规则引擎，可以为您：</div>
            <ul class="ai-cap-list">
              <li>🛰️ 实时回答系统运行态势（项目、指标、预警、待办）</li>
              <li>📊 按领域深入分析指标和项目阶段</li>
              <li>🏗️ 查询具体项目阶段、风险和审批进度</li>
              <li>📝 自动生成月度态势分析报告</li>
              <li>🧠 基于场景给出决策建议</li>
              <li>📋 智能分派异常事件为待办工单</li>
            </ul>
            <div class="ai-bubble-hint">您可以这样问我：</div>
            <div class="ai-quick-actions">
              <button onclick="aiQuickAsk('当前系统整体运行情况怎么样')">📊 系统整体态势</button>
              <button onclick="aiQuickAsk('城乡建设领域有什么需要关注的')">🏗️ 城乡建设分析</button>
              <button onclick="aiQuickAsk('当前有哪些预警需要处理')">⚠️ 当前预警</button>
              <button onclick="aiQuickAsk('逾期项目该怎么处置')">🧠 逾期项目决策</button>
              <button onclick="aiQuickAsk('生成本月水利水务分析报告')">📝 月度报告</button>
            </div>
          </div>
        </div>
      </div>
      <div class="ai-input-row">
        <input id="aiInput" class="ai-input" placeholder="用自然语言描述您的问题…（如：帮我分析下交通领域的现状）" onkeydown="if(event.key==='Enter')aiSend()">
        <button class="btn-go" onclick="aiSend()">发送</button>
      </div>
    </div>`;
}

function _esc(s) {
  return String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

function _renderBubbleText(text) {
  // 简单的 markdown-lite: 换行 + 项目符号 + 强调
  let html = _esc(text);
  // 加粗 **xxx**
  html = html.replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>');
  // 高亮 [xxx] 标签
  html = html.replace(/\[(.*?)\]/g, '<span class="ai-tag">$1</span>');
  // 风险符号上色
  html = html.replace(/(🔴|🟡|🟢|⚠️|✅|🚨|💧|🏗️|🧠|📊|📝|📋|🛰️|🔔|💬|👋|📈|🚌|🌊)/g, '<span class="ai-emoji">$1</span>');
  // 数字高亮（整数/百分比/小数）
  html = html.replace(/(?<![\w.])(\d+(?:\.\d+)?(?:%|个|项|条|km|m|人|元|亿|万吨|分钟|小时|天)?)/g, '<span class="ai-num">$1</span>');
  // 换行
  html = html.replace(/\n/g, '<br>');
  return html;
}

async function aiSend() {
  const input = document.getElementById('aiInput');
  const query = input.value.trim();
  if (!query) return;
  input.value = '';

  const list = document.getElementById('aiChatList');
  const ts = new Date().toLocaleTimeString('zh-CN', { hour12: false });
  // 用户消息
  list.insertAdjacentHTML('beforeend',
    `<div class="ai-msg user">
      <div class="ai-avatar user-avatar">${_esc((currentUser && currentUser.real_name || 'U').slice(0,1))}</div>
      <div class="ai-bubble user-bubble">
        <div class="ai-bubble-content">${_esc(query)}</div>
        <div class="ai-bubble-meta">${ts}</div>
      </div>
    </div>`);

  // 思考中
  const typingId = 'typing_' + Date.now();
  list.insertAdjacentHTML('beforeend',
    `<div class="ai-msg bot" id="${typingId}">
      <div class="ai-avatar">🤖</div>
      <div class="ai-bubble">
        <div class="ai-typing"><span></span><span></span><span></span> 正在分析数据…</div>
      </div>
    </div>`);
  list.scrollTop = list.scrollHeight;

  // 仅传最近 6 轮历史，避免请求过大
  const recentHistory = chatHistory.slice(-6);
  const data = await api('/api/ai/chat', { method: 'POST', body: JSON.stringify({ query, history: recentHistory }) });

  const typing = document.getElementById(typingId);
  if (!typing) return;
  if (data && data.code === 200) {
    const reply = data.data.reply || '';
    const followups = data.data.followups || [];
    const sources = data.data.sources || [];
    const kbSuggestions = data.data.kb_suggestions || [];
    const ents = data.data.entities || {};
    let entTag = '';
    if (ents.domains && ents.domains.length) entTag += `<span class="ai-tag">${_esc(ents.domains.join('/'))}</span> `;
    if (ents.projects && ents.projects.length) entTag += `<span class="ai-tag">项目：${_esc(ents.projects[0])}</span> `;
    if (ents.time_range) entTag += `<span class="ai-tag">时间：${_esc(ents.time_range)}</span> `;
    if (ents.topic && ents.topic !== 'general') entTag += `<span class="ai-tag ai-tag-external">联网检索 · ${_esc(ents.topic)}</span> `;
    if (entTag) entTag = `<div class="ai-ents">${entTag}</div>`;

    let followupHtml = '';
    if (followups.length) {
      followupHtml = `<div class="ai-followups">${followups.map(f =>
        `<button onclick="aiQuickAsk(${JSON.stringify(f)})">${_esc(f)}</button>`).join('')}</div>`;
    }

    // 来源卡片（联网检索）
    let sourcesHtml = '';
    if (sources.length) {
      sourcesHtml = `<div class="ai-sources">
        <div class="ai-sources-head">📚 参考来源（来自公开网络）</div>
        ${sources.map((s, i) => `
          <a class="ai-source-card" href="${_esc(s.url)}" target="_blank" rel="noopener">
            <div class="ai-source-num">${i+1}</div>
            <div class="ai-source-body">
              <div class="ai-source-title">${_esc(s.title)}</div>
              <div class="ai-source-snippet">${_esc(s.snippet || '')}</div>
              <div class="ai-source-url">${_esc(s.url)}</div>
            </div>
          </a>`).join('')}
      </div>`;
    }

    // 知识库补全建议
    let kbHtml = '';
    if (kbSuggestions.length) {
      kbHtml = `<div class="ai-kb-suggest">
        <div class="ai-kb-head">💡 建议补全到本地知识库</div>
        <ul class="ai-kb-list">${kbSuggestions.map(s => `<li>📄 ${_esc(s)}</li>`).join('')}</ul>
        <div class="ai-kb-tip">系统管理 → 知识库管理 上传 PDF/Word，自动解析后即可语义检索。</div>
      </div>`;
    }

    typing.querySelector('.ai-bubble').innerHTML = `
      <div class="ai-bubble-title">小安</div>
      <div class="ai-bubble-meta">${new Date().toLocaleTimeString('zh-CN', { hour12: false })}${sources.length ? ' · 🌐 联网检索' : ''}</div>
      ${entTag}
      <div class="ai-bubble-content">${_renderBubbleText(reply)}</div>
      ${sourcesHtml}
      ${kbHtml}
      ${followupHtml}
    `;
    chatHistory.push({ role: 'user', content: query });
    chatHistory.push({ role: 'assistant', content: reply });
    if (chatHistory.length > 30) chatHistory = chatHistory.slice(-30);
  } else {
    typing.querySelector('.ai-bubble').innerHTML = `<div class="ai-bubble-content">⚠️ 对话服务暂不可用，请稍后再试。</div>`;
  }
  list.scrollTop = list.scrollHeight;
}

function aiQuickAsk(q) { const i = document.getElementById('aiInput'); i.value = q; aiSend(); }

/* -- 智能预警 -- */
async function renderAIWarnings() {
  const body = document.getElementById('aiBody');
  body.innerHTML = '<div class="empty">分析中...</div>';
  const data = await api('/api/ai/warnings');
  if (!data || data.code !== 200) { body.innerHTML = '<div class="empty">加载失败</div>'; return; }
  const d = data.data;

  body.innerHTML = `
    <div class="ai-result-card">
      <div class="ai-result-head">🔍 智能预警扫描报告</div>
      <div class="ai-result-meta">检查项：${d.stats.total_checks} 项 · 触发预警：${d.stats.triggered} 项 · 紧急待办：${d.stats.urgent_todos} 项 · 逾期项目：${d.stats.overdue_projects} 个</div>
      <div class="ai-summary">${d.summary}</div>
      ${d.alerts.length ? `<div class="ai-alert-list">${d.alerts.map(a => `
        <div class="ai-alert-item ${a.severity} ai-alert-click" onclick="navTo('/topic')">
          <div class="ai-alert-head"><span class="tag ${a.severity==='high'?'tag-red':'tag-orange'}">${a.severity==='high'?'高':'中'}</span> ${a.indicator}: <b>${a.value} ${a.unit}</b></div>
          <div class="ai-alert-advice">💡 ${a.advice}</div>
        </div>`).join('')}</div>` : '<div class="empty">✅ 所有指标正常</div>'}
      <button class="btn-ghost" onclick="renderAIWarnings()" style="margin-top:12px">↻ 重新扫描</button>
    </div>`;
}

/* -- 智能分析 -- */
async function renderAIAnalyze() {
  const body = document.getElementById('aiBody');
  body.innerHTML = `
    <div class="ai-result-card">
      <div class="ai-result-head">📝 智能分析报告</div>
      <p style="color:var(--txt-2);font-size:13px;margin-bottom:16px">选择分析领域，系统将基于当前指标数据生成月度态势分析报告。</p>
      <div class="toolbar">
        <button class="tab active" onclick="runAnalysis(0)">🌐 全局</button>
        <button class="tab" onclick="runAnalysis(1)">🏗️ 城乡建设</button>
        <button class="tab" onclick="runAnalysis(2)">🚌 交通运输</button>
        <button class="tab" onclick="runAnalysis(3)">💧 水利水务</button>
        <button class="tab" onclick="runAnalysis(4)">🏙️ 城市管理</button>
      </div>
      <div id="aiAnalysisContent"></div>
    </div>`;
  await runAnalysis(0);
}

async function runAnalysis(domain) {
  const content = document.getElementById('aiAnalysisContent');
  content.innerHTML = '<div class="empty">生成中...</div>';
  const data = await api('/api/ai/analyze', { method: 'POST', body: JSON.stringify({ domain }) });
  if (!data || data.code !== 200) { content.innerHTML = '<div class="empty">生成失败</div>'; return; }

  content.innerHTML = data.data.analyses.map(a => `
    <div class="ai-analysis-block">
      <div class="ai-analysis-title">${a.name}领域分析</div>
      <div class="ai-analysis-body">${a.content}</div>
      <div class="ai-analysis-hl">
        ${a.highlights.map(h => `<span class="hl-item">✅ ${h}</span>`).join('')}
      </div>
    </div>`).join('')
    + `<div class="ai-report-footer">📅 生成时间：${data.data.generated_at} · 引擎：${data.data.model}</div>`;
}

/* -- 智能决策 -- */
async function renderAIDecide() {
  const body = document.getElementById('aiBody');
  body.innerHTML = `
    <div class="ai-result-card">
      <div class="ai-result-head">🧠 智能决策建议</div>
      <p style="color:var(--txt-2);font-size:13px;margin-bottom:16px">选择决策场景，系统将基于规则引擎给出分步骤决策建议。</p>
      <div class="toolbar">
        <button class="tab active" onclick="runDecide('default')">📋 日常调度</button>
        <button class="tab" onclick="runDecide('flood')">🌊 防汛应急</button>
        <button class="tab" onclick="runDecide('overdue')">⏰ 逾期处置</button>
      </div>
      <div id="aiDecideContent"></div>
    </div>`;
  await runDecide('default');
}

async function runDecide(scenario) {
  const content = document.getElementById('aiDecideContent');
  content.innerHTML = '<div class="empty">分析中...</div>';
  const data = await api('/api/ai/decide', { method: 'POST', body: JSON.stringify({ scenario }) });
  if (!data || data.code !== 200) { content.innerHTML = '<div class="empty">生成失败</div>'; return; }
  const d = data.data;

  content.innerHTML = `
    <div class="ai-decision-title">📋 ${d.title}</div>
    <div class="ai-reasoning">🧠 推理依据：${d.reasoning}</div>
    <div class="ai-action-list">
      ${d.actions.map(a => `
        <div class="ai-action-item">
          <span class="ai-step">${a.step}</span>
          <div class="ai-action-body">
            <div class="ai-action-name">${a.action}</div>
            <div class="ai-action-meta"><span>责任处室：${a.dept}</span><span class="tag ${a.urgency==='紧急'?'tag-red':a.urgency==='高'?'tag-orange':'tag-blue'}">${a.urgency}</span></div>
          </div>
        </div>`).join('')}
    </div>`;
}

/* ---------- 业务专题一张图 ---------- */
let topicDomain = 1;  // 当前专题领域

/* 跨处室业务线（来源：2026年上半年工作总结） */
const TOPIC_CONFIG = {
  1: { name: '项目全生命周期', icon: '🏗️', color: '#00d4ff',
       desc: '贯穿政务服务处→质量安全处→城乡发展处→监察处→房屋处，施工许可200+件/审批1.5日/联合验收100+项目',
       departments: ['政务服务处','工程质量安全处','城乡发展处','城市建设监察处','房屋管理处'],
       stats: [
         { label: '施工许可审批', value: '200+', unit: '件' },
         { label: '平均审批用时', value: '1.5', unit: '天' },
         { label: '联合验收项目', value: '100+', unit: '个' },
         { label: '新竣备楼栋', value: '90+', unit: '栋' },
         { label: '竣备建筑面积', value: '70+', unit: '万m²' },
         { label: '帮办服务覆盖', value: '41', unit: '个疏解项目' },
       ],
       metrics: [
         { name: '施工许可月受理量', trend: [165,178,192,188,200,210], unit: '件' },
         { name: '联合验收月办结量', trend: [11,14,18,16,19,22], unit: '件' },
       ],
       highlights: ['审批时间压缩至1.5天', '竣工一件事功能开发中', '全生命周期帮办服务体系初步形成', '一北片区技术底板初验完成'] },
  2: { name: '城建综合监管', icon: '🛡️', color: '#ff5252',
       desc: '建筑市场处+质量安全处+监察处联动，检查780次/问题闭环2774项/实名制全覆盖/137条异常线索全部闭合',
       departments: ['建筑市场处','工程质量安全处','城市建设监察处','政策法规处'],
       stats: [
         { label: '现场检查', value: '780', unit: '次' },
         { label: '发现问题', value: '2774', unit: '项(全部闭环)' },
         { label: '实名制覆盖率', value: '100', unit: '%' },
         { label: '异常线索核查', value: '137', unit: '条(全部闭合)' },
         { label: '施工图审查', value: '100', unit: '%' },  // 抽查→100%审查
         { label: '行政处罚', value: '712,146.82', unit: '元' },
       ],
       metrics: [
         { name: '月度安全检查次数', trend: [110,125,135,128,142,140], unit: '次' },
         { name: '问题整改闭环率', trend: [92,95,97,98,99,100], unit: '%' },
       ],
       highlights: ['变施工图抽查为100%审查', '印发“六个到位”50项实施方法', '实名制系统与银行端数据直连', '小施工安全管理11场培训1200+人次'] },
  3: { name: '防洪排涝协同', icon: '🌊', color: '#69f0ae',
       desc: '水利组+城管处+交通处联动，1000+防汛责任人/153处隐患整改/枣林庄枢纽+留通泵站/联排联调体系',
       departments: ['水利组','城市管理处','综合交通处'],
       stats: [
         { label: '防汛责任人', value: '1000+', unit: '人' },
         { label: '隐患整改', value: '153', unit: '处' },
         { label: '泵站排涝能力', value: '3', unit: '座(主汛期前)' },
         { label: '白洋淀补水', value: '10+', unit: '亿m³' },
         { label: '河湖巡查', value: '14', unit: '次(涉河问题305个)' },
         { label: '在建防洪项目', value: '6+', unit: '个' },
       ],
       metrics: [
         { name: '白洋淀水位(m)', trend: [6.8, 6.9, 7.0, 7.2, 7.5, 7.6], unit: 'm' },
         { name: '泵站排涝流量', trend: [0,0,0,45,60,80], unit: 'm³/s' },
       ],
       highlights: ['雄安干渠全线贯通', '应急水源工程试运行', '新增供水4万吨/日', '留通/昝岗西泵站主汛期前达标'] },
  4: { name: '绿色降碳创新', icon: '🌱', color: '#ffb300',
       desc: '城乡发展处+质量安全处+信息化处协同，45项示范/装配式32%/“7+1”指标体系/BIM4审查/碳排管理平台一期建成',
       departments: ['城乡发展处','工程质量安全处','信息化处'],
       stats: [
         { label: '绿建示范项目', value: '45', unit: '项' },
         { label: '装配式建造占比', value: '32', unit: '%' },
         { label: '三星级绿建', value: '100', unit: '%(政府投资)' },
         { label: '碳排放测评试点', value: '13', unit: '个' },
         { label: '建材码覆盖', value: '135', unit: '种材料' },
         { label: '星级智慧工地', value: '25', unit: '个' },
       ],
       metrics: [
         { name: '装配式建造占比(%)', trend: [25,28,30,31,32,32], unit: '%' },
         { name: '绿建示范项目(累计)', trend: [25,32,38,40,43,45], unit: '项' },
       ],
       highlights: ['碳排管理平台一期建成', 'BIM4审查以图模一致为核心', '建筑垃圾全流程线上监管', '城建档案数字平台试运行'] },
  5: { name: '城市运营一网统管', icon: '🏙️', color: '#e040fb',
       desc: '城管处+信息化处+各业务处室，运管服平台处置2万+事件/71家物业全覆盖/29.7万户安检/7000km管网检测',
       departments: ['城市管理处','信息化处','房屋管理处','综合交通处','水利组'],
       stats: [
         { label: '运管服处置事件', value: '20000+', unit: '件' },
         { label: '物业服务企业', value: '71', unit: '家(全覆盖)' },
         { label: '燃气入户安检', value: '29.7万', unit: '户' },
         { label: '燃气管网检测', value: '7000+', unit: 'km' },
         { label: '垃圾分类设施', value: '75', unit: '处(新增)' },
         { label: '供水保障', value: '4', unit: '万吨/日(新增)' },
       ],
       metrics: [
         { name: '运管服月处置事件', trend: [2800,3200,3500,3300,3700,3500], unit: '件' },
         { name: '供热优质率(≥21℃)', trend: [91,92,93,94,95,95], unit: '%' },
       ],
       highlights: ['“一委一办一平台”机制做实', '容东19个社区物业重新选聘', '外摆位管理办法印发', '721工作法全面推行'] },
};

async function renderTopic() {
  const cfg = TOPIC_CONFIG[topicDomain];
  const tabs = Object.entries(TOPIC_CONFIG).map(([k, v]) =>
    `<div class="subtab ${+k===topicDomain?'active':''}" onclick="topicDomain=${k};renderTopic()">${v.icon} ${v.name}</div>`).join('');

  let html = `<div class="page-head"><div class="page-title">🗺️ 业务专题一张图<small>跨处室业务线 · 来源：2026年上半年工作总结</small></div></div>
    <div class="tabs">${tabs}</div><div id="topicBody"></div>`;
  document.getElementById('content').innerHTML = html;
  await loadTopicContent(cfg);
}

async function loadTopicContent(cfg) {
  const body = document.getElementById('topicBody');
  
  // 加载专题工作台数据
  const wb = await api('/api/topic-workbench/' + topicDomain);
  const w = (wb && wb.code === 200) ? wb.data : null;
  
  const deptChips = cfg.departments.map(d => `<span class="dept-chip" style="font-size:11px">${d}</span>`).join(' ');
  
  // ===== 顶部：待办快览条（真正的"干活"入口）=====
  let actionBar = '';
  if (w) {
    actionBar = `<div class="tp-action-row">
      <div class="tp-action-card ${w.todo_count > 0 ? 'has-items' : ''}" onclick="navTo('/todos')">
        <div class="tp-action-num">${w.todo_count}</div>
        <div class="tp-action-label">📋 待办事项</div>
        <div class="tp-action-hint">${w.todo_count > 0 ? '点击去处理' : '暂无待办 ✓'}</div>
      </div>
      <div class="tp-action-card ${w.approval_count > 0 ? 'has-items' : ''}" onclick="navTo('/project')">
        <div class="tp-action-num">${w.approval_count}</div>
        <div class="tp-action-label">📝 待审批</div>
        <div class="tp-action-hint">${w.approval_count > 0 ? w.approval_count + ' 件待审批' : '无需审批 ✓'}</div>
      </div>
      <div class="tp-action-card ${w.alert_count > 0 ? 'alerts' : ''}" onclick="navTo('/project')">
        <div class="tp-action-num" style="color:${w.alert_count > 0 ? 'var(--red)' : 'var(--green)'}">${w.alert_count}</div>
        <div class="tp-action-label">⚠️ 预警</div>
        <div class="tp-action-hint">${w.alert_count > 0 ? w.alert_count + ' 个预警待处置' : '一切正常 ✓'}</div>
      </div>
      <div class="tp-action-card" onclick="topicDomain=${topicDomain};renderTopic()">
        <div class="tp-action-num" style="font-size:18px">↻</div>
        <div class="tp-action-label">刷新</div>
        <div class="tp-action-hint">获取最新数据</div>
      </div>
    </div>`;
  }
  
  // ===== 中部：待办详情 + 预警列表（双列）=====
  let detailSection = '';
  if (w) {
    const todoItems = (w.todos || []).length
      ? w.todos.map(t => `<div class="tp-list-item" onclick="navTo('/todos')">
        <span class="dot ${t.urgency >= 3 ? 'dot-red' : t.urgency >= 2 ? 'dot-orange' : 'dot-blue'}"></span>
        <div class="tp-list-body"><div class="tp-list-title">${t.title}</div>
        <div class="tp-list-meta">${t.todo_type_name || ''} · 截止 ${t.due_date || '—'}</div></div>
        <span class="tag ${t.urgency >= 3 ? 'tag-red' : 'tag-blue'}">${t.urgency_name || ''}</span>
      </div>`).join('')
      : '<div class="empty" style="padding:20px">✅ 该业务线暂无待办事项</div>';
    
    const approvalItems = (w.pending_approvals || []).length
      ? w.pending_approvals.map(a => `<div class="tp-list-item" onclick="openProjectDetail(${a.project_id})">
        <span class="dot dot-orange"></span>
        <div class="tp-list-body"><div class="tp-list-title">${a.approval_type} · ${a.project_name || ''}</div>
        <div class="tp-list-meta">申请 ${a.apply_date || '-'} · 审批人 ${a.approver || '-'}</div></div>
        <span class="tag tag-orange">待审批</span>
      </div>`).join('')
      : '<div class="empty" style="padding:20px">✅ 该业务线暂无待审批项</div>';
    
    const alertItems = (w.alerts || []).length
      ? w.alerts.map(a => `<div class="tp-list-item" onclick="openProjectDetail(${a.project_id})" style="border-left:3px solid ${a.alert_type === 'overdue' ? 'var(--red)' : 'var(--orange)'}">
        <span class="dot ${a.alert_type === 'overdue' ? 'dot-red' : 'dot-orange'}"></span>
        <div class="tp-list-body"><div class="tp-list-title">${a.project_name || ''}</div>
        <div class="tp-list-meta">进度 ${a.progress}% · ${a.stage || ''} · ${a.alert_type === 'overdue' ? '逾期 ' + a.days + ' 天' : a.days + '天后到期'}</div></div>
        <span class="tag ${a.alert_type === 'overdue' ? 'tag-red' : 'tag-orange'}">${a.alert_type === 'overdue' ? '逾期' : '临近'}</span>
      </div>`).join('')
      : '<div class="empty" style="padding:20px">✅ 该业务线项目进度正常</div>';
    
    // 跨处室流转分布
    const flowBars = (w.flow_stats || []).length
      ? w.flow_stats.map(f => {
          const max = Math.max(...(w.flow_stats.map(x => x.items)));
          const pct = Math.round(f.items / max * 100);
          return `<div class="tp-flow-row">
            <span class="tp-flow-dept">${f.dept}</span>
            <div class="tp-flow-bar-wrap"><div class="tp-flow-bar" style="width:${pct}%;background:${cfg.color}"></div></div>
            <span class="tp-flow-num">${f.items} 项</span>
          </div>`;
        }).join('')
      : '<div class="empty" style="padding:20px">暂无流转数据</div>';
    
    detailSection = `
      <div class="tp-detail-grid">
        <div class="panel">
          <div class="panel-head"><div class="t">📋 待办事项</div><div class="more" onclick="navTo('/todos')">全部 →</div></div>
          <div class="tp-scroll-list">${todoItems}</div>
        </div>
        <div class="panel">
          <div class="panel-head"><div class="t">📝 待审批</div><div class="more" onclick="navTo('/project')">查看项目 →</div></div>
          <div class="tp-scroll-list">${approvalItems}</div>
        </div>
      </div>
      <div class="tp-detail-grid">
        <div class="panel">
          <div class="panel-head"><div class="t">⚠️ 项目进度预警</div></div>
          <div class="tp-scroll-list">${alertItems}</div>
        </div>
        <div class="panel">
          <div class="panel-head"><div class="t">🔀 跨处室流转分布</div></div>
          ${flowBars}
        </div>
      </div>`;
  }
  
  // ===== 底部：核心统计 + 亮点 =====
  const statCards = cfg.stats.map((s, idx) => `
    <div class="tp-stat-card tp-stat-click" onclick="navTo('/project')">
      <div class="tp-stat-val">${s.value}<small>${s.unit}</small></div>
      <div class="tp-stat-label">${s.label}</div>
    </div>`).join('');
  const highlightHTML = cfg.highlights.map(h => `<li>${h}</li>`).join('');
  
  body.innerHTML = `
    ${actionBar}
    <div class="section" style="margin-top:16px">
      <div class="section-title">👥 协同处室</div>
      <div style="display:flex;flex-wrap:wrap;gap:6px;margin:8px 0">${deptChips}</div>
      <div style="font-size:12px;color:var(--txt-3);margin-top:4px">${cfg.desc}</div>
    </div>
    ${detailSection}
    <div class="tp-grid" style="margin-top:16px">
      <div class="tp-main">
        <div class="section">
          <div class="section-title">📊 核心统计（来源：2026上半年总结）</div>
          <div class="tp-stat-grid">${statCards}</div>
        </div>
      </div>
      <div class="tp-side">
        <div class="section">
          <div class="section-title">✨ 工作亮点</div>
          <ul class="tp-hl-list">${highlightHTML}</ul>
        </div>
      </div>
    </div>`;
}

/* ---------- 规建管一体化 ---------- */
let projFilter = { keyword: '', ptype: '', area: '', stage: '', alert: '', my_dept: 0 };
let projViewMode = 'card';  // card | list
let expandedProject = null;
let projSubTab = 'projects';  // projects | pending | efficiency
let selectedApprovals = new Set();  // 批量审批选中集合

function _userDeptName() {
  return (currentUser && currentUser.dept_name) || '';
}

async function renderProject() {
  let html = `<div class="page-head"><div class="page-title">🏗️ 规建管运一体化<small>工程项目全生命周期管理 · 务实高效</small></div>
    <div style="display:flex;gap:8px">
      <button class="btn-ghost" onclick="exportProjectsExcel()">📥 导出台账</button>
    </div></div>`;

  // 子页签
  html += `<div class="tabs" style="margin-bottom:14px">
    <div class="tab ${projSubTab==='projects'?'active':''}" onclick="projSubTab='projects';selectedApprovals.clear();renderProject()">项目管理</div>
    <div class="tab ${projSubTab==='pending'?'active':''}" onclick="projSubTab='pending';selectedApprovals.clear();renderProject()">待我审批</div>
    <div class="tab ${projSubTab==='efficiency'?'active':''}" onclick="projSubTab='efficiency';renderProject()">审批时效</div>
  </div>`;

  document.getElementById('content').innerHTML = html + '<div id="projBody"></div>';

  if (projSubTab === 'efficiency') {
    await renderApprovalEfficiency();
  } else if (projSubTab === 'pending') {
    await renderPendingApprovals();
  } else {
    await renderProjectList();
  }
}

async function renderApprovalEfficiency() {
  const body = document.getElementById('projBody');
  body.innerHTML = '<div class="loading">加载审批时效数据...</div>';
  const data = await api('/api/approvals/efficiency');
  if (!data || data.code !== 200) { body.innerHTML = '<div class="empty">加载失败</div>'; return; }
  const d = data.data;
  const sm = d.summary;

  let html = `<div class="stat-row" style="grid-template-columns:repeat(4,1fr);margin-bottom:18px">
    <div class="stat-box proj-stat-click" onclick="navTo('/project')"><div class="lab">审批总量</div><div class="num">${sm.total_approvals}</div><div class="sub">含待办 ${sm.pending} 条</div></div>
    <div class="stat-box proj-stat-click" onclick="navTo('/project')"><div class="lab">平均审批时长</div><div class="num">${sm.avg_days}<span class="unit">天</span></div><div class="sub">${sm.avg_days <= 2 ? '高效' : sm.avg_days <= 5 ? '正常' : '偏慢'}</div></div>
    <div class="stat-box proj-stat-click" onclick="navTo('/project')" style="border-left:2px solid var(--red)"><div class="lab">超时待办</div><div class="num" style="color:${sm.overdue > 0 ? 'var(--red)' : 'var(--green)'}">${sm.overdue}</div><div class="sub">${sm.overdue > 0 ? '需催办' : '无超时 ✓'}</div></div>
    <div class="stat-box proj-stat-click" onclick="navTo('/project')" style="border-left:2px solid var(--green)"><div class="lab">按时办结率</div><div class="num" style="color:var(--green)">${sm.on_time_rate}%</div></div>
  </div>`;

  // 处室效率排行
  const effColor = { '高效': 'var(--green)', '正常': 'var(--cyan)', '待改善': 'var(--red)' };
  html += `<div class="panel">
    <div class="panel-head"><div class="t">📊 各处室审批效率排行</div></div>
    <table class="tbl"><thead><tr>
      <th style="width:40px">#</th><th>处室</th>
      <th style="width:70px">总量</th><th style="width:60px">已通过</th><th style="width:60px">已驳回</th>
      <th style="width:60px">待审批</th><th style="width:60px">超时</th>
      <th style="width:90px">平均时长</th><th style="width:80px">按时率</th><th style="width:70px">评级</th>
    </tr></thead><tbody>`;

  if (!d.departments.length) {
    html += '<tr><td colspan="10" style="text-align:center;padding:24px;color:var(--txt-3)">暂无审批数据</td></tr>';
  } else {
    d.departments.forEach((dep, i) => {
      const overdueCls = dep.overdue > 0 ? 'style="color:var(--red);font-weight:600"' : '';
      const pendingCls = dep.pending > 0 ? 'style="color:var(--orange);font-weight:600"' : '';
      html += `<tr class="eff-row-click" onclick="navTo('/project')">
        <td style="color:var(--txt-3)">${i+1}</td>
        <td><span class="dept-chip">${dep.dept}</span></td>
        <td>${dep.total}</td>
        <td style="color:var(--green)">${dep.approved}</td>
        <td style="color:var(--red)">${dep.rejected}</td>
        <td ${pendingCls}>${dep.pending}</td>
        <td ${overdueCls}>${dep.overdue}</td>
        <td>${dep.avg_days > 0 ? dep.avg_days + ' 天' : '—'}</td>
        <td>${dep.on_time_rate}%</td>
        <td><span class="tag ${dep.efficiency_label==='高效'?'tag-green':dep.efficiency_label==='正常'?'tag-blue':'tag-red'}">${dep.efficiency_label}</span></td>
      </tr>`;
    });
  }
  html += `</tbody></table></div>`;

  body.innerHTML = html;
}

async function renderPendingApprovals() {
  const body = document.getElementById('projBody');
  body.innerHTML = '<div class="loading">加载待审批事项...</div>';
  const myDept = _userDeptName();
  const res = await api('/api/projects/pending-approvals');
  if (!res || res.code !== 200) { body.innerHTML = '<div class="empty">加载失败</div>'; return; }
  let list = res.data.list || [];

  // 筛选：admin看全部，其他用户只看本处室
  const isAdmin = currentUser && currentUser.roles && currentUser.roles.some(r => r.code === 'ADMIN');
  const myPending = isAdmin ? list : list.filter(a => myDept && (a.approver || '').includes(myDept));

  let html = '';

  // 统计卡
  html += `<div class="stat-row" style="grid-template-columns:repeat(4,1fr);margin-bottom:16px">
    <div class="stat-box proj-stat-click" onclick="navTo('/project')" style="border-left:2px solid var(--orange)"><div class="lab">待我审批</div><div class="num" style="color:var(--orange)">${myPending.length}</div><div class="sub">${myDept || '全部处室'}</div></div>
    <div class="stat-box proj-stat-click" onclick="navTo('/project')"><div class="lab">超时未处理</div><div class="num" style="color:${myPending.filter(a=>a.is_overdue).length>0?'var(--red)':'var(--green)'}">${myPending.filter(a=>a.is_overdue).length}</div><div class="sub">需立即处理</div></div>
    <div class="stat-box proj-stat-click" onclick="navTo('/project')"><div class="lab">已选中</div><div class="num" id="batchSelectedCount" style="color:var(--cyan)">${selectedApprovals.size}</div><div class="sub">条审批事项</div></div>
    <div class="stat-box proj-stat-click" onclick="navTo('/project')"><div class="lab">全部待审批</div><div class="num">${list.length}</div><div class="sub">全局视角</div></div>
  </div>`;

  if (!myPending.length) {
    html += `<div class="empty" style="padding:48px 0">🎉 暂无待审批事项${!isAdmin && myDept ? `（${myDept}）` : ''}</div>`;
    body.innerHTML = html;
    return;
  }

  // 表格 + checkbox
  html += `<table class="tbl" id="pendingTbl"><thead><tr>
    <th style="width:36px"><input type="checkbox" id="selAllAppr" onchange="toggleAllApprovals(this)" ${selectedApprovals.size === myPending.length && myPending.length > 0 ? 'checked' : ''} style="cursor:pointer"></th>
    <th style="width:40px">#</th>
    <th>项目名称</th>
    <th>审批类型</th>
    <th>申请日期</th>
    <th>审批处室</th>
    <th style="width:70px">状态</th>
    <th style="width:60px">操作</th>
  </tr></thead><tbody>`;

  myPending.forEach((a, i) => {
    const checked = selectedApprovals.has(a.id) ? 'checked' : '';
    const overdueTag = a.is_overdue ? '<span class="tag tag-red" style="font-size:10px;margin-left:4px">超时</span>' : '';
    html += `<tr class="${checked ? 'appr-sel' : ''}" id="appr-row-${a.id}">
      <td><input type="checkbox" ${checked} onchange="toggleApproval(${a.id})" style="cursor:pointer"></td>
      <td style="color:var(--txt-3)">${i + 1}</td>
      <td>${a.project_name || '—'}${overdueTag}</td>
      <td>${a.approval_type}</td>
      <td>${a.apply_date}</td>
      <td><span class="dept-chip">${a.approver || '—'}</span></td>
      <td><span class="tag tag-orange">待审批</span></td>
      <td>
        <button class="btn-sm btn-approve" onclick="doApproval(${a.id},'approve',null)" title="单独通过">✓</button>
        <button class="btn-sm btn-reject" onclick="doApproval(${a.id},'reject',null)" title="单独驳回">✕</button>
      </td>
    </tr>`;
  });

  html += `</tbody></table>`;

  // 浮动批量操作栏
  html += `<div class="batch-bar" id="batchBar" style="display:${selectedApprovals.size > 0 ? 'flex' : 'none'}">
    <span class="batch-info">已选 <strong id="batchCount">${selectedApprovals.size}</strong> 项</span>
    <button class="btn-sm btn-approve" onclick="doBatchApproval('approve')">✓ 批量通过</button>
    <button class="btn-sm btn-reject" onclick="doBatchApproval('reject')">✕ 批量驳回</button>
    <button class="btn-ghost" onclick="selectedApprovals.clear();renderPendingApprovals()" style="font-size:12px;padding:5px 12px">取消选择</button>
  </div>`;

  body.innerHTML = html;
}

function toggleApproval(aid) {
  if (selectedApprovals.has(aid)) {
    selectedApprovals.delete(aid);
  } else {
    selectedApprovals.add(aid);
  }
  updateBatchBar();
}

function toggleAllApprovals(checkbox) {
  const rows = document.querySelectorAll('#pendingTbl tbody tr');
  if (checkbox.checked) {
    rows.forEach(row => {
      const id = parseInt(row.id.replace('appr-row-', ''));
      if (id) {
        selectedApprovals.add(id);
        row.classList.add('appr-sel');
        const cb = row.querySelector('input[type=checkbox]');
        if (cb) cb.checked = true;
      }
    });
  } else {
    rows.forEach(row => {
      const id = parseInt(row.id.replace('appr-row-', ''));
      if (id) {
        selectedApprovals.delete(id);
        row.classList.remove('appr-sel');
        const cb = row.querySelector('input[type=checkbox]');
        if (cb) cb.checked = false;
      }
    });
  }
  updateBatchBar();
}

function updateBatchBar() {
  const bar = document.getElementById('batchBar');
  const count = document.getElementById('batchCount');
  const countStat = document.getElementById('batchSelectedCount');
  if (bar) bar.style.display = selectedApprovals.size > 0 ? 'flex' : 'none';
  if (count) count.textContent = selectedApprovals.size;
  if (countStat) countStat.textContent = selectedApprovals.size;
}

async function doBatchApproval(action) {
  const labels = { approve: '通过', reject: '驳回' };
  if (selectedApprovals.size === 0) { showToast('请先勾选审批事项', 'warn'); return; }
  if (!confirm(`确定批量${labels[action]} ${selectedApprovals.size} 项审批？`)) return;

  const ids = [...selectedApprovals];
  showToast(`正在批量${labels[action]} ${ids.length} 项...`, 'info');
  const res = await api('/api/approvals/batch-action', {
    method: 'POST',
    body: JSON.stringify({ ids: ids, action: action, comment: '' }),
  });

  if (res && res.code === 200) {
    const msg = res.data.message || `批量${labels[action]}完成`;
    showToast(`✅ ${msg}`, 'success');
    selectedApprovals.clear();
    await renderPendingApprovals();
  } else {
    showToast((res && res.message) || '批量操作失败', 'warn');
  }
}

async function renderProjectList() {
  const body = document.getElementById('projBody');
  // 统计
  const stats = await api('/api/projects/stats');
  const s = (stats && stats.code === 200) ? stats.data : null;
  
  // 本处室审批数据（实操入口）
  const pendingData = await api('/api/projects/pending-approvals');
  const pendingItems = (pendingData && pendingData.code === 200) ? (pendingData.data.list || []) : [];
  const myDept = _userDeptName();
  const myPending = pendingItems.filter(a => myDept && (a.approver || '').includes(myDept));

  const types = ['', '房建', '市政', '交通', '水利', '园林'];
  const areas = ['', '启动区', '起步区', '容东片区', '昝岗片区', '白洋淀', '容城县城'];
  const stages = ['', '立项', '规划', '审批', '建设', '验收', '运维'];
  const alerts = [['', '全部'], ['overdue', '逾期'], ['near_due', '临近']];

  let html = `<div class="toolbar" style="flex-wrap:wrap;gap:6px;margin-bottom:14px">
    <button class="btn-ghost ${projFilter.my_dept ? 'active' : ''}" onclick="projFilter.my_dept = projFilter.my_dept ? 0 : 1; renderProjectList()" title="仅看本处室相关">🏢 ${projFilter.my_dept ? '本处室视图 ✓' : '全部项目'}</button>
    <button class="btn-ghost ${projViewMode==='card'?'active':''}" onclick="projViewMode='card';renderProjectList()">📋 卡片</button>
    <button class="btn-ghost ${projViewMode==='list'?'active':''}" onclick="projViewMode='list';renderProjectList()">📊 列表</button>
  </div>`;

  // 待我处理条（最高优先）
  if (myPending.length > 0) {
    html += `<div class="tp-action-row" style="margin-bottom:14px">
      <div class="tp-action-card has-items" style="border-left:3px solid var(--orange)">
        <div class="tp-action-num">${myPending.length}</div>
        <div class="tp-action-label">📝 ${myDept || '本处室'} · 待审批</div>
        <div class="tp-action-hint">${myPending.map(a => a.approval_type).slice(0, 3).join('、')}</div>
      </div>
      <div class="tp-action-card ${s && s.risk_summary.overdue > 0 ? 'alerts' : ''}" onclick="projFilter.alert='overdue';renderProjectList()">
        <div class="tp-action-num" style="color:${s && s.risk_summary.overdue > 0 ? 'var(--red)' : 'var(--green)'}">${s ? s.risk_summary.overdue : 0}</div>
        <div class="tp-action-label">🚨 逾期项目</div>
        <div class="tp-action-hint">${s && s.risk_summary.overdue > 0 ? '需立即处置' : '无逾期 ✓'}</div>
      </div>
      <div class="tp-action-card" onclick="projFilter.alert='near_due';renderProjectList()">
        <div class="tp-action-num" style="color:${s && s.risk_summary.near_due > 0 ? 'var(--orange)' : 'var(--green)'}">${s ? s.risk_summary.near_due : 0}</div>
        <div class="tp-action-label">⏰ 临近到期</div>
        <div class="tp-action-hint">${s && s.risk_summary.near_due > 0 ? '9月1日前到期' : '无临近 ✓'}</div>
      </div>
    </div>`;
  }

  // 统计条
  if (s) {
    html += `<div class="stat-row" style="grid-template-columns:repeat(5,1fr);margin-bottom:16px">
      <div class="stat-box proj-stat-click" onclick="navTo('/project')"><div class="lab">项目总数</div><div class="num">${s.total}</div></div>
      <div class="stat-box proj-stat-click" onclick="openCoreDetail('cj14')"><div class="lab">总投资</div><div class="num" style="font-size:24px">${(s.total_invest/10000).toFixed(0)}<span class="unit">亿元</span></div></div>
      <div class="stat-box proj-stat-click" onclick="projFilter.alert='overdue';renderProjectList()"><div class="lab">逾期</div><div class="num" style="color:var(--red)">${s.risk_summary.overdue}</div></div>
      <div class="stat-box proj-stat-click" onclick="projFilter.alert='near_due';renderProjectList()"><div class="lab">临近</div><div class="num" style="color:var(--orange)">${s.risk_summary.near_due}</div></div>
      <div class="stat-box proj-stat-click" onclick="projFilter.alert='';renderProjectList()"><div class="lab">正常</div><div class="num" style="color:var(--green)">${s.risk_summary.normal}</div></div>
    </div>`;
  }

  // 筛选工具栏
  html += `<div class="toolbar" style="flex-wrap:wrap;gap:6px">
    <input class="proj-search" placeholder="🔍 搜索项目名称..." value="${projFilter.keyword}" onkeyup="projFilter.keyword=this.value;renderProjectDebounced()">
    ${[['类型', types, 'ptype'], ['片区', areas, 'area'], ['阶段', stages, 'stage'], ['风险', alerts, 'alert']].map(([label, opts, key]) =>
      `<select onchange="projFilter.${key}=this.value;renderProjectList()" style="background:rgba(10,14,39,.6);border:1px solid var(--line);color:var(--txt);padding:6px 10px;border-radius:7px;font-size:13px">
        <option value="">${label}</option>${opts.slice(1).map(o => Array.isArray(o)
          ? `<option value="${o[0]}" ${projFilter[key]===o[0]?'selected':''}>${o[1]}</option>`
          : `<option value="${o}" ${projFilter[key]===o?'selected':''}>${o}</option>`).join('')}
      </select>`).join('')}
    <button class="btn-ghost" onclick="Object.keys(projFilter).forEach(k=>projFilter[k]='');renderProjectList()">↻ 清除</button>
  </div>`;

  // 加载项目数据
  let params = [];
  Object.entries(projFilter).forEach(([k, v]) => { if (v) params.push(k + '=' + encodeURIComponent(v)); });
  const data = await api('/api/projects?' + params.join('&'));
  let list = (data && data.code === 200) ? (data.data.list || []) : [];
  
  // 本处室视图：过滤项目（需加载阶段数据判断处室归属）
  if (projFilter.my_dept && myDept) {
    const filtered = [];
    for (const p of list) {
      const detail = await api('/api/projects/' + p.id);
      if (detail && detail.code === 200) {
        const stages = detail.data.stages || [];
        const matched = stages.some(s => (s.resp_dept || '').includes(myDept));
        if (matched) filtered.push(p);
      }
    }
    list = filtered;
  }

  if (!list.length) { html += '<div class="empty">' + (projFilter.my_dept ? '本处室暂无关联项目' : '暂无匹配项目') + '</div>'; }
  else if (projViewMode === 'card') {
    html += `<div class="proj-grid">${list.map(p => renderProjectCard(p)).join('')}</div>`;
  } else {
    html += `<table class="tbl"><thead><tr><th>项目名称</th><th>类型</th><th>片区</th><th>投资(亿)</th><th>阶段</th><th>进度</th><th>风险</th></tr></thead><tbody>
      ${list.map(p => `
        <tr style="cursor:pointer" onclick="toggleProjectDetail(${p.id})">
          <td>${p.name}</td><td>${p.ptype}</td><td>${p.area}</td>
          <td>${(p.invest/10000).toFixed(1)}</td><td>${p.stage}</td>
          <td><div class="proj-mini-bar"><div class="proj-mini-fill" style="width:${p.progress}%;background:${p.risk==='overdue'?'var(--red)':p.risk==='near'?'var(--orange)':'var(--cyan)'}"></div></div><small>${p.progress}%</small></td>
          <td><span class="tag ${p.risk==='overdue'?'tag-red':p.risk==='near'?'tag-orange':p.risk==='none'?'tag-green':'tag-blue'}">${p.risk==='overdue'?'逾期':p.risk==='near'?'临近':p.risk==='none'?'已完成':'正常'}</span></td>
        </tr>`).join('')}
    </tbody></table>`;

    // 展开详情
    if (expandedProject) {
      html += `<div id="projDetail" style="margin-top:16px"></div>`;
    }
  }

  if (body) body.innerHTML = html;
  else document.getElementById('content').innerHTML = html;
  if (expandedProject && projViewMode === 'list') {
    await loadProjectDetail(expandedProject);
  }
}

let renderDebounce = null;
function renderProjectDebounced() {
  if (renderDebounce) clearTimeout(renderDebounce);
  renderDebounce = setTimeout(() => renderProjectList(), 400);
}

function renderProjectCard(p) {
  const riskColor = { overdue: 'var(--red)', near: 'var(--orange)', normal: 'var(--cyan)', none: 'var(--green)' };
  const riskLabel = { overdue: '逾期', near: '临近', normal: '正常', none: '已完成' };
  return `<div class="proj-card" onclick="openProjectDetail(${p.id})">
    <div class="proj-card-head">
      <span class="proj-card-type">${p.ptype}</span>
      <span class="tag ${p.risk==='overdue'?'tag-red':p.risk==='near'?'tag-orange':p.risk==='none'?'tag-green':'tag-blue'}">${riskLabel[p.risk]}</span>
    </div>
    <div class="proj-card-name">${p.name}</div>
    <div class="proj-card-meta">
      <span>${p.area}</span><span>${p.build_unit}</span>
    </div>
    <div class="proj-card-progress">
      <div class="proj-progress-bar"><div class="proj-progress-fill" style="width:${p.progress}%;background:${riskColor[p.risk]}"></div></div>
      <span class="proj-progress-val">${p.progress}%</span>
    </div>
    <div class="proj-card-foot">
      <span>投资 ${(p.invest/10000).toFixed(1)}亿</span><span>阶段：${p.stage}</span>
    </div>
  </div>`;
}

async function openProjectDetail(pid) {
  projViewMode = 'list';
  expandedProject = pid;
  await renderProjectList();
}

async function toggleProjectDetail(pid) {
  expandedProject = expandedProject === pid ? null : pid;
  await renderProjectList();
}

async function loadProjectDetail(pid) {
  const detail = document.getElementById('projDetail');
  if (!detail) return;
  const data = await api('/api/projects/' + pid);
  if (!data || data.code !== 200) { detail.innerHTML = '<div class="empty">加载失败</div>'; return; }
  const dd = data.data;
  const p = dd.project;

  // 阶段时间轴（含处室标签）
  const stageHTML = dd.stages.map((s, i) => {
    const done = s.status === '已完成';
    const active = s.status === '进行中';
    const delay = s.status === '超期';
    const cls = done ? 'done' : active ? 'active' : delay ? 'delay' : '';
    const deptChips = s.resp_dept ? s.resp_dept.split(',').map(d => `<span class="dept-chip">${d.trim()}</span>`).join('') : '';
    return `<div class="ps-node ${cls}">
      <div class="ps-dot"></div>
      <div class="ps-info"><div class="ps-name">${s.stage_name} ${deptChips}</div>
        <div class="ps-date">${s.start_date} ~ ${s.plan_end_date || '—'}</div>
        ${s.actual_end_date ? `<div class="ps-actual">实际：${s.actual_end_date}</div>` : ''}
        ${s.remark ? `<div class="ps-remark">📌 ${s.remark}</div>` : ''}
      </div>
    </div>`;
  }).join('');

  // 审批记录（含操作按钮）
  const myDeptName = _userDeptName();
  const apprHTML = dd.approvals.length ? dd.approvals.map(a => {
    const canAct = a.status === '待审批';
    const myDeptMatch = myDeptName && (a.approver || '').includes(myDeptName);
    const actionBtns = (canAct && myDeptMatch)
      ? `<div class="appr-actions" style="margin-top:6px">
          <button class="btn-sm btn-approve" onclick="event.stopPropagation();doApproval(${a.id},'approve',${pid})">✓ 通过</button>
          <button class="btn-sm btn-reject" onclick="event.stopPropagation();doApproval(${a.id},'reject',${pid})">✕ 驳回</button>
        </div>`
      : (canAct ? `<span class="tag tag-gray" style="font-size:10px;margin-left:8px">${(a.approver || '')}办理中</span>` : '');
    const remarkHTML = a.remark ? `<div style="font-size:11px;color:var(--txt-3);margin-top:4px">📌 ${a.remark}</div>` : '';
    return `<div class="appr-row ${canAct && myDeptMatch ? 'appr-actionable' : ''}">
      <span class="tag ${a.status==='已通过'?'tag-green':a.status==='待审批'?'tag-orange':'tag-red'}">${a.status}</span>
      <span>${a.approval_type}</span>
      <span class="appr-date">${a.apply_date}${a.approve_date ? ' → ' + a.approve_date : ''}</span>
      <span class="appr-by">${a.approver}</span>
      ${actionBtns}
      ${remarkHTML}
    </div>`;
  }).join('') : '<div class="empty">暂无审批记录</div>';

  detail.innerHTML = `
    <div class="panel">
      <div class="panel-head"><div class="t">📋 ${p.name} · 详情</div>
        <span class="more" onclick="expandedProject=null;renderProjectList()">✕ 收起</span></div>

      <div class="proj-detail-grid">
        <div><span class="proj-dl">类型</span> ${p.ptype}</div>
        <div><span class="proj-dl">片区</span> ${p.area}</div>
        <div><span class="proj-dl">建设单位</span> ${p.build_unit}</div>
        <div><span class="proj-dl">施工单位</span> ${p.contractor || '-'}</div>
        <div><span class="proj-dl">监理单位</span> ${p.supervisor || '-'}</div>
        <div><span class="proj-dl">投资额</span> ${(p.invest/10000).toFixed(1)}亿元</div>
        <div><span class="proj-dl">建设规模</span> ${p.scale || '-'} ${p.scale_unit || ''}</div>
        <div><span class="proj-dl">当前阶段</span> ${p.stage}</div>
        <div><span class="proj-dl">开工日期</span> ${p.start_date || '-'}</div>
        <div><span class="proj-dl">计划竣工</span> ${p.plan_end_date || '-'}</div>
      </div>

      <div style="margin-top:18px"><div class="panel-head"><div class="t">⏱ 阶段时间轴</div></div>
        <div class="ps-timeline">${stageHTML}</div></div>

      <div style="margin-top:18px"><div class="panel-head"><div class="t">📝 审批记录</div></div>
        <div class="appr-list">${apprHTML}</div></div>
    </div>`;
}

async function doApproval(aid, action, pid) {
  const labels = { approve: '通过', reject: '驳回' };
  if (!confirm(`确定${labels[action]}此项审批？${action === 'reject' ? '\n驳回后可重新提交。' : ''}`)) return;
  
  const res = await api('/api/projects/approvals/' + aid + '/action', {
    method: 'POST',
    body: JSON.stringify({ action: action, comment: '' }),
  });
  
  if (res && res.code === 200) {
    showToast(`审批已${labels[action]}`, 'success');
    if (pid) {
      // 从项目详情页操作，重新加载
      expandedProject = pid;
      projViewMode = 'list';
      await renderProjectList();
    } else {
      // 从待审批页操作，重新加载待审批列表
      await renderPendingApprovals();
    }
  } else {
    showToast((res && res.message) || '操作失败', 'warn');
  }
}

async function exportProjectsExcel() {
  showToast('正在生成台账...', 'info');
  try {
    const res = await fetch('/api/projects/export', {
      headers: { 'Authorization': 'Bearer ' + token },
    });
    if (!res.ok) throw new Error('导出失败');
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `建交局项目台账_${new Date().toISOString().slice(0,10)}.xlsx`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast('台账导出成功 ✓', 'success');
  } catch (e) {
    showToast('导出失败：' + e.message, 'warn');
  }
}

/* ---------- 态势大屏 ---------- */
let overviewRefreshTimer = null;

// HTML 转义（安全渲染用户内容）
function esc(s) {
  if (s == null) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

async function renderOverview() {
  const data = await api('/api/overview/dashboard');
  if (!data || data.code !== 200) {
    document.getElementById('content').innerHTML = '<div class="empty">数据加载失败</div>';
    return;
  }
  const d = data.data;

  // 核心指标项（带 code 和点击）
  const coreItems = [
    { code:'cj01', label:'在建项目', value:d.core.in_progress_projects, unit:'个', color:'var(--cyan)' },
    { code:'cj02', label:'本月审批', value:d.core.month_permits, unit:'件', color:'var(--blue)' },
    { code:'cj03', label:'审批通过率', value:d.core.fire_pass_rate, unit:'%', color:'var(--green)' },
    { code:'cj04', label:'隐患数', value:d.core.hazards, unit:'项', color:'var(--orange)' },
    { code:'cj05', label:'整改闭环率', value:d.core.closure_rate, unit:'%', color:'var(--green)' },
    { code:'cj14', label:'总投资', value:d.core.total_invest, unit:'亿元', color:'var(--cyan)' },
    { code:'jt05', label:'公交日均客流', value:d.core.bus_daily_flow, unit:'万人次', color:'var(--orange)' },
  ];

  // 领域指标面板 HTML（可点击）
  function domainPanel(dp, side) {
    const rows = dp.indicators.map(ind => `
      <div class="ov-ind-row">
        <span class="ov-ind-name">${ind.name}</span>
        <span class="ov-ind-val">${ind.value ?? '-'}<small>${ind.unit}</small></span>
      </div>`).join('');
    return `<div class="ov-domain-panel ov-domain-clickable" onclick="openDomainDetail(${dp.domain})" title="点击查看${dp.name}详细数据">
      <div class="ov-dom-head"><span>${dp.icon}</span> ${dp.name}</div>
      <div class="ov-ind-list">${rows}</div>
    </div>`;
  }

  // 构建完整 HTML
  const leftPanels = d.domain_panels.slice(0, 2).map(p => domainPanel(p, 'left')).join('');
  const rightPanels = d.domain_panels.slice(2, 4).map(p => domainPanel(p, 'right')).join('');

  let html = `
  <div class="overview-wrap">
    <!-- 顶栏 -->
    <div class="ov-topbar">
      <div class="ov-title-row">
        <span class="ov-logo"><svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg></span>
        <span class="ov-sys-name">雄安新区建设和交通管理局 · 协同调度中心</span>
        <span class="ov-xa-tag">千年大计 · 国家大事</span>
        <span class="ov-label">态势大屏</span>
        <span class="ov-clock" id="ovClock">--</span>
        <span class="ov-live"><span class="ov-live-dot"></span>实时</span>
      </div>
      <div class="ov-core-strip">
        ${coreItems.map(c => `<div class="ov-core-item" onclick="openCoreDetail('${c.code}')" title="点击查看${c.label}详情"><span class="ov-core-label">${c.label}</span><span class="ov-core-val" style="color:${c.color}">${c.value}<small>${c.unit}</small></span></div>`).join('')}
      </div>
    </div>

    <!-- 主体三栏 -->
    <div class="ov-main">
      <div class="ov-left">${leftPanels}</div>
      <div class="ov-center">
        <!-- 二维/三维视图切换 -->
        <div class="ov-map-switch" id="ovMapSwitch">
          <span class="ov-map-btn active" data-mode="2d" onclick="switchMapView('2d')">二维地图</span>
          <span class="ov-map-btn" data-mode="3d" onclick="switchMapView('3d')">三维CIM</span>
        </div>
        <!-- 二维地图容器 -->
        <div class="ov-map-container" id="ovMapContainer2d">
          <div id="ovMapCanvas"></div>
          <div class="ov-map-overlay">
            <span class="ov-map-title">雄安新区 · 天地图</span>
          </div>
          <div class="ov-map-legend">
            <span><i style="background:#00d4ff"></i>项目</span>
            <span><i style="background:#ffb300"></i>公交站</span>
            <span><i style="background:#69f0ae"></i>市政设施</span>
          </div>
        </div>
        <!-- 三维引擎容器（默认隐藏） -->
        <div class="ov-map-container ov-dts-container" id="ovMapContainer3d" style="display:none">
          <div id="ovDtsPlayer"></div>
          <div class="ov-dts-overlay">
            <span class="ov-map-title">雄安新区 · 三维CIM</span>
          </div>
          <div class="ov-dts-status ov-dts-unavailable" id="ovDtsStatus">
            ⚠️ 三维引擎未接入<br><small>请联系管理员配置DTS云渲染服务器地址</small>
          </div>
        </div>
        <!-- 事件时间线 -->
        <div class="ov-timeline">
          <div class="ov-tl-head"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:4px"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>实时事件</div>
          <div class="ov-tl-list" id="ovTimeline">
            ${d.timeline.map(t => `
              <div class="ov-tl-item ${t.tag ? 'urgent' : ''}">
                <span class="ov-tl-ico">${t.icon}</span>
                <span class="ov-tl-title">${t.title}</span>
                <span class="ov-tl-time">${t.time}</span>
                ${t.tag ? `<span class="tag tag-red">${t.tag}</span>` : ''}
              </div>`).join('')}
          </div>
        </div>
      </div>
      <div class="ov-right">${rightPanels}</div>
    </div>

    <!-- 底部预警滚动条 -->
    <div class="ov-warn-bar">
      <span class="ov-warn-label"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:4px"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>实时预警</span>
      <div class="ov-warn-scroll" id="ovWarnScroll">
        <div class="ov-warn-track">
          ${d.warnings.length ? d.warnings.map(w => `
            <span class="ov-warn-item lvl-${w.level}" onclick="showWarnDetail(${w.id},'${esc(w.title)}','${esc(w.content)}','${esc(w.sender)}','${w.created_at}',${w.level})">${esc(w.title)}<small>${esc(w.sender)} · ${w.created_at}</small></span>
          `).join('') : '<span class="ov-warn-item">当前无预警</span>'}
        </div>
      </div>
    </div>
  </div>`;

  document.getElementById('content').innerHTML = html;

  // 时钟
  function tick() { const el = document.getElementById('ovClock'); if (el) el.textContent = new Date().toLocaleString('zh-CN', { hour12: false }); }
  tick();
  if (overviewRefreshTimer) clearInterval(overviewRefreshTimer);
  overviewRefreshTimer = setInterval(tick, 1000);

  // 重置地图过滤 + 画地图
  window._ovMarkerFilter = null;
  setTimeout(() => drawOverviewMap(d.map_markers), 100);

  // 加载DTS配置（静默，不阻塞渲染）
  loadDtsConfig().catch(() => {});

  // 预警滚动动画
  initWarnScroll();
}

/* ---------- 二维/三维视图切换 ---------- */
let currentMapView = '2d';

function switchMapView(mode) {
  if (mode === currentMapView) return;
  currentMapView = mode;

  // 更新按钮状态
  document.querySelectorAll('.ov-map-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.mode === mode);
  });

  const c2d = document.getElementById('ovMapContainer2d');
  const c3d = document.getElementById('ovMapContainer3d');

  if (mode === '3d') {
    c2d.style.display = 'none';
    c3d.style.display = '';
    // 初始化DTS引擎（仅在首次切换到3d时）
    if (!DTS_ENGINE.isAvailable && !DTS_ENGINE.isConnecting) {
      DTS_ENGINE.init();
    }
  } else {
    c3d.style.display = 'none';
    c2d.style.display = '';
    // Leaflet 地图 invalidateSize（从隐藏→显示需要重算尺寸）
    if (window._ovMap) {
      setTimeout(() => window._ovMap.invalidateSize(), 50);
    }
  }
}

function drawOverviewMap(markers) {
  const container = document.getElementById('ovMapCanvas');
  if (!container || typeof L === 'undefined') return;

  // 天地图 key（天地图官方公共 key，浏览器端免注册使用）
  const TD_KEY = '0b018552994f71a9467d24461a8f8238';

  // 初始化地图，定位雄安新区
  const map = L.map(container, {
    center: [39.04, 116.08],
    zoom: 12,
    zoomControl: false,
    attributionControl: false,
    preferCanvas: true,
  });

  // —— 自绘暗色底图（政务大屏风格，无需网络瓦片） ——
  const DarkGridLayer = L.GridLayer.extend({
    createTile: function(coords) {
      const tile = document.createElement('canvas');
      const sz = 256;
      tile.width = sz; tile.height = sz;
      const ctx = tile.getContext('2d');
      // 深色渐变背景
      const grad = ctx.createLinearGradient(0, 0, sz, sz);
      grad.addColorStop(0, '#080d1f');
      grad.addColorStop(1, '#0a1530');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, sz, sz);
      // 细网格
      ctx.strokeStyle = 'rgba(6,182,212,.06)';
      ctx.lineWidth = 0.5;
      for (let i = 0; i <= sz; i += 32) {
        ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, sz); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(sz, i); ctx.stroke();
      }
      // 粗网格
      ctx.strokeStyle = 'rgba(6,182,212,.12)';
      ctx.lineWidth = 0.5;
      for (let i = 0; i <= sz; i += 128) {
        ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, sz); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(sz, i); ctx.stroke();
      }
      return tile;
    }
  });
  const darkLayer = new DarkGridLayer();

  // —— 天地图图层（有 key 时使用） ——
  let useTd = !!TD_KEY;
  if (useTd) {
    const vecLayer = L.tileLayer(
      'https://t{s}.tianditu.gov.cn/DataServer?T=vec_w&x={x}&y={y}&l={z}&tk=' + TD_KEY,
      { subdomains: ['0','1','2','3','4','5','6','7'], maxZoom: 18 }
    );
    const cvaLayer = L.tileLayer(
      'https://t{s}.tianditu.gov.cn/DataServer?T=cva_w&x={x}&y={y}&l={z}&tk=' + TD_KEY,
      { subdomains: ['0','1','2','3','4','5','6','7'], maxZoom: 18 }
    );
    vecLayer.on('tileerror', () => {
      map.removeLayer(vecLayer); map.removeLayer(cvaLayer);
      darkLayer.addTo(map);
      const ov = document.querySelector('.ov-map-overlay');
      if (ov) ov.textContent = '雄安新区 · 态势底图';
    });
    vecLayer.addTo(map);
    cvaLayer.addTo(map);
  } else {
    darkLayer.addTo(map);
    const ov = document.querySelector('.ov-map-overlay');
    if (ov) ov.textContent = '雄安新区 · 态势底图（填入天地图 key 后显示真实地图）';
  }

  // 缩放控件
  L.control.zoom({ position: 'bottomright' }).addTo(map);

  // 片区标注
  const areas = [
    { name: '容东片区', lng: 116.098, lat: 39.050 },
    { name: '容西片区', lng: 116.078, lat: 39.058 },
    { name: '启动区', lng: 116.108, lat: 39.043 },
    { name: '起步区', lng: 116.115, lat: 39.040 },
    { name: '昝岗片区', lng: 116.160, lat: 39.054 },
    { name: '雄县', lng: 116.120, lat: 39.020 },
    { name: '容城', lng: 116.070, lat: 39.066 },
    { name: '安新', lng: 116.032, lat: 38.998 },
    { name: '白洋淀', lng: 116.060, lat: 38.935 },
  ];
  for (const a of areas) {
    L.marker([a.lat, a.lng], {
      icon: L.divIcon({ className: 'ov-area-label', html: `<span>${a.name}</span>`, iconSize: [60, 20], iconAnchor: [30, 10] })
    }).addTo(map);
  }

  // 白洋淀水域
  L.circle([38.935, 116.060], {
    radius: 5000, color: '#06b6d4', weight: 1, opacity: 0.5,
    fillColor: '#06b6d4', fillOpacity: 0.1,
  }).addTo(map);

  // 存储标记数据，但不绘制（由 refreshOvMapMarkers 按需绘制）
  window._ovAllMarkers = markers || [];
  window._ovMarkerLayer = null;
  window._ovMap = map;

  // 如果已有过滤条件则立即按需绘制
  if (window._ovMarkerFilter) {
    setTimeout(refreshOvMapMarkers, 50);
  }
}

/**
 * 按当前 _ovMarkerFilter 刷新地图标记
 * 过滤规则：
 *   { type:'core', code:'cj01' } → project 类型标记
 *   { type:'core', code:'jt05' } → station 类型标记
 *   { type:'core', code:'cj14' } → project 类型标记
 *   { type:'domain', domain:1 }  → 按领域筛选项目ptype
 *   null                         → 不显示标记
 */
function refreshOvMapMarkers() {
  if (!window._ovMap || !window._ovAllMarkers) return;
  if (window._ovMarkerLayer) {
    window._ovMap.removeLayer(window._ovMarkerLayer);
    window._ovMarkerLayer = null;
  }
  const filter = window._ovMarkerFilter;
  if (!filter) return;

  let targetTypes = [];
  if (filter.type === 'core') {
    if (filter.code === 'jt05') targetTypes = ['station'];
    else targetTypes = ['project'];
  } else if (filter.type === 'domain') {
    if (filter.domain === 1) targetTypes = ['project'];
    else if (filter.domain === 2) targetTypes = ['station'];
    else if (filter.domain === 3) targetTypes = [];
    else if (filter.domain === 4) targetTypes = ['municipal'];
  }

  const filtered = window._ovAllMarkers.filter(m => targetTypes.includes(m.type));
  if (!filtered.length) return;

  const typeIcon = {
    project: { color: '#00d4ff', r: 8 },
    station: { color: '#ffb300', r: 6 },
    municipal: { color: '#69f0ae', r: 5 },
  };
  window._ovMarkerLayer = L.layerGroup().addTo(window._ovMap);
  for (const m of filtered) {
    const cfg = typeIcon[m.type] || typeIcon.project;
    const icon = L.divIcon({
      className: 'ov-marker',
      html: `<div class="ov-marker-pulse" style="--mc:${cfg.color}"></div>
             <div class="ov-marker-dot" style="background:${cfg.color};box-shadow:0 0 10px ${cfg.color}"></div>`,
      iconSize: [cfg.r * 2, cfg.r * 2],
      iconAnchor: [cfg.r, cfg.r],
    });
    L.marker([m.lat, m.lng], { icon }).addTo(window._ovMarkerLayer);
  }
}

/* ---------- 态势大屏：通用模态框 ---------- */
function showOvModal(title, contentHTML, opts) {
  opts = opts || {};
  const overlay = document.createElement('div');
  overlay.className = 'ov-modal-overlay';
  overlay.innerHTML = `
    <div class="ov-modal-box" style="${opts.width ? 'width:'+opts.width : ''}">
      <div class="ov-modal-head">
        <span class="ov-modal-title">${title}</span>
        <button class="ov-modal-close" id="ovModalClose">✕</button>
      </div>
      <div class="ov-modal-body">${contentHTML}</div>
    </div>`;
  overlay.addEventListener('click', e => {
    if (e.target === overlay) closeOvModal();
  });
  document.body.appendChild(overlay);
  const closeBtn = document.getElementById('ovModalClose');
  if (closeBtn) closeBtn.addEventListener('click', closeOvModal);
  // 动画
  requestAnimationFrame(() => overlay.style.opacity = '1');

  function closeOvModal() {
    if (overlay.parentElement) overlay.parentElement.removeChild(overlay);
    if (opts.onClose) opts.onClose();
  }
}

/* ---------- 态势大屏：核心指标详情 ---------- */
async function openCoreDetail(code) {
  const data = await api('/api/overview/core-detail', { method: 'POST', body: JSON.stringify({ code }) });
  if (!data || data.code !== 200) { showToast('数据加载失败', 'warn'); return; }
  const dd = data.data;

  // 标题映射
  const labelMap = {
    cj01:'在建项目', cj02:'本月办件', cj03:'消防验收通过率',
    cj04:'隐患数', cj05:'整改闭环率',
    cj14:'总投资', jt05:'公交日客流',
  };

  // 设置地图过滤
  window._ovMarkerFilter = { type: 'core', code };
  refreshOvMapMarkers();

  // 构建表格
  let html = '';
  if (dd.summary) {
    html += `<div class="ov-summary-card"><strong>${esc(dd.summary)}</strong></div>`;
  }
  if (dd.rows && dd.rows.length) {
    html += `<table class="ov-detail-table"><thead><tr>${dd.columns.map(c => `<th>${c}</th>`).join('')}</tr></thead><tbody>`;
    html += dd.rows.map(row => `<tr>${row.map(cell => `<td>${esc(cell)}</td>`).join('')}</tr>`).join('');
    html += `</tbody></table>`;
  } else {
    html += `<div class="empty">暂无详细数据</div>`;
  }

  showOvModal(`${labelMap[code] || '详情'} · 明细数据`, html, {
    onClose: () => { window._ovMarkerFilter = null; refreshOvMapMarkers(); }
  });
}

/* ---------- 态势大屏：预警详情 ---------- */
function showWarnDetail(id, title, content, sender, createdAt, level) {
  const levelLabels = {1:'一般', 2:'较重', 3:'严重'};
  const lvlColor = {1:'var(--warning)', 2:'var(--orange)', 3:'var(--danger)'};
  const html = `
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:16px">
      <div><div style="color:var(--text-3);font-size:12px;margin-bottom:4px">标题</div><div style="font-size:15px;font-weight:600;color:var(--text)">${esc(title)}</div></div>
      <div><div style="color:var(--text-3);font-size:12px;margin-bottom:4px">级别</div><span class="tag" style="background:${lvlColor[level]};color:#fff;border:none">${levelLabels[level] || level}</span></div>
      <div><div style="color:var(--text-3);font-size:12px;margin-bottom:4px">发送方</div><div style="color:var(--text-2)">${esc(sender)}</div></div>
      <div><div style="color:var(--text-3);font-size:12px;margin-bottom:4px">时间</div><div style="color:var(--text-2)">${createdAt}</div></div>
    </div>
    <div style="padding-top:14px;border-top:1px solid var(--border-light)">
      <div style="color:var(--text-3);font-size:12px;margin-bottom:8px">详细内容</div>
      <div style="color:var(--text-2);line-height:1.8;font-size:14px;white-space:pre-wrap">${esc(content || '暂无详细内容')}</div>
    </div>`;
  showOvModal('⚠️ 预警详情', html);
}

/* ---------- 态势大屏：领域详情 ---------- */
async function openDomainDetail(domain) {
  const data = await api('/api/overview/domain-detail/' + domain);
  if (!data || data.code !== 200) { showToast('数据加载失败', 'warn'); return; }
  const dd = data.data;

  // 设置地图过滤
  window._ovMarkerFilter = { type: 'domain', domain };
  refreshOvMapMarkers();

  let html = '';

  // 基础统计
  html += `<div class="ov-summary-card">共 <strong>${dd.stats.total_indicators}</strong> 项指标 · <strong>${dd.stats.total_projects}</strong> 个项目 · <strong>${dd.stats.total_extra}</strong> 条专项记录</div>`;

  // 指标列表
  if (dd.indicators && dd.indicators.length) {
    html += `<div class="ov-section-title">📊 全部指标</div>`;
    html += `<table class="ov-detail-table"><thead><tr><th>指标名称</th><th>最新值</th><th>单位</th><th>说明</th></tr></thead><tbody>`;
    for (const ind of dd.indicators) {
      html += `<tr><td>${esc(ind.name)}</td><td class="num">${ind.value ?? '-'}</td><td>${esc(ind.unit)}</td><td style="font-size:12px;color:var(--text-3)">${esc(ind.definition)}</td></tr>`;
    }
    html += `</tbody></table>`;
  }

  // 项目列表
  if (dd.entities && dd.entities.length) {
    html += `<div class="ov-section-title">🏗️ 项目列表（${dd.entities.length} 个）</div>`;
    html += `<div class="ov-entity-grid">`;
    for (const p of dd.entities) {
      html += `<div class="ov-entity-card">
        <div class="ov-entity-name">${esc(p.name)}</div>
        <div class="ov-entity-meta">
          <span class="ov-entity-tag">${esc(p.ptype)}</span>
          <span>${esc(p.area)}</span>
          <span>${(p.invest/10000).toFixed(1)}亿</span>
          <span>${p.progress}%</span>
          <span>${esc(p.stage)}</span>
        </div>
      </div>`;
    }
    html += `</div>`;
  }

  // 专项实体
  if (dd.extra_entities && dd.extra_entities.length) {
    html += `<div class="ov-section-title">📋 专项数据（${dd.extra_entities.length} 条）</div>`;
    html += `<div class="ov-entity-grid">`;
    for (const e of dd.extra_entities) {
      const metaParts = [];
      if (e.cert_level) metaParts.push(e.cert_level);
      if (e.area) metaParts.push(e.area);
      if (e.workers) metaParts.push(`${e.workers}人`);
      if (e.lines) metaParts.push(`线路:${e.lines}`);
      if (e.daily_flow) metaParts.push(`日均客流${e.daily_flow}`);
      if (e.wtype) metaParts.push(e.wtype);
      if (e.water_area) metaParts.push(`水域${e.water_area}km²`);
      if (e.quality) metaParts.push(`水质${e.quality}`);
      if (e.ftype) metaParts.push(e.ftype);
      if (e.status) metaParts.push(e.status);
      html += `<div class="ov-entity-card">
        <div class="ov-entity-name">${esc(e.name)}</div>
        <div class="ov-entity-meta">${metaParts.map(p => `<span>${esc(p)}</span>`).join('')}</div>
      </div>`;
    }
    html += `</div>`;
  }

  showOvModal(`${dd.icon || ''} ${esc(dd.name)} · 详细数据`, html, {
    onClose: () => { window._ovMarkerFilter = null; refreshOvMapMarkers(); }
  });
}

function initWarnScroll() {
  const track = document.querySelector('.ov-warn-track');
  if (!track) return;
  const clone = track.cloneNode(true);
  track.parentElement.appendChild(clone);
  track.parentElement.style.setProperty('--scroll-w', track.scrollWidth + 'px');
}

function renderPlaceholder(ico, title, desc, plans) {
  document.getElementById('content').innerHTML = `
    <div class="placeholder">
      <div class="ph-ico">${ico}</div>
      <h2>${title}</h2>
      <p>${desc}</p>
      <p style="color:#44557a">该模块将在后续开发步骤中建设（Step 3~7）</p>
      <div class="ph-plan"><h4>规划内容</h4><ul>${plans.map(p => `<li>${p}</li>`).join('')}</ul></div>
    </div>`;
}

/* ---------- Toast 通知 ---------- */
function showToast(msg, type) {
  type = type || 'info';
  let container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  const icons = { info: 'ℹ️', warn: '⚠️', success: '✅' };
  const toast = document.createElement('div');
  toast.className = 'toast ' + type;
  toast.innerHTML = `<span>${icons[type] || '📢'}</span><span>${msg}</span>`;
  container.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transform = 'translateX(60px)'; toast.style.transition = '.3s'; setTimeout(() => toast.remove(), 300); }, 3500);
}

/* ---------- 自动刷新 ---------- */
let autoRefreshTimer = null;
let refreshCountdown = 30;

function startAutoRefresh() {
  if (autoRefreshTimer) clearInterval(autoRefreshTimer);
  refreshCountdown = 30;
  autoRefreshTimer = setInterval(() => {
    refreshCountdown--;
    const dot = document.getElementById('refreshDot');
    if (dot) { dot.textContent = refreshCountdown + 's'; dot.className = 'refresh-dot counting'; }
    if (refreshCountdown <= 0) {
      refreshCountdown = 30;
      if (currentRoute === '/workbench') renderWorkbench();
      else if (currentRoute === '/overview') renderOverview();
      if (dot) dot.className = 'refresh-dot';
    }
  }, 1000);
}

function stopAutoRefresh() {
  if (autoRefreshTimer) { clearInterval(autoRefreshTimer); autoRefreshTimer = null; }
}

/* ---------- 键盘快捷键 ---------- */
document.addEventListener('keydown', e => {
  if (e.key === 'Enter' && document.activeElement && document.activeElement.id === 'globalSearch') {
    showToast('全局搜索功能开发中，请通过「建交数据中枢」浏览数据', 'info');
    return;
  }
  if (e.ctrlKey || e.metaKey) {
    const shortcuts = { '1': '/workbench', '2': '/data', '3': '/overview', '4': '/project', '5': '/topic', '6': '/ai' };
    const route = shortcuts[e.key];
    if (route && currentRoute !== route) { e.preventDefault(); navTo(route); showToast('快捷切换: ' + route, 'info'); }
  }
});

/* ---------- 启动 ---------- */
(async function bootstrap() {
  if (token) {
    const d = await api('/api/auth/userinfo');
    if (d && d.code === 200) { currentUser = d.data; await enterPortal(); return; }
  }
  document.getElementById('loginView').style.display = 'flex';
})();
