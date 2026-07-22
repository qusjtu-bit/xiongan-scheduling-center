# -*- coding: utf-8 -*-
"""
态势大屏 API（Step 4）

聚合四大领域核心指标 + GIS地图标记 + 实时预警 + 事件时间线
"""
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app import db
from app.models import Message, Todo, Indicator, IndicatorData
from app.models import ProjectInfo, ProjectStage, ApprovalRecord
from app.models import BusinessLicense, TransportStation, WaterBody, MunicipalNode

overview_bp = Blueprint('overview', __name__)

DOMAIN_LABELS = {1: '城乡建设', 2: '交通运输', 3: '水利水务', 4: '城市管理'}
DOMAIN_ICONS = {1: '🏗️', 2: '🚌', 3: '💧', 4: '🏙️'}


def _get_indicator_val(code):
    """获取指标最新值"""
    row = IndicatorData.query.filter_by(indicator_code=code).order_by(
        IndicatorData.period.desc()).first()
    return round(row.value, 2) if row else None


@overview_bp.route('/overview/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    """态势大屏聚合数据"""

    # ======== 1. 核心指标 ========
    core = {
        'in_progress_projects': int(round(_get_indicator_val('cj01') or 0)),
        'month_permits': int(round(_get_indicator_val('cj02') or 0)),
        'fire_pass_rate': _get_indicator_val('cj03') or 0,
        'hazards': int(round(_get_indicator_val('cj04') or 0)),
        'closure_rate': _get_indicator_val('cj05') or 0,
        'attendance_rate': _get_indicator_val('cj06') or 0,
        'total_invest': _get_indicator_val('cj14') or 0,
        'bus_daily_flow': _get_indicator_val('jt05') or 0,
        'water_quality_rate': _get_indicator_val('sl02') or 0,
        'road_intact_rate': _get_indicator_val('cg04') or 0,
        'green_coverage': _get_indicator_val('cg11') or 0,
        'total_projects': ProjectInfo.query.count(),
        'total_businesses': BusinessLicense.query.count(),
        'total_stations': TransportStation.query.count(),
        'total_waters': WaterBody.query.count(),
        'total_munis': MunicipalNode.query.count(),
    }

    # ======== 2. 四大领域指标面板 ========
    domain_panels = []
    # 各领域选 6 项核心指标
    domain_configs = {
        1: ['cj01', 'cj02', 'cj03', 'cj05', 'cj06', 'cj14'],
        2: ['jt01', 'jt02', 'jt03', 'jt05', 'jt06', 'jt10'],
        3: ['sl01', 'sl02', 'sl04', 'sl06', 'sl08', 'sl13'],
        4: ['cg01', 'cg04', 'cg05', 'cg06', 'cg07', 'cg11'],
    }
    for domain in range(1, 5):
        indicators = []
        for code in domain_configs[domain]:
            ind = Indicator.query.filter_by(code=code).first()
            if ind:
                val = _get_indicator_val(code)
                indicators.append({
                    'code': ind.code, 'name': ind.name, 'value': val,
                    'unit': ind.unit,
                })
        domain_panels.append({
            'domain': domain,
            'name': DOMAIN_LABELS[domain],
            'icon': DOMAIN_ICONS[domain],
            'indicators': indicators,
        })

    # ======== 3. GIS 地图标记（含经纬度的实体） ========
    map_markers = []

    # 城建项目
    stage_colors = {'建设': '#00d4ff', '运维': '#00e676', '规划': '#ffb300'}
    for p in ProjectInfo.query.all():
        map_markers.append({
            'id': f'proj_{p.id}', 'name': p.name, 'type': 'project',
            'type_label': '项目', 'lng': p.lng, 'lat': p.lat,
            'color': stage_colors.get(p.stage, '#00d4ff'),
            'info': f'{p.ptype} · {p.stage} · 投资{int(p.invest/10000)}亿',
        })

    # 公交站点
    for s in TransportStation.query.all():
        map_markers.append({
            'id': f'station_{s.id}', 'name': s.name, 'type': 'station',
            'type_label': '公交站', 'lng': s.lng, 'lat': s.lat,
            'color': '#ffb300',
            'info': f'日均客流 {s.daily_flow} 人次 · 线路 {s.lines}',
        })

    # 市政设施（仅含坐标的）
    for m in MunicipalNode.query.all():
        map_markers.append({
            'id': f'muni_{m.id}', 'name': m.name, 'type': 'municipal',
            'type_label': m.ftype, 'lng': m.lng, 'lat': m.lat,
            'color': '#e040fb' if m.status == '异常' else '#69f0ae',
            'info': f'{m.ftype} · {m.area} · {m.status}',
        })

    # ======== 4. 实时预警 TOP8 ========
    warnings = []
    msgs = Message.query.filter(
        Message.msg_type == 2,  # 预警消息
    ).order_by(Message.level.desc(), Message.created_at.desc()).limit(8).all()
    for m in msgs:
        warnings.append({
            'id': m.id, 'title': m.title,
            'level': m.level,
            'level_label': {1: '一般', 2: '较重', 3: '严重'}.get(m.level, '一般'),
            'sender': m.sender,
            'content': m.content or '暂无详细内容',
            'created_at': m.created_at.strftime('%m-%d %H:%M') if m.created_at else '',
        })

    # ======== 5. 事件时间线（消息+待办混合，最近15条） ========
    timeline = []
    # 近期消息
    recent_msgs = Message.query.order_by(Message.created_at.desc()).limit(10).all()
    for m in recent_msgs:
        timeline.append({
            'type': 'msg',
            'icon': {1: '📢', 2: '⚠️', 3: '📋', 4: '⚙️'}.get(m.msg_type, '📢'),
            'title': m.title,
            'time': m.created_at.strftime('%m-%d %H:%M') if m.created_at else '',
            'tag': m.level >= 3 and '紧急' or '',
        })
    # 近期待办
    recent_todos = Todo.query.filter(Todo.urgency >= 2).order_by(Todo.due_date.asc()).limit(5).all()
    for t in recent_todos:
        timeline.append({
            'type': 'todo',
            'icon': '📋',
            'title': t.title,
            'time': f'截止 {t.due_date}' if t.due_date else '',
            'tag': '紧急' if t.urgency >= 3 else '',
        })
    # 按时间排序
    timeline.sort(key=lambda x: x.get('time', ''), reverse=True)

    # ======== 6. 领域统计分布 ========
    domain_stats = []
    for domain in range(1, 5):
        ind_count = Indicator.query.filter_by(domain=domain).count()
        projects = ProjectInfo.query.filter_by().all()  # domain filtering happens in-code
        # project types → domain mapping
        ptype_domain = {
            '房建': 1, '市政': 1, '交通': 2, '水利': 3, '园林': 4,
        }
        proj_count = sum(1 for p in projects if ptype_domain.get(p.ptype) == domain)
        records = 0
        if domain == 1:
            records = ProjectInfo.query.count() + BusinessLicense.query.count()
        elif domain == 2:
            records = TransportStation.query.count()
        elif domain == 3:
            records = WaterBody.query.count()
        elif domain == 4:
            records = MunicipalNode.query.count()
        domain_stats.append({
            'domain': domain, 'name': DOMAIN_LABELS[domain],
            'indicators': ind_count, 'projects': proj_count,
            'records': records,
        })

    return jsonify(code=200, message='success', data={
        'core': core,
        'domain_panels': domain_panels,
        'map_markers': map_markers,
        'warnings': warnings,
        'timeline': timeline,
        'domain_stats': domain_stats,
    })


# ===================================================================
#  核心指标详情下钻
# ===================================================================

@overview_bp.route('/overview/core-detail', methods=['POST'])
@jwt_required()
def core_detail():
    """根据指标编码返回详情明细数据"""
    code = request.json.get('code', '')
    if not code:
        return jsonify(code=400, message='缺少指标编码'), 400

    data = {'code': code, 'rows': [], 'title': '', 'columns': []}

    if code == 'cj01':
        # 在建项目列表
        data['title'] = '在建项目清单'
        data['columns'] = ['项目名称', '类型', '片区', '投资(亿元)', '进度', '阶段']
        projects = ProjectInfo.query.filter(ProjectInfo.stage.in_(['建设', '施工'])).all()
        for p in projects:
            data['rows'].append([
                p.name, p.ptype, p.area,
                round(p.invest / 10000, 1), f'{p.progress}%', p.stage,
            ])

    elif code == 'cj02':
        # 本月办件 — 审批记录
        data['title'] = '本月审批办件'
        data['columns'] = ['审批类型', '关联项目', '申请日期', '状态', '审批人']
        now = datetime.now()
        month_start = f'{now.year}-{now.month:02d}'
        records = ApprovalRecord.query.filter(
            ApprovalRecord.apply_date.like(f'{month_start}%')
        ).all()
        proj_map = {p.id: p.name for p in ProjectInfo.query.all()}
        for r in records:
            data['rows'].append([
                r.approval_type, proj_map.get(r.project_id, '-'),
                r.apply_date, r.status, r.approver or '-',
            ])

    elif code == 'cj03':
        # 消防验收通过率 — 消防验收记录
        data['title'] = '消防验收记录'
        data['columns'] = ['审批类型', '关联项目', '申请日期', '结果', '审批人']
        records = ApprovalRecord.query.filter(
            ApprovalRecord.approval_type.like('%消防%')
        ).all()
        proj_map = {p.id: p.name for p in ProjectInfo.query.all()}
        total = len(records)
        passed = sum(1 for r in records if r.status == '已通过')
        data['summary'] = f'共 {total} 项，已通过 {passed} 项，通过率 {round(passed/total*100,1) if total else 0}%'
        for r in records:
            data['rows'].append([
                r.approval_type, proj_map.get(r.project_id, '-'),
                r.apply_date, r.status, r.approver or '-',
            ])

    elif code == 'cj04':
        # 隐患数 — 用 IndicatorData 返回近期趋势
        data['title'] = '隐患统计'
        data['columns'] = ['周期', '隐患数量']
        records = IndicatorData.query.filter_by(indicator_code='cj04').order_by(
            IndicatorData.period.desc()).limit(12).all()
        for r in records:
            data['rows'].append([r.period, int(r.value)])
        ind = Indicator.query.filter_by(code='cj04').first()
        data['summary'] = ind.definition if ind and ind.definition else ''

    elif code == 'cj05':
        # 整改闭环率 — 近期趋势
        data['title'] = '整改闭环率'
        data['columns'] = ['周期', '闭环率(%)']
        records = IndicatorData.query.filter_by(indicator_code='cj05').order_by(
            IndicatorData.period.desc()).limit(12).all()
        for r in records:
            data['rows'].append([r.period, r.value])
        ind = Indicator.query.filter_by(code='cj05').first()
        data['summary'] = ind.definition if ind and ind.definition else ''

    elif code == 'cj06':
        # 考勤率 — 近期趋势
        data['title'] = '考勤率统计'
        data['columns'] = ['周期', '考勤率(%)']
        records = IndicatorData.query.filter_by(indicator_code='cj06').order_by(
            IndicatorData.period.desc()).limit(12).all()
        for r in records:
            data['rows'].append([r.period, r.value])
        ind = Indicator.query.filter_by(code='cj06').first()
        data['summary'] = ind.definition if ind and ind.definition else ''

    elif code == 'cj14':
        # 总投资
        data['title'] = '项目投资汇总'
        data['columns'] = ['项目名称', '类型', '片区', '投资(万元)', '阶段']
        projects = ProjectInfo.query.order_by(ProjectInfo.invest.desc()).all()
        for p in projects:
            data['rows'].append([
                p.name, p.ptype, p.area,
                round(p.invest, 0), p.stage,
            ])

    elif code == 'jt05':
        # 公交日客流
        data['title'] = '公交站点客流排名'
        data['columns'] = ['站点名称', '途经线路', '日均客流(人次)']
        stations = TransportStation.query.order_by(
            TransportStation.daily_flow.desc()).all()
        for s in stations:
            data['rows'].append([s.name, s.lines, s.daily_flow])

    return jsonify(code=200, message='success', data=data)


# ===================================================================
#  领域详情下钻
# ===================================================================

@overview_bp.route('/overview/domain-detail/<int:domain>', methods=['GET'])
@jwt_required()
def domain_detail(domain):
    """返回某一领域的完整指标 + 实体列表"""
    if domain not in DOMAIN_LABELS:
        return jsonify(code=400, message='无效领域'), 400

    # 全部指标
    indicators = Indicator.query.filter_by(domain=domain).order_by(
        Indicator.sort, Indicator.code).all()
    ind_list = []
    for ind in indicators:
        val = _get_indicator_val(ind.code)
        ind_list.append({
            'code': ind.code, 'name': ind.name,
            'value': val, 'unit': ind.unit,
            'definition': ind.definition or '',
        })

    # 实体列表
    ptype_domain = {'房建': 1, '市政': 1, '交通': 2, '水利': 3, '园林': 4}
    entities = []
    projects = ProjectInfo.query.all()
    domain_projects = [p for p in projects if ptype_domain.get(p.ptype) == domain]
    for p in domain_projects:
        entities.append({
            'type': 'project', 'id': p.id, 'name': p.name,
            'ptype': p.ptype, 'area': p.area,
            'invest': p.invest, 'progress': p.progress, 'stage': p.stage,
            'lng': p.lng, 'lat': p.lat,
        })

    # 领域特有实体
    extra_entities = []
    if domain == 1:
        businesses = BusinessLicense.query.all()
        for b in businesses:
            extra_entities.append({
                'type': 'business', 'id': b.id, 'name': b.name,
                'cert_level': b.cert_level, 'area': b.area, 'workers': b.workers,
            })
    elif domain == 2:
        stations = TransportStation.query.all()
        for s in stations:
            extra_entities.append({
                'type': 'station', 'id': s.id, 'name': s.name,
                'lines': s.lines, 'daily_flow': s.daily_flow,
                'lng': s.lng, 'lat': s.lat,
            })
    elif domain == 3:
        waters = WaterBody.query.all()
        for w in waters:
            extra_entities.append({
                'type': 'water', 'id': w.id, 'name': w.name,
                'wtype': w.wtype, 'area': w.area,
                'water_area': w.water_area, 'quality': w.quality,
            })
    elif domain == 4:
        munis = MunicipalNode.query.all()
        for m in munis:
            extra_entities.append({
                'type': 'municipal', 'id': m.id, 'name': m.name,
                'ftype': m.ftype, 'area': m.area, 'status': m.status,
                'lng': m.lng, 'lat': m.lat,
            })

    return jsonify(code=200, message='success', data={
        'domain': domain,
        'name': DOMAIN_LABELS[domain],
        'icon': DOMAIN_ICONS[domain],
        'indicators': ind_list,
        'entities': entities,
        'extra_entities': extra_entities,
        'stats': {
            'total_projects': len(entities),
            'total_indicators': len(ind_list),
            'total_extra': len(extra_entities),
        },
    })
