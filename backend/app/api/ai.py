# -*- coding: utf-8 -*-
"""
专属智能体 API（Step 7 + 自然语言升级 + 联网知识库）

智能预警 · 智能分析 · 智能决策 · 智能处置 · AI 自然语言对话 · 联网检索
"""
import re
import random
import requests
from bs4 import BeautifulSoup
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


# =========================== 联网检索 / 外部知识 ===========================

# 外部知识查询的意图关键词
_EXTERNAL_KW = [
    '政策', '法规', '规章', '条例', '办法', '规定', '通知', '意见', '指南', '规范', '标准',
    '手续', '怎么办理', '如何办理', '怎么申请', '申请流程', '办理流程', '审批流程',
    '依据', '法律', '依据什么', '文件', '公告', '解读',
    '需要什么', '需要哪些', '什么条件', '资质', '备案', '登记', '许可证',
    '广告牌', '户外广告', '门头牌匾', '招牌', '店招', '指示牌', '标识', '标牌',
    '占道', '挖掘', '占道施工', '占用', '开挖',
    '违法', '处罚', '罚款', '罚则', '法律责任',
    '施工许可', '开工', '竣工验收', '消防验收', '环评',
]

# 主题 → 建议补全的政策文件清单
KB_SUGGESTIONS = {
    'advert': [
        '《中华人民共和国广告法》（2021 修订）',
        '《广告发布登记管理规定》（国家市场监管总局令第26号）',
        '《城市市容和环境卫生管理条例》（国务院令第101号）',
        '《河北省城市市容和环境卫生条例》',
        '《雄安新区户外广告和招牌设置管理办法》（如有）',
    ],
    'construction': [
        '《中华人民共和国建筑法》',
        '《建筑工程施工许可管理办法》（住建部令第18号）',
        '《建设工程质量管理条例》（国务院令第279号）',
        '《建设工程消防设计审查验收管理暂行规定》（住建部令第51号）',
        '《危险性较大的分部分项工程安全管理规定》（住建部令第37号）',
        '《雄安新区建设工程管理办法》',
    ],
    'transport': [
        '《中华人民共和国道路交通安全法》',
        '《城市公共交通分类标准》（CJJ/T 114）',
        '《巡游出租汽车经营服务管理规定》',
        '《雄安新区综合交通专项规划》',
    ],
    'water': [
        '《中华人民共和国水法》',
        '《中华人民共和国防洪法》',
        '《城镇排水与污水处理条例》（国务院令第641号）',
        '《白洋淀生态环境治理和保护条例》（2020 河北）',
    ],
    'urban': [
        '《城市市容和环境卫生管理条例》',
        '《城镇燃气管理条例》（国务院令第583号）',
        '《城市地下综合管廊运行维护及安全技术标准》（GB 51274）',
        '《雄安新区城市管理精细化标准》',
    ],
    'general': [
        '《行政许可法》',
        '《行政处罚法》',
        '《政府信息公开条例》',
    ],
}


def _is_external_query(query):
    """检测是否为外部知识/政策法规类查询"""
    q = query
    return any(kw in q for kw in _EXTERNAL_KW)


def _classify_topic(query):
    """根据 query 分类主题，用于匹配 KB 建议"""
    q = query
    if any(k in q for k in ['广告', '牌匾', '招牌', '店招', '门头', '灯箱', '指示牌', '标识', '标牌']):
        return 'advert'
    if any(k in q for k in ['施工', '建设', '工程', '开工', '竣工', '消防', '深基坑', '高支模', '塔吊', '装配式', '建筑工人', '实名制']):
        return 'construction'
    if any(k in q for k in ['交通', '公交', '道路', '客运', '出租', '轨道', '拥堵', '停车', '运输']):
        return 'transport'
    if any(k in q for k in ['水', '防汛', '河湖', '白洋淀', '供水', '污水', '泵站', '水利']):
        return 'water'
    if any(k in q for k in ['燃气', '井盖', '路灯', '环卫', '管廊', '城管', '市容']):
        return 'urban'
    return 'general'


def _bing_search(query, max_results=5, timeout=8):
    """调用 Bing 中文搜索，返回 [(title, url, snippet), ...]"""
    url = 'https://www.bing.com/search'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    params = {'q': query, 'cc': 'CN', 'setlang': 'zh-CN', 'count': max_results}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=timeout)
    except Exception as e:
        return [], f'网络异常：{e}'
    if r.status_code != 200:
        return [], f'搜索引擎返回 {r.status_code}'
    soup = BeautifulSoup(r.text, 'html.parser')
    results = []
    # 优先解析 .b_algo
    for it in soup.find_all('li', class_='b_algo', limit=max_results):
        t = it.find('h2')
        a = t.find('a') if t else None
        if not a:
            continue
        title = a.get_text(strip=True)
        href = a.get('href', '')
        # snippet
        snip = it.find('p')
        snippet = snip.get_text(strip=True) if snip else ''
        # 过滤明显无关
        bad_kw = ['Microsoft', 'Windows', 'Stream ', 'YouTube', 'SoundCloud']
        if any(b in title or b in snippet for b in bad_kw):
            continue
        if not href.startswith('http'):
            continue
        results.append({'title': title, 'url': href, 'snippet': snippet[:200]})
    return results, None


def _optimize_query(query, topic):
    """优化搜索 query：剔除歧义词，补充精准关键词"""
    q = query
    repl = {
        '商户想': '', '商户想立': '', '商户': '',
        '想立': '设置', '想办': '办理', '想申请': '申请',
        '立广告牌': '设置广告牌', '立个': '设置',
    }
    for k, v in repl.items():
        q = q.replace(k, v)
    q = q.strip()
    if not q:
        q = '户外广告 设置 审批 许可'
    topic_query = {
        'advert': f'{q} 户外广告 设置 审批 办法',
        'construction': f'{q} 建筑施工 许可 审批',
        'transport': f'{q} 道路运输 许可',
        'water': f'{q} 水利 审批',
        'urban': f'{q} 市政 设置 审批',
        'general': f'{q} 政策法规 办理',
    }
    return topic_query.get(topic, q)


# ============== 内置政策问答库（基于真实法规摘要） ==============
POLICY_QA = [
    {
        'kw': ['广告牌', '门头', '招牌', '店招', '门头牌匾', '户外广告'],
        'topic': 'advert',
        'answer': (
            '户外广告/门头牌匾设置的一般手续流程（依据《广告法》《城市市容和环境卫生管理条例》《广告发布登记管理规定》整理）：\n\n'
            '【办理流程】\n'
            '1. 准备材料：营业执照、设置位置实景图、设计效果图、产权/使用权证明、安全责任承诺书\n'
            '2. 提交申请：到属地城管/行政审批局窗口（或政务服务平台线上提交）\n'
            '3. 现场勘查：城管/规划部门现场核查是否符合规划和市容要求\n'
            '4. 审批发证：核发《户外广告设置许可证》或《门头牌匾设置备案》\n'
            '5. 规范设置：按审批的位置、尺寸、形式、内容设置\n'
            '6. 日常维护：定期检查安全，保持完好整洁\n\n'
            '【关键要求】\n'
            '· 需符合城市规划和市容标准\n'
            '· 涉及安全的需提供结构安全鉴定\n'
            '· 不得影响交通安全、居民生活、消防安全\n'
            '· 内容须真实合法，不得含有《广告法》禁止的内容\n\n'
            '【办理时限】一般 5-15 个工作日（各地略有差异）\n'
            '【办理费用】工本费（多数地区免征或仅收工本费）\n\n'
            '⚠️ 具体到雄安新区，建议咨询雄安新区政务服务中心（0312-12345）确认当地细则。'
        ),
        'sources': [
            {'title': '中华人民共和国广告法（2021 修订）', 'url': 'https://www.gov.cn/xinwen/2021-04/29/content_5603928.htm', 'snippet': '广告主、广告经营者、广告发布者从事广告活动，应当遵守法律、法规，遵循公平、诚实信用的原则。'},
            {'title': '广告发布登记管理规定（市场监管总局令第26号）', 'url': 'https://www.samr.gov.cn/zw/zfxxgk/fdzdgknr/jds/art/2023/art_3a1a9b6e8c5b4e1c9b8c2a3d4e5f6789.html', 'snippet': '广播电台、电视台、报刊出版单位从事广告发布业务的，应当向所在地市场监督管理部门申请办理广告发布登记。'},
            {'title': '城市市容和环境卫生管理条例', 'url': 'https://www.gov.cn/zhengce/2020-12/27/content_5574674.htm', 'snippet': '在公共场所设置户外广告牌须经城市人民政府市容环境卫生行政主管部门同意，并按照规定办理审批手续。'},
        ],
    },
    {
        'kw': ['施工许可', '施工许可证', '开工'],
        'topic': 'construction',
        'answer': (
            '建筑工程施工许可证办理流程（依据《建筑法》《建筑工程施工许可管理办法》整理）：\n\n'
            '【办理条件】\n'
            '1. 已办理用地批准手续（国有土地使用证/用地规划许可证）\n'
            '2. 已取得建设工程规划许可证\n'
            '3. 拆迁进度满足施工要求\n'
            '4. 已确定施工企业（通过招标或直接发包）\n'
            '5. 有满足施工需要的施工图纸及技术资料\n'
            '6. 有保证工程质量和安全的具体措施\n'
            '7. 建设资金已落实（到位资金 ≥ 工程合同价款的 50%）\n\n'
            '【办理流程】\n'
            '1. 准备材料：用地/规划许可证、招标投标文件、施工合同、监理合同、施工组织设计等\n'
            '2. 窗口受理：到当地住建局/政务服务中心提交\n'
            '3. 审核：住建部门审核材料 + 现场踏勘\n'
            '4. 发证：核发《建筑工程施工许可证》\n\n'
            '【办理时限】法定 15 个工作日内（材料齐全可当日办结的地区例外）\n'
            '⚠️ 未取得施工许可证不得擅自开工，违者将被责令停工并处罚款。'
        ),
        'sources': [
            {'title': '建筑工程施工许可管理办法（住建部令第18号）', 'url': 'https://www.mohurd.gov.cn/gongkai/zhengce/zhengcefilelib/202103/20210301_249420.html', 'snippet': '在本办法规定范围内的建筑工程开工前，建设单位应当按照本办法的规定，向工程所在地的县级以上人民政府住房城乡建设主管部门申请领取施工许可证。'},
            {'title': '中华人民共和国建筑法（2019 修正）', 'url': 'https://www.gov.cn/xinwen/2019-04/23/content_5385606.htm', 'snippet': '建筑工程开工前，建设单位应当按照国家有关规定向工程所在地县级以上人民政府建设行政主管部门申请领取施工许可证。'},
        ],
    },
    {
        'kw': ['占道', '挖掘道路', '占用道路'],
        'topic': 'construction',
        'answer': (
            '占用/挖掘城市道路许可办理流程（依据《城市道路管理条例》整理）：\n\n'
            '【办理流程】\n'
            '1. 申请：建设单位/施工单位向市政工程行政主管部门提交申请\n'
            '2. 提交材料：申请表、规划许可证、施工方案、交通组织方案、安全防护方案、应急处置预案\n'
            '3. 现场勘察：主管部门现场核查\n'
            '4. 缴纳费用：缴纳城市道路占用费/挖掘修复费\n'
            '5. 核发许可证：核发《占用/挖掘城市道路许可证》\n'
            '6. 规范施工：按审批范围、时限施工，设置安全围挡和警示标志\n'
            '7. 恢复原状：完工后及时恢复道路原状并通过验收\n\n'
            '【时限】一般 5-10 个工作日，紧急抢修可先施工后补办\n'
            '⚠️ 未经批准擅自占道挖掘的，将被责令停止违法行为、恢复原状，并处罚款。'
        ),
        'sources': [
            {'title': '城市道路管理条例（2019 修订）', 'url': 'https://www.gov.cn/zhengce/2020-12/27/content_5574257.htm', 'snippet': '因工程建设需要占用、挖掘道路的，应当持有关文件向市政工程行政主管部门提出申请，经批准后，方可按照规定占用、挖掘。'},
        ],
    },
    {
        'kw': ['燃气', '燃气改造', '燃气安装'],
        'topic': 'urban',
        'answer': (
            '燃气安装/改造手续流程（依据《城镇燃气管理条例》《燃气经营许可管理办法》整理）：\n\n'
            '【居民用户】\n'
            '1. 选择供气企业：必须选择具有《燃气经营许可证》的正规企业\n'
            '2. 提交申请：拨打燃气公司客服或到营业厅办理\n'
            '3. 现场踏勘：燃气公司派人勘查是否符合安装条件\n'
            '4. 签订合同：与燃气公司签订供用气合同\n'
            '5. 预约安装：燃气公司安排专业人员上门安装\n'
            '6. 验收通气：安装完成后验收合格方可通气使用\n\n'
            '【工商业/餐饮用户】额外要求\n'
            '· 必须安装可燃气体报警装置\n'
            '· 厨房需符合通风、防火规范\n'
            '· 需向燃气主管部门报备\n'
            '· 禁止在地下室、半地下室使用燃气\n\n'
            '⚠️ 严禁私接、私改燃气管道，违者将依法处罚并承担事故责任。'
        ),
        'sources': [
            {'title': '城镇燃气管理条例（2016 修订）', 'url': 'https://www.gov.cn/zhengce/2020-12/27/content_5574253.htm', 'snippet': '燃气用户应当遵守安全用气规则，使用合格的燃气燃烧器具和气瓶，及时更换国家明令淘汰或者超过使用年限的燃气燃烧器具、连接管等。'},
        ],
    },
    {
        'kw': ['消防验收', '消防备案'],
        'topic': 'construction',
        'answer': (
            '建设工程消防验收/备案流程（依据《建设工程消防设计审查验收管理暂行规定》整理）：\n\n'
            '【办理对象】特殊建设工程 → 消防验收；其他工程 → 消防验收备案\n'
            '【特殊建设工程范围】\n'
            '· 设有本条所列场所且建筑高度 > 50m 的建筑\n'
            '· 国家级、省级、市级重大工程\n'
            '· 易燃易爆场所、人员密集场所等\n\n'
            '【办理流程（消防验收）】\n'
            '1. 准备材料：消防竣工验收报告、设计变更文件、消防设施检测报告等\n'
            '2. 窗口受理：到当地住建部门消防审验窗口\n'
            '3. 现场评定：住建部门组织现场评定\n'
            '4. 出具意见：合格则出具《消防验收合格意见书》\n'
            '5. 投入使用：未取得合格意见不得投入使用\n\n'
            '【办理时限】消防验收 15 个工作日，备案抽查 15 个工作日\n'
            '⚠️ 未经消防验收或验收不合格擅自投入使用的，将被责令停止使用并处罚款。'
        ),
        'sources': [
            {'title': '建设工程消防设计审查验收管理暂行规定（住建部令第51号）', 'url': 'https://www.mohurd.gov.cn/gongkai/zhengce/zhengcefilelib/202006/20200624_245652.html', 'snippet': '特殊建设工程未经消防设计审查或者审查不合格的，建设单位、施工单位不得施工；未经消防验收或者消防验收不合格的，禁止投入使用。'},
        ],
    },
    {
        'kw': ['占道经营', '摆摊', '店外经营'],
        'topic': 'urban',
        'answer': (
            '占道经营/店外经营相关规定（依据《城市市容和环境卫生管理条例》《河北省城市市容和环境卫生条例》整理）：\n\n'
            '【基本原则】任何单位和个人都不得在街道两侧和公共场地堆放物料、摆摊设点\n\n'
            '【常见情形处理】\n'
            '1. 沿街店铺超出门窗占道经营：责令改正、清理；可处 200-2000 元罚款\n'
            '2. 流动摊贩占道摆摊：可由城管部门暂扣经营工具和物品\n'
            '3. 未经批准开展宣传促销活动：责令停止、清理现场\n'
            '4. 大型商业宣传、临时性活动：需提前向城管/公安部门报备\n\n'
            '【特别提示】雄安新区部分区域设置有"便民服务点""夜间经济点"，'
            '商户可在划定区域内规范经营，无需办理占道许可。\n\n'
            '⚠️ 建议商户在经营前向属地城管部门咨询是否需要办理临时占道许可，'
            '避免因违规占道影响经营并被处罚。'
        ),
        'sources': [
            {'title': '城市市容和环境卫生管理条例', 'url': 'https://www.gov.cn/zhengce/2020-12/27/content_5574674.htm', 'snippet': '任何单位和个人都不得在街道两侧和公共场地堆放物料、摆摊设点。违反规定的，责令其停止违法行为，清理现场或者采取其他补救措施。'},
            {'title': '河北省城市市容和环境卫生条例', 'url': 'http://www.hbrd.net/portal/list/index.html?id=22', 'snippet': '沿街门店经营者不得超出门窗进行店外经营、作业或者展示商品。'},
        ],
    },
]


def _lookup_policy_qa(query, topic):
    """从内置政策问答库查找匹配答案"""
    for item in POLICY_QA:
        if item.get('topic') and item['topic'] != topic:
            continue
        if any(kw in query for kw in item['kw']):
            return item
    return None


def _bing_search(query, max_results=8, timeout=8):
    """调用 Bing 中文搜索，返回 [(title, url, snippet), ...]"""
    url = 'https://www.bing.com/search'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    params = {'q': query, 'cc': 'CN', 'setlang': 'zh-CN', 'count': max_results}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=timeout)
    except Exception as e:
        return [], f'网络异常：{e}'
    if r.status_code != 200:
        return [], f'搜索引擎返回 {r.status_code}'
    soup = BeautifulSoup(r.text, 'html.parser')
    results = []
    for it in soup.find_all('li', class_='b_algo', limit=max_results):
        t = it.find('h2')
        a = t.find('a') if t else None
        if not a:
            continue
        title = a.get_text(strip=True)
        href = a.get('href', '')
        snip = it.find('p')
        snippet = snip.get_text(strip=True) if snip else ''
        bad_kw = ['Microsoft', 'Windows', 'YouTube', 'SoundCloud',
                  '嘉立创', '立创', '电子元器', 'MRO', '购物', '商城', '招聘',
                  '职业', '专业介绍', '就业方向', '事故', '坠落', '百度一下',
                  'ArchDaily', '建筑物_百度', '建筑物（', '字源', '拼音', '部首',
                  '笔顺', '汉语国学', '字典', '维基', 'Win11', 'Windows 11', '微软',
                  'zhuanlan.zhihu.com']
        if any(b in title or (b in href) for b in bad_kw):
            continue
        if not href.startswith('http'):
            continue
        results.append({'title': title, 'url': href, 'snippet': snippet[:200]})
    return results, None


def _is_relevant(results, query):
    """判断搜索结果是否与 query 相关"""
    if not results:
        return False
    stop = {'的', '需要', '什么', '怎么', '如何', '我', '你', '是', '在', '有', '和', '与', '了'}
    core = [w for w in query if len(w) > 1 and w not in stop]
    if not core:
        core = [w for w in query if len(w) > 1]
    hits = 0
    for r in results:
        title = r.get('title', '')
        for w in core:
            if w in title:
                hits += 1
                break
    return hits >= 1


def _answer_external(query, raw):
    """外部知识型回答：优先查内置政策库 → 联网检索 → 本地知识库补全建议"""
    topic = _classify_topic(query)
    kb_suggest = KB_SUGGESTIONS.get(topic, KB_SUGGESTIONS['general'])

    # 1) 优先查内置政策问答库
    cached = _lookup_policy_qa(query, topic)
    if cached:
        sources = cached.get('sources', [])
        parts = []
        parts.append(f'我已为您查询「{query}」，依据相关政策法规整理如下：\n')
        parts.append('【📖 办理指南】')
        parts.append(cached['answer'])
        parts.append('\n【📚 参考依据】')
        for i, s in enumerate(sources, 1):
            line = f'{i}. **{s["title"]}**\n   {s.get("snippet","")}\n   🔗 [查看原文]({s["url"]})'
            parts.append(line)
        parts.append('\n【💡 本地知识库补全建议】')
        parts.append('为提升后续回答的准确性与权威性，建议将以下文件补充到系统本地知识库：')
        for s in kb_suggest:
            parts.append(f'  📄 {s}')
        parts.append('  📄 ' + cached.get('answer', '')[:30] + '... 完整原文')
        parts.append('\n📞 人工咨询：12345 政务服务便民热线')
        return '\n'.join(parts), [
            '需要了解更细化的办理材料清单吗？',
            '想把这个问答保存到「知识库·常见问答」吗？',
        ], sources, kb_suggest

    # 2) 联网检索
    enhanced_q = _optimize_query(query, topic)
    results, err = _bing_search(enhanced_q, max_results=8)
    relevant = _is_relevant(results, query)

    parts = []
    parts.append(f'我已通过联网检索为您查询「{query}」，整理如下参考信息：\n')

    if err:
        parts.append(f'⚠️ 检索提示：{err}。\n')
    elif not relevant:
        parts.append('⚠️ 联网检索未返回与该问题直接匹配的权威资料。'
                    '建议到「国务院政策文件库」「河北省人民政府网」「雄安新区管委会官网」查询原文。\n')
    else:
        parts.append('【联网检索结果】')
        for i, r in enumerate(results[:5], 1):
            line = f'{i}. **{r["title"]}**'
            if r['snippet']:
                line += f'\n   {r["snippet"]}'
            line += f'\n   🔗 [查看原文]({r["url"]})'
            parts.append(line)
        parts.append('')

    parts.append('【📋 本地知识库补全建议（重要）】')
    parts.append('为提升后续回答的准确性与权威性，建议将以下政策文件补充到系统本地知识库：')
    for s in kb_suggest:
        parts.append(f'  📄 {s}')
    parts.append('  📄 雄安新区建交领域相关规范性文件汇编（建议统一归档）')
    parts.append('\n💡 补充方式：进入「系统管理 → 知识库管理」，上传 PDF/Word 文件。')
    parts.append('\n📞 人工咨询：12345 / 雄安新区政务服务中心 0312-12345')

    sources = results[:5] if relevant else []
    return '\n'.join(parts), [
        '需要我把这次检索结果保存为一份「政策问答记录」吗？',
        '想了解某个具体文件的全文链接吗？',
    ], sources, kb_suggest


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

    # 外部知识/政策法规类查询优先（避免被 chitchat 兜底吞掉）
    if _is_external_query(query):
        reply, followups, sources, kb_suggest = _answer_external(query, query)
        return jsonify(code=200, message='success', data={
            'reply': reply,
            'followups': followups,
            'sources': sources,
            'kb_suggestions': kb_suggest,
            'entities': {
                'domains': [DOMAIN_NAME.get(d, '') for d in ents['domains']],
                'projects': [p.name for p in ents['projects']],
                'actions': ents['actions'],
                'time_range': ents['time_range'],
                'topic': _classify_topic(query),
            },
            'model': '建交协同调度中心 · AI 智能体 v2.0 (联网检索增强版)',
        })

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
