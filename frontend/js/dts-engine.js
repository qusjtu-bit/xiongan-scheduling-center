/* ============================================================
   DTS 三维引擎适配模块（飞渡 Freedo DigitalTwinPlayer）
   雄安新区建设和交通管理局 · 协同调度中心
   
   用途：为态势大屏中间区域提供三维CIM视图能力
   云渲染架构：三维场景在DTS-Cloud服务器渲染，视频流传入浏览器
   
   接入步骤：
   1. 部署 DTS-Cloud 云渲染服务器
   2. 将 ac.min.js 放入 frontend/js/ 目录
   3. 配置 DTS_ENGINE.config.host 为实际服务器地址
   4. 在 DTS 中加载雄安三维 CIM 场景，获取 sceneId
   ============================================================ */
'use strict';

const DTS_ENGINE = {
  /* ---------- 配置项（部署时修改） ---------- */
  config: {
    host: '',               // DTS云渲染服务器地址（如 '192.168.1.27:8081'）
    domId: 'ovDtsPlayer',   // 渲染容器 div id
    sceneId: '',            // CIM场景ID
  },

  /* ---------- 实例状态 ---------- */
  player: null,             // DigitalTwinPlayer 实例
  api: null,                // airCityApi 实例（getAPI() 返回）
  isAvailable: false,       // DTS服务是否可用
  isConnecting: false,      // 是否正在连接中
  _eventHandlers: {},       // 事件处理器映射

  /* ---------- 检测 DTS SDK 是否已加载 ---------- */
  sdkLoaded() {
    return typeof DigitalTwinPlayer !== 'undefined';
  },

  /* ---------- 初始化 DTS 引擎 ---------- */
  init() {
    if (this.isConnecting || this.isAvailable) return;
    if (!this.config.host) {
      console.warn('[DTS] 未配置云渲染服务器地址');
      return false;
    }
    if (!this.sdkLoaded()) {
      console.warn('[DTS] ac.min.js 未加载，请在 frontend/js/ 中放入 SDK 文件');
      return false;
    }

    this.isConnecting = true;
    const statusEl = document.getElementById('ovDtsStatus');
    if (statusEl) {
      statusEl.innerHTML = '🔄 正在连接三维引擎...';
      statusEl.className = 'ov-dts-status ov-dts-loading';
      statusEl.style.display = '';
    }

    try {
      this.player = new DigitalTwinPlayer(this.config.host, {
        domId: this.config.domId,

        apiOptions: {
          onReady: () => {
            this.isAvailable = true;
            this.isConnecting = false;
            this.api = this.player.getAPI();
            if (statusEl) statusEl.style.display = 'none';
            console.info('[DTS] 三维引擎就绪，API已初始化');
            // 同步当前标记点到三维场景
            this.syncMarkers();
            // 触发自定义就绪事件
            if (this._eventHandlers.onReady) this._eventHandlers.onReady();
          },

          onLog: (s, nnl) => {
            console.info('[DTS]', s, nnl ? '' : '\n');
          },

          onEvent: (e) => {
            this._handleEvent(e);
          },
        },

        ui: {
          startupInfo: true,
          statusButton: true,
        },

        events: {
          onVideoLoaded: () => {
            console.info('[DTS] 视频流加载成功');
          },
          onConnClose: () => {
            this.isAvailable = false;
            this.isConnecting = false;
            console.warn('[DTS] 连接断开');
            if (statusEl) {
              statusEl.innerHTML = '❌ 三维引擎连接断开<br><small>请检查云渲染服务器状态</small>';
              statusEl.className = 'ov-dts-status ov-dts-error';
              statusEl.style.display = '';
            }
          },
        },

        keyEventTarget: 'none',
      });

      console.info('[DTS] 正在连接', this.config.host);
      return true;
    } catch (e) {
      this.isConnecting = false;
      console.error('[DTS] 初始化失败:', e);
      if (statusEl) {
        statusEl.innerHTML = '❌ 三维引擎连接失败<br><small>' + (e.message || '未知错误') + '</small>';
        statusEl.className = 'ov-dts-status ov-dts-error';
        statusEl.style.display = '';
      }
      return false;
    }
  },

  /* ---------- 销毁引擎 ---------- */
  destroy() {
    if (this.api) {
      try { this.api.destroy(); } catch (e) { console.warn('[DTS] destroy 失败:', e); }
      this.api = null;
    }
    this.player = null;
    this.isAvailable = false;
    this.isConnecting = false;
    console.info('[DTS] 引擎已销毁');
  },

  /* ---------- 注册事件处理器 ---------- */
  on(eventName, handler) {
    this._eventHandlers[eventName] = handler;
  },

  /* ---------- 处理三维场景交互事件 ---------- */
  _handleEvent(e) {
    // DTS 事件类型映射到前端业务逻辑
    const eventMap = {
      'LeftMouseButtonClick': 'click',
      'MouseEnter': 'hover',
      'MouseLeave': 'leave',
    };
    const eventType = eventMap[e.eventtype] || e.eventtype;

    // 图层/实体点击事件 → 前端弹窗
    if (eventType === 'click') {
      const entityId = e.Id || e.id;
      const entityType = e.Type || e.type;

      // 查找对应的业务数据
      const marker = (window._ovAllMarkers || []).find(m => m.id === entityId);
      if (marker) {
        // 根据实体类型打开对应详情弹窗
        if (marker.type === 'project') {
          // 项目详情
          openCoreDetail('cj01');
        } else if (marker.type === 'station') {
          openCoreDetail('jt05');
        } else if (marker.type === 'municipal') {
          openDomainDetail(4);
        }
      }

      if (this._eventHandlers.onEntityClick) {
        this._eventHandlers.onEntityClick(e);
      }
    }

    if (this._eventHandlers.onEvent) {
      this._eventHandlers.onEvent(e);
    }
  },

  /* ---------- 相机飞到指定位置 ---------- */
  flyTo(lng, lat, alt, heading, pitch) {
    if (!this.api || !this.isAvailable) return;
    try {
      this.api.camera.flyTo(
        lng || 116.08,
        lat || 39.04,
        alt || 5000,
        heading || 0,
        pitch || -45
      );
    } catch (e) {
      console.warn('[DTS] flyTo 失败:', e);
    }
  },

  /* ---------- 同步二维标记点到三维场景 ---------- */
  syncMarkers() {
    if (!this.api || !this.isAvailable) return;
    const filter = window._ovMarkerFilter;
    if (!filter) return;

    // 先清除三维标记
    this.clearMarkers();

    // 按过滤条件筛选标记
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

    const filtered = (window._ovAllMarkers || []).filter(m => targetTypes.includes(m.type));
    this.addMarkers(filtered);
  },

  /* ---------- 在三维场景中添加标记点 ---------- */
  addMarkers(markers) {
    if (!this.api || !this.isAvailable) return;
    // 标记点添加逻辑 —— 具体实现取决于CIM场景中的实体ID映射
    // 当CIM场景接入后，可通过 TagData / TagStyle API 添加标签
    // 当前为预留接口
    console.info('[DTS] 预留添加标记点:', markers.length, '个');

    // 示例：添加文字标签（需要CIM场景中有对应的实体）
    // for (const m of markers) {
    //   const tagData = new TagData(m.id, m.name, m.lng, m.lat, 0);
    //   this.api.tag.add(tagData, new TagStyle());
    // }
  },

  /* ---------- 清除三维场景标记 ---------- */
  clearMarkers() {
    if (!this.api || !this.isAvailable) return;
    try {
      this.api.tag.clearAll();
    } catch (e) {
      console.warn('[DTS] clearMarkers 失败:', e);
    }
  },

  /* ---------- 显示引擎状态 ---------- */
  showStatus() {
    if (!this.config.host) return '未配置';
    if (!this.sdkLoaded()) return 'SDK未加载';
    if (this.isConnecting) return '连接中';
    if (this.isAvailable) return '已就绪';
    return '未连接';
  },
};

/* ---------- 从后端加载DTS配置 ---------- */
async function loadDtsConfig() {
  try {
    const data = await api('/api/overview/dts-config');
    if (data && data.code === 200 && data.data) {
      const cfg = data.data;
      if (cfg.host) DTS_ENGINE.config.host = cfg.host;
      if (cfg.scene_id) DTS_ENGINE.config.sceneId = cfg.scene_id;
      console.info('[DTS] 配置已加载:', cfg.available ? '可用' : '不可用', cfg.host || '未配置');
      return cfg;
    }
  } catch (e) {
    console.warn('[DTS] 配置加载失败:', e);
  }
  return null;
}
