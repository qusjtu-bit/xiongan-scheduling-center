# -*- coding: utf-8 -*-
"""
专属智能体 API（Step 7 + 自然语言升级）

智能预警 · 智能分析 · 智能决策 · 智能处置 · AI 自然语言对话
"""
import re
import random
from datetime import date, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import Indicator, IndicatorData, Message, Todo
from app.models import ProjectInfo, ProjectStage, ApprovalRecord, TransportStation, WaterBody, MunicipalNode

ai_bp = Blueprint('ai', __name__)

# =========================== 智能预警 ===========================

@ai_bp.route('/ai/warnings', methods=['GET'])
@jwt_required()
def smart_warnings():
    """规则引擎：综合指标异常 + 历史趋势判断预警"""
    alerts = []
    todo_urgent = Todo.query.filter(Todo.urgency >= 2, Todo.status == 0).count()
    projects_overdue = sum(1 for p in ProjectInfo.query.all()
                           if p.plan_end_date and p.plan_end_date < date.today().isoformat() and p.progress < 100)

    # 检查各领域关键指标
    checks = [
        ('cj04', '工程隐患数', lambda v: v > 60, '在建工程隐患数量偏高，建议工程质量安全处加强现场巡查'),
        ('cj05', '整改闭环率', lambda v: v < 85, '整改闭环率低于85%，请督促各项目限期完成隐患整改'),
        ('jt02', '拥堵指数', lambda v: v > 1.5, '主要路段拥堵指数偏高，建议优化信号配时和公交运力'),
        ('sl04', '水位超警次数', lambda v: v > 3, '水位超警次数较多，请加强防汛巡查和物资储备'),
        ('cg10', '燃气监测异常数', lambda v: v > 8, '燃气管网异常事件偏多，建议组织专项排查'),
        ('cj06', '实名制考勤率', lambda v: v < 88, '实名制考勤率低于88%，可能存在用工管理漏洞'),
        ('sl02', '水质达标率', lambda v: v < 85, '水质达标率下降，请排查上游污染源和污水处理'),
        ('jt05', '公交日均客流', lambda v: v < 8, '公交客流偏低，建议评估线路优化方案'),
    ]

    for code, name, check, advice in checks:
        row = IndicatorData.query.filter_by(indicator_code=code).order_by(
            IndicatorData.period.desc()).first()
        if row and check(row.value):
            ind = Indicator.query.filter_by(code=code).first()
            alerts.append({
                'code': code,
                'indicator': ind.name if ind else name,
                'value': round(row.value, 2),
                'unit': ind.unit if ind else '',
                'advice': advice,
                'severity': 'high' if row.value > (60 if '%' not in (ind.unit if ind else '') else 90) else 'medium',
            })

    # 综合分析
    summary = f'当前系统运行正常，在建项目{ProjectInfo.query.count()}个'
    if projects_overdue > 0:
        summary += f'，其中{projects_overdue}个项目逾期需重点关注'
    if todo_urgent > 0:
        summary += f'，紧急待办{todo_urgent}项待处理'
    if len(alerts) > 3:
        summary += '。系统检测到多项指标异常，建议启动专项督查'
    else:
        summary += '。各项指标总体平稳'

    return jsonify(code=200, message='success', data={
        'alerts': alerts,
        'summary': summary,
        'stats': {
            'total_checks': len(checks),
            'triggered': len(alerts),
            'urgent_todos': todo_urgent,
            'overdue_projects': projects_overdue,
        },
    })


# =========================== 智能分析 ===========================

@ai_bp.route('/ai/analyze', methods=['POST'])
@jwt_required()
def smart_analyze():
    """生成月度态势分析报告（规则模板）"""
    d = request.get_json(silent=True) or {}
    domain = d.get('domain', 0)

    analyses = []
    if domain in (0, 1):
        cj01 = IndicatorData.query.filter_by(indicator_code='cj01').order_by(
            IndicatorData.period.desc()).first()
        cj14 = IndicatorData.query.filter_by(indicator_code='cj14').order_by(
            IndicatorData.period.desc()).first()
        analyses.append({
            'domain': 1, 'name': '城乡建设',
            'content': f'在建项目{int(cj01.value) if cj01 else "—"}个，总投资约{cj14.value if cj14 else "—"}亿元。'
                       f'实名制考勤率与消防验收通过率总体平稳，建议持续强化深基坑、高支模等危大工程安全管控。',
            'highlights': ['在建项目数量稳中有升', '装配式建筑占比持续提高', '安全生产形势总体可控'],
        })
    if domain in (0, 2):
        jt03 = IndicatorData.query.filter_by(indicator_code='jt03').order_by(
            IndicatorData.period.desc()).first()
        analyses.append({
            'domain': 2, 'name': '交通运输',
            'content': f'路网运行总体畅通，公交线路{int(jt03.value) if jt03 else "—"}条正常运行。'
                       f'雄安站日均到发客流稳定，新能源公交占比持续提升。建议关注高峰时段拥堵疏导。',
            'highlights': ['新能源公交占比稳步提升', '雄安站枢纽运行顺畅', '非法营运查处力度加大'],
        })
    if domain in (0, 3):
        sl02 = IndicatorData.query.filter_by(indicator_code='sl02').order_by(
            IndicatorData.period.desc()).first()
        analyses.append({
            'domain': 3, 'name': '水利水务',
            'content': f'水质达标率{sl02.value if sl02 else "—"}%，河湖长巡查制度落实到位。'
                       f'防汛物资储备充足，泵站运行率正常。建议持续关注白洋淀生态补水与水质改善。',
            'highlights': ['河湖长巡查覆盖率达100%', '防汛物资储备率达标', '供水管网漏损率持续下降'],
        })
    if domain in (0, 4):
        cg01 = IndicatorData.query.filter_by(indicator_code='cg01').order_by(
            IndicatorData.period.desc()).first()
        analyses.append({
            'domain': 4, 'name': '城市管理',
            'content': f'环卫覆盖率{cg01.value if cg01 else "—"}%，道路完好率与路灯亮灯率保持高位。'
                       f'综合管廊运营里程稳步增长，井盖异常事件处置及时。建议加快推进智慧城管平台对接。',
            'highlights': ['路灯亮灯率保持98%以上', '井盖异常处置及时率提升', '综合管廊运营里程增长'],
        })

    return jsonify(code=200, message='success', data={
        'analyses': analyses,
        'generated_at': date.today().isoformat(),
        'model': '建交协同调度中心 · 智能分析引擎 v1.0',
    })


# =========================== 智能决策 ===========================

@ai_bp.route('/ai/decide', methods=['POST'])
@jwt_required()
def smart_decide():
    d = request.get_json(silent=True) or {}
    scenario = d.get('scenario', 'default')
    decisions = {
        'flood': {
            'title': '防汛应急决策建议',
            'actions': [
                {'step': 1, 'action': '启动防汛应急响应预案', 'dept': '水利组', 'urgency': '紧急'},
                {'step': 2, 'action': '通知沿河项目停工撤人', 'dept': '工程质量安全处', 'urgency': '紧急'},
                {'step': 3, 'action': '加密水位雨量监测频次至每30分钟', 'dept': '水利组', 'urgency': '高'},
                {'step': 4, 'action': '调拨防汛物资至重点区域', 'dept': '办公室', 'urgency': '高'},
                {'step': 5, 'action': '通知白洋淀船舶回港避风', 'dept': '综合交通组', 'urgency': '中'},
            ],
            'reasoning': '基于雨量超阈值+水位快速上涨趋势，建议立即启动IV级响应并做好升级准备',
        },
        'overdue': {
            'title': '逾期项目处置建议',
            'actions': [
                {'step': 1, 'action': '向逾期项目建设单位发出督办函', 'dept': '城乡发展处', 'urgency': '高'},
                {'step': 2, 'action': '组织约谈项目负责人', 'dept': '城乡发展处', 'urgency': '高'},
                {'step': 3, 'action': '重新倒排工期并报备', 'dept': '工程质量安全处', 'urgency': '中'},
                {'step': 4, 'action': '纳入月度绩效考核扣分项', 'dept': '办公室', 'urgency': '中'},
            ],
            'reasoning': '项目逾期将影响片区整体建设时序，需从行政+经济手段双管齐下推动进度',
        },
        'default': {
            'title': '日常调度决策建议',
            'actions': [
                {'step': 1, 'action': '优先处置紧急预警事项', 'dept': '调度中心', 'urgency': '高'},
                {'step': 2, 'action': '召开月度调度例会', 'dept': '办公室', 'urgency': '中'},
                {'step': 3, 'action': '汇总各业务处室周报', 'dept': '各业务处室', 'urgency': '中'},
                {'step': 4, 'action': '更新数据中枢指标数据', 'dept': '信息化处', 'urgency': '低'},
                {'step': 5, 'action': '开展安全生产月专项检查', 'dept': '工程质量安全处', 'urgency': '中'},
            ],
            'reasoning': '系统运行平稳，按日常调度节奏推进各项工作，重点关注临近预警项',
        },
    }
    result = decisions.get(scenario, decisions['default'])
    return jsonify(code=200, message='success', data=result)


# =========================== 智能处置 ===========================

@ai_bp.route('/ai/dispatch', methods=['POST'])
@jwt_required()
def smart_dispatch():
    d = request.get_json(silent=True) or {}
    event_type = d.get('type', 'default')
    templates = {
        'safety': {
            'title': '安全隐患智能分派',
            'todo': {'todo_type': 2, 'source_system': 'AI智能体', 'urgency': 3,
                     'due_date': (date.today().replace(day=min(date.today().day + 2, 28))).isoformat()},
            'message': {'msg_type': 2, 'level': 3,
                        'content': 'AI智能体检测到安全隐患指标异常，已自动生成处置工单。请责任处室在48小时内完成核查并反馈。'},
        },
        'default': {
            'title': '常规事件智能分派',
            'todo': {'todo_type': 4, 'source_system': 'AI智能体', 'urgency': 1,
                     'due_date': (date.today().replace(day=min(date.today().day + 5, 28))).isoformat()},
            'message': {'msg_type': 4, 'level': 1,
                        'content': 'AI智能体已自动识别并分派事件，请及时处理。'},
        },
    }
    tpl = templates.get(event_type, templates['default'])
    return jsonify(code=200, message='success', data={
        'dispatched': True,
        'template': tpl['title'],
        'todo_preview': tpl['todo'],
        'message_preview': tpl['message'],
    })


# =========================== AI 自然语言对话 ===========================

# ---------- 实体识别 ----------
def _extract_entities(query):
    """抽取领域/项目/指标/时间/数据维度等实体"""
    q = query
    ents = {
        'domains': [],
        'projects': [],
        'indicators': [],
        'time_range': None,
        'actions': [],
    }
    # 领域
    domain_map = {
        '城乡': 1, '建设': 1, '工程': 1, '建筑': 1, '城建': 1,
        '交通': 2, '运输': 2, '公交': 2, '道路': 2, '路网': 2,
        '水利': 3, '水务': 3, '防汛': 3, '河湖': 3, '白洋淀': 3,
        '城管': 4, '市政': 4, '环卫': 4, '管廊': 4, '燃气': 4, '井盖': 4,
    }
    for kw, did in domain_map.items():
        if kw in q:
            if did not in ents['domains']:
                ents['domains'].append(did)

    # 动作
    action_map = ['分析', '预警', '决策', '派单', '派工单', '生成报告', '总结', '说明',
                  '介绍一下', '什么是', '为什么', '怎么办', '怎么处理', '什么情况',
                  '风险', '建议', '整改', '处置', '上报', '落实']
    for a in action_map:
        if a in q:
            ents['actions'].append(a)

    # 时间
    if '今天' in q or '今日' in q:
        ents['time_range'] = 'today'
    elif '本周' in q or '这周' in q:
        ents['time_range'] = 'week'
    elif '本月' in q or '这个月' in q or '月度' in q or '月报' in q:
        ents['time_range'] = 'month'
    elif '今年' in q or '年度' in q or '年报' in q:
        ents['time_range'] = 'year'

    # 项目实体（粗匹配名称）
    all_projects = ProjectInfo.query.all()
    for p in all_projects:
        if p.name and p.name in q:
            ents['projects'].append(p)

    return ents


DOMAIN_NAME = {0: '全局', 1: '城乡建设', 2: '交通运输', 3: '水利水务', 4: '城市管理'}

def _ptype_to_domain(ptype):
    """项目类型 → 领域编码（1城乡/2交通/3水利/4城管）"""
    if not ptype:
        return 1
    p = str(ptype)
    if any(k in p for k in ['房建', '市政', '园林', '建筑', '城建']):
        return 1
    if any(k in p for k in ['交通', '道路', '桥梁', '轨道']):
        return 2
    if any(k in p for k in ['水利', '水务', '河湖']):
        return 3
    if any(k in p for k in ['管廊', '燃气', '井盖', '路灯', '环卫', '城管', '市政']):
        return 4
    return 1

# ---------- 数据采集 ----------
def _gather_context(ents):
    """根据实体从数据库采集真实数据，作为生成素材"""
    ctx = {
        'project_total': ProjectInfo.query.count(),
        'projects_by_stage': {},
        'projects_overdue': [],
        'projects_near_due': [],
        'alerts': [],
        'urgent_todos': Todo.query.filter(Todo.urgency >= 2, Todo.status == 0).count(),
        'pending_approvals': sum(1 for a in ApprovalRecord.query.all() if a.status in (0, 2)),
        'domain_indicators': {},   # {domain: [(name, value, unit, trend)]}
        'domain_panels': {},       # {domain: {total, healthy, warning, danger}}
        'msg_unread': Message.query.filter_by(read_flag=0).count() if hasattr(Message, 'read_flag') else 0,
    }

    # 项目阶段分布
    stages = ['立项', '规划', '审批', '建设', '验收', '运维']
    for s in stages:
        ctx['projects_by_stage'][s] = sum(1 for p in ProjectInfo.query.all() if p.stage == s)

    # 逾期项目
    today = date.today().isoformat()
    for p in ProjectInfo.query.all():
        if p.plan_end_date and p.plan_end_date < today and p.progress is not None and p.progress < 100:
            ctx['projects_overdue'].append(p)
        elif p.plan_end_date and ctx['projects_overdue'] is not None:
            # 临期
            try:
                d_end = date.fromisoformat(p.plan_end_date)
                if 0 <= (d_end - date.today()).days <= 30 and (p.progress or 0) < 80:
                    ctx['projects_near_due'].append(p)
            except Exception:
                pass

    # 指标（按领域）
    for code, name, check, advice in [
        ('cj04', '工程隐患数', lambda v: v > 60, ''),
        ('cj05', '整改闭环率', lambda v: v < 85, ''),
        ('jt02', '拥堵指数', lambda v: v > 1.5, ''),
        ('sl04', '水位超警次数', lambda v: v > 3, ''),
        ('cg10', '燃气监测异常数', lambda v: v > 8, ''),
    ]:
        row = IndicatorData.query.filter_by(indicator_code=code).order_by(IndicatorData.period.desc()).first()
        if row:
            ctx['alerts'].append({'code': code, 'name': name, 'value': row.value, 'warn': check(row.value)})

    return ctx


# ---------- 表达模板 ----------
def _greet():
    pool = [
        '您好！我是建交协同调度中心的智能助手小安。',
        '欢迎使用雄安建交协同调度中心AI助手。',
        '您好！智能助手已就位，随时为您服务。',
    ]
    return random.choice(pool)


def _answer_overview(ents, ctx):
    """全局概览型回答"""
    parts = []
    parts.append(f'截至今日，系统共监测{ctx["project_total"]}个在建/竣工项目，覆盖城乡建设、交通运输、水利水务、城市管理四大业务领域。')
    # 阶段分布
    if ctx['projects_by_stage']:
        st = '、'.join([f'{k}阶段{v}个' for k, v in ctx['projects_by_stage'].items() if v > 0][:3])
        if st:
            parts.append(f'目前项目主要集中在{st}。')
    # 风险
    if ctx['projects_overdue']:
        names = '、'.join([p.name for p in ctx['projects_overdue'][:3]])
        parts.append(f'⚠️ 需特别关注逾期项目 {len(ctx["projects_overdue"])} 个，包括{names}{"等" if len(ctx["projects_overdue"]) > 3 else ""}，建议立即组织专项协调。')
    else:
        parts.append('所有项目按期推进，暂无逾期情况。')
    if ctx['urgent_todos'] > 0:
        parts.append(f'当前有{ctx["urgent_todos"]}项紧急待办事项等待处理，可在「消息中心」统一查看。')
    # 指标
    if ctx['alerts']:
        warn_names = [a['name'] for a in ctx['alerts'] if a['warn']]
        if warn_names:
            parts.append(f'指标侧，{ "、".join(warn_names)} 已触发预警阈值，建议相关处室开展核查。')
    return '\n'.join(parts), ['我可以为您展开某个领域的详细分析，或生成月度态势报告。', '是否需要我启动逾期项目处置决策流程？']


def _answer_domain(ents, ctx, domain_id):
    """单领域深入回答"""
    dom_name = DOMAIN_NAME[domain_id]
    parts = []
    # 该领域项目数
    proj = [p for p in ProjectInfo.query.all() if _ptype_to_domain(p.ptype) == domain_id]
    if proj:
        stages = {}
        for p in proj:
            stages[p.stage or '未填写'] = stages.get(p.stage or '未填写', 0) + 1
        stage_str = '、'.join([f'{k}{v}个' for k, v in stages.items()][:3])
        parts.append(f'{dom_name}领域当前在监项目{len(proj)}个，{stage_str}。')
    # 该领域预警
    DOMAIN_CODES = {
        1: [('cj04', '工程隐患数'), ('cj05', '整改闭环率'), ('cj06', '实名制考勤率')],
        2: [('jt02', '拥堵指数'), ('jt05', '公交日均客流')],
        3: [('sl04', '水位超警次数'), ('sl02', '水质达标率')],
        4: [('cg10', '燃气监测异常数')],
    }
    rows = []
    for code, name in DOMAIN_CODES.get(domain_id, []):
        row = IndicatorData.query.filter_by(indicator_code=code).order_by(IndicatorData.period.desc()).first()
        ind = Indicator.query.filter_by(code=code).first()
        if row and ind:
            rows.append((ind, row))
    if rows:
        parts.append(f'核心指标最新读数：')
        for ind, row in rows:
            parts.append(f'  · {ind.name}：{row.value}{ind.unit}（{row.period}）')
    # 建议
    if domain_id == 1:
        advice = '建议本周内组织一次工程质量安全专项抽查，重点核查深基坑、高支模、塔吊等危大工程。'
    elif domain_id == 2:
        advice = '建议关注早高峰（7:30-9:00）和晚高峰（17:30-19:00）拥堵指数变化，必要时启动公交应急运力。'
    elif domain_id == 3:
        advice = '当前正值汛期，建议加密水位监测频次至每30分钟一次，并清点补充防汛物资。'
    else:
        advice = '建议结合夏季用电高峰，加强对燃气、供电设施的巡检频次。'
    parts.append(advice)
    return '\n'.join(parts), [f'需要我为{dom_name}生成一份月度态势分析报告吗？', f'想了解{dom_name}的逾期项目详情吗？']


def _answer_project(ents, ctx):
    """项目相关问题"""
    if ents['projects']:
        p = ents['projects'][0]
        stages = ProjectStage.query.filter_by(project_id=p.id).order_by(ProjectStage.stage_order).all()
        approvals = ApprovalRecord.query.filter_by(project_id=p.id).order_by(ApprovalRecord.apply_date.desc()).all()
        parts = [f'关于「{p.name}」，为您整理如下信息：']
        parts.append(f'· 所属领域：{DOMAIN_NAME.get(_ptype_to_domain(p.ptype), "-")}')
        parts.append(f'· 当前阶段：{p.stage or "未填写"}（{p.progress or 0}%）')
        parts.append(f'· 建设单位：{p.build_unit or "-"}')
        parts.append(f'· 计划工期：{p.start_date or "-"} 至 {p.plan_end_date or "-"}')
        if p.contractor:
            parts.append(f'· 施工单位：{p.contractor}')
        if p.supervisor:
            parts.append(f'· 监理单位：{p.supervisor}')
        # 风险判断
        risk = '无'
        if p.plan_end_date and p.plan_end_date < date.today().isoformat() and (p.progress or 0) < 100:
            risk = '🔴 已逾期'
        elif p.plan_end_date:
            try:
                d_end = date.fromisoformat(p.plan_end_date)
                if 0 <= (d_end - date.today()).days <= 30 and (p.progress or 0) < 80:
                    risk = '🟡 临期'
            except Exception:
                pass
        parts.append(f'· 风险等级：{risk}')
        # 阶段进度
        if stages:
            parts.append('· 阶段进度：')
            for s in stages[:4]:
                mark = '✅' if s.status == '已完成' else ('🔄' if s.status == '进行中' else '⏳')
                parts.append(f'  {mark} {s.stage_name}（{s.stage_order}/6）{s.plan_start_date or ""} - {s.plan_end_date or ""}')
        # 审批
        if approvals:
            appr = approvals[0]
            parts.append(f'· 最新审批：{appr.approval_type}（{appr.status}），办理人 {appr.approver or "-"}')
        return '\n'.join(parts), [f'想看「{p.name}」的全部审批记录吗？', f'需要我为该项目生成一份阶段进度分析吗？']
    # 无具体项目 → 项目总览
    parts = [f'系统共收录{ctx["project_total"]}个项目。']
    if ctx['projects_overdue']:
        names = '、'.join([p.name for p in ctx['projects_overdue'][:5]])
        parts.append(f'其中逾期项目{len(ctx["projects_overdue"])}个：{names}{"等" if len(ctx["projects_overdue"]) > 5 else ""}。')
    else:
        parts.append('目前所有项目均按计划推进。')
    if ctx['projects_near_due']:
        parts.append(f'另有{len(ctx["projects_near_due"])}个项目临近完工期（30天内），需重点跟进。')
    if ctx['pending_approvals'] > 0:
        parts.append(f'当前有{ctx["pending_approvals"]}项审批待处理，可在「规建管一体化」中查看详情。')
    return '\n'.join(parts), ['想了解某个具体项目的进度吗？告诉我项目名称即可。', '我可以为逾期项目生成处置建议，是否需要？']


def _answer_warning(ents, ctx):
    parts = []
    if ctx['alerts']:
        warn = [a for a in ctx['alerts'] if a['warn']]
        if warn:
            parts.append(f'当前系统已触发{len(warn)}项预警：')
            for a in warn:
                parts.append(f'  ⚠️ {a["name"]}：最新读数 {a["value"]}，已超出安全阈值')
            parts.append('建议立即查看「态势大屏」和「智能预警」模块，按严重程度分级处置。')
        else:
            parts.append('✅ 当前所有核心指标均在安全阈值内，系统运行平稳。')
    if ctx['urgent_todos'] > 0:
        parts.append(f'⚠️ 您当前有{ctx["urgent_todos"]}项紧急待办，建议优先处理。')
    return '\n'.join(parts), ['需要我启动处置决策流程吗？', '我可以列出全部待办并按紧急程度排序。']


def _answer_decision(ents, ctx):
    parts = ['我可以基于实时数据为您提供决策建议。常用场景包括：']
    parts.append('· 🚨 防汛应急：基于雨量水位数据，启动IV/III级应急响应')
    parts.append('· 🏗️ 逾期处置：行政+经济双管齐下，推动项目复工')
    parts.append('· 📅 日常调度：按月度例会节奏推进各项工作')
    parts.append('请在「智能决策」面板选择具体场景，或告诉我您当前面临的实际问题。')
    return '\n'.join(parts), ['想让我分析一个具体场景吗？', '需要我根据当前指标自动推荐最合适的处置方案吗？']


def _answer_report(ents, ctx):
    if ents['domains']:
        d = ents['domains'][0]
        return (f'好的，我已为您准备{DOMAIN_NAME[d]}领域的月度态势分析报告。可在「智能分析」模块中点击"生成分析"查看完整报告。'
                f'报告将涵盖该领域的核心指标走势、项目阶段分布、风险点提示和下月工作建议。',
                [f'需要我同时输出其他领域的报告吗？', '报告支持导出为 PDF，是否需要？'])
    return ('我可以为您生成多领域态势分析报告，包括核心指标分析、阶段分布、风险预警和工作建议四部分。'
            '请告诉我您想了解哪个领域，或者直接说"生成月度报告"。',
            ['想分析某个具体领域吗？', '需要包含数据可视化图表吗？'])


def _answer_dispatch(ents, ctx):
    return ('我可以将识别到的异常事件自动转化为工单，分派到对应处室，并附上建议处理时限。'
            '如需演示，请在「智能处置」面板选择事件类型（安全隐患/常规事件），点击"模拟分派"即可。',
            ['想立即分派一个安全隐患工单吗？', '需要先查看当前所有待办吗？'])


def _answer_chitchat(ents, ctx, raw):
    """兜底自然对话"""
    greetings = ['你好', '您好', 'hi', 'hello', '在吗']
    if any(g in raw.lower() for g in greetings):
        return f'{_greet()} 请问今天有什么可以帮您？', ['想了解当前系统总体运行情况吗？', '需要我帮您分析某个领域数据吗？']
    if '谢谢' in raw or '感谢' in raw:
        return '不客气！如有任何需要，随时告诉我。', ['还有其他事项需要协助吗？']
    if '你是谁' in raw or '你是什么' in raw:
        return ('我是建交协同调度中心的智能助手，融合了数据中枢、态势感知、规则引擎和自然语言理解能力，'
                '可以为局领导、处室负责人和经办人提供态势分析、预警提示、决策建议和工单分派等服务。', [])
    if '能做什么' in raw or '功能' in raw or '会什么' in raw:
        return ('我可以做这些事情：\n'
                '1. 🛰️ 实时回答系统运行态势（项目、指标、预警、待办）\n'
                '2. 📊 按领域（建设/交通/水利/城管）深入分析指标和项目\n'
                '3. 🏗️ 查询具体项目阶段、风险和审批进度\n'
                '4. 📝 自动生成月度态势分析报告\n'
                '5. 🧠 基于场景给出决策建议（防汛/逾期/日常）\n'
                '6. 📋 智能分派异常事件为待办工单\n'
                '7. 💬 自然语言多轮对话与追问引导', ['想从哪里开始？告诉我一个领域或场景即可。'])
    if '再见' in raw or '拜拜' in raw:
        return '好的，随时为您服务！👋', []
    # 兜底
    pool = [
        '好的，已收到您的需求。我已结合当前系统数据进行分析，整理如下要点：\n',
    ]
    return (f'{_greet()}{random.choice(pool)}当前系统监测{ctx["project_total"]}个项目，'
            f'触发预警{len([a for a in ctx["alerts"] if a["warn"]])}项，'
            f'紧急待办{ctx["urgent_todos"]}项。'
            f'如需了解某个具体领域、项目或场景，请告诉我。',
            ['想从哪个领域开始？', '需要我为您生成一份日报吗？'])


# ---------- 主路由 ----------
@ai_bp.route('/ai/chat', methods=['POST'])
@jwt_required()
def ai_chat():
    """自然语言生成式对话：实体识别 + 数据驱动 + 多样化表达 + 追问引导 + 上下文记忆"""
    d = request.get_json(silent=True) or {}
    query = (d.get('query') or '').strip()
    history = d.get('history') or []  # 多轮上下文 [{role, content}]

    if not query:
        return jsonify(code=200, message='success', data={
            'reply': f'{_greet()}请问今天有什么可以帮您？',
            'followups': ['想了解系统当前运行态势吗？', '需要分析某个领域数据吗？'],
            'model': '建交协同调度中心 · AI 智能体 v2.0 (自然语言生成引擎)',
        })

    ents = _extract_entities(query)
    ctx = _gather_context(ents)

    # 上下文联想：如果当前问题很短（"详细说说"/"为什么呢"），从历史中承接领域
    if history and len(query) < 12 and any(w in query for w in ['详细', '展开', '为什么', '怎么办', '说', '呢', '？']):
        for h in reversed(history[-3:]):
            if h.get('role') == 'user':
                prev_ents = _extract_entities(h.get('content', ''))
                if prev_ents['domains']:
                    ents['domains'] = ents['domains'] or prev_ents['domains']
                if prev_ents['projects']:
                    ents['projects'] = ents['projects'] or prev_ents['projects']
                if prev_ents['actions']:
                    ents['actions'] = list(set(ents['actions'] + prev_ents['actions']))
                break

    # 路由
    if ents['projects'] or any(k in query for k in ['项目', '工程', '工地', '进度', '工期', '竣工', '立项']):
        reply, followups = _answer_project(ents, ctx)
    elif ents['domains']:
        # 多领域取第一个
        reply, followups = _answer_domain(ents, ctx, ents['domains'][0])
    elif any(a in query for a in ['预警', '告警', '异常', '风险', '隐患', '超限']):
        reply, followups = _answer_warning(ents, ctx)
    elif any(a in query for a in ['决策', '建议', '怎么办', '怎么处理', '方案', '处置']):
        reply, followups = _answer_decision(ents, ctx)
    elif any(a in query for a in ['报告', '分析报告', '总结', '月报', '年报']):
        reply, followups = _answer_report(ents, ctx)
    elif any(a in query for a in ['派单', '分派', '工单', '派发', '下发']):
        reply, followups = _answer_dispatch(ents, ctx)
    elif any(k in query for k in ['总', '全', '整体', '运行', '态势', '情况', '概览', '怎么样']):
        reply, followups = _answer_overview(ents, ctx)
    else:
        reply, followups = _answer_chitchat(ents, ctx, query)

    # 补一句尾部引导
    tail_pool = [
        '\n如需进一步分析或调整，请告诉我。',
        '\n以上数据均来自系统实时采集，可追溯。',
        '\n随时告诉我后续问题，我会持续跟进。',
    ]
    if random.random() < 0.6:
        reply += random.choice(tail_pool)

    return jsonify(code=200, message='success', data={
        'reply': reply,
        'followups': followups,
        'entities': {
            'domains': [DOMAIN_NAME.get(d, '') for d in ents['domains']],
            'projects': [p.name for p in ents['projects']],
            'actions': ents['actions'],
            'time_range': ents['time_range'],
        },
        'model': '建交协同调度中心 · AI 智能体 v2.0 (自然语言生成引擎)',
    })
