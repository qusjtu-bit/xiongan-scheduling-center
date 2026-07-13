# -*- coding: utf-8 -*-
"""
规建管一体化 API（Step 5）

项目列表/详情、阶段时间轴、审批记录、进度预警、统计分析
"""
from datetime import date

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import ProjectInfo, ProjectStage, ApprovalRecord

project_bp = Blueprint('project', __name__)

STAGE_ORDER = ['立项', '规划', '审批', '建设', '验收', '运维']


def _today():
    return date.today().isoformat()


def _parse_date(s):
    """容忍 YYYY-MM 格式，补全为 YYYY-MM-DD"""
    if not s:
        return None
    if len(s) == 7:  # YYYY-MM
        s = s + '-01'
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None


# =========================== 项目列表 ===========================

@project_bp.route('/projects', methods=['GET'])
@jwt_required()
def list_projects():
    q = ProjectInfo.query

    # 筛选条件
    keyword = request.args.get('keyword', '').strip()
    ptype = request.args.get('ptype', '').strip()
    area = request.args.get('area', '').strip()
    stage = request.args.get('stage', '').strip()
    alert = request.args.get('alert', '').strip()  # overdue / near_due

    if keyword:
        q = q.filter(ProjectInfo.name.like(f'%{keyword}%'))
    if ptype:
        q = q.filter_by(ptype=ptype)
    if area:
        q = q.filter_by(area=area)
    if stage:
        q = q.filter_by(stage=stage)

    # 预警筛选：逾期或即将到期
    today = _today()
    today_date = date.today()
    if alert == 'overdue':
        # Filter in Python for date-tolerant comparison
        q = q.filter(ProjectInfo.progress < 100)
    elif alert == 'near_due':
        q = q.filter(ProjectInfo.progress < 80)

    items = q.order_by(ProjectInfo.id).all()

    # 判断是否逾期/临近
    result = []
    for p in items:
        d = p.to_dict()
        plan_end = _parse_date(p.plan_end_date)
        d['is_overdue'] = (plan_end is not None and plan_end < today_date and p.progress < 100)
        d['stage_order'] = STAGE_ORDER.index(p.stage) if p.stage in STAGE_ORDER else -1
        # 进度风险
        if p.progress >= 100:
            d['risk'] = 'none'
        elif d['is_overdue']:
            d['risk'] = 'overdue'
        elif plan_end and plan_end <= date(2026, 9, 1) and p.progress < 80:
            d['risk'] = 'near'
        else:
            d['risk'] = 'normal'
        result.append(d)

    return jsonify(code=200, message='success', data={
        'total': len(result),
        'list': result,
    })


# =========================== 项目详情 ===========================

@project_bp.route('/projects/<int:pid>', methods=['GET'])
@jwt_required()
def project_detail(pid):
    p = ProjectInfo.query.get_or_404(pid)

    # 阶段时间轴
    stages = ProjectStage.query.filter_by(project_id=pid).order_by(
        ProjectStage.stage_order).all()

    # 审批记录
    approvals = ApprovalRecord.query.filter_by(project_id=pid).order_by(
        ApprovalRecord.id.desc()).all()

    # 判断预警
    plan_end = _parse_date(p.plan_end_date)
    today_date = date.today()
    overdue = plan_end is not None and plan_end < today_date and p.progress < 100
    risk = 'overdue' if overdue else ('near' if plan_end and plan_end <= date(2026, 9, 1) and p.progress < 80 else 'normal')

    return jsonify(code=200, message='success', data={
        'project': p.to_dict(),
        'stages': [s.to_dict() for s in stages],
        'approvals': [a.to_dict() for a in approvals],
        'risk': risk,
        'is_overdue': overdue,
    })


# =========================== 项目统计 ===========================

@project_bp.route('/projects/stats', methods=['GET'])
@jwt_required()
def project_stats():
    items = ProjectInfo.query.all()
    today_date = date.today()
    sep_first = date(2026, 9, 1)

    # 按阶段统计
    stage_count = {}
    for s in STAGE_ORDER:
        stage_count[s] = 0
    for p in items:
        if p.stage in stage_count:
            stage_count[p.stage] += 1

    # 按类型统计
    type_count = {}
    for p in items:
        t = p.ptype or '其他'
        type_count[t] = type_count.get(t, 0) + 1

    # 按片区统计
    area_count = {}
    for p in items:
        a = p.area or '其他'
        area_count[a] = area_count.get(a, 0) + 1

    # 投资总额
    total_invest = sum(p.invest for p in items)

    # 进度预警
    overdue = 0
    near_due = 0
    for p in items:
        plan = _parse_date(p.plan_end_date)
        if plan and plan < today_date and p.progress < 100:
            overdue += 1
        elif plan and today_date <= plan <= sep_first and p.progress < 80:
            near_due += 1
    normal = len(items) - overdue - near_due

    return jsonify(code=200, message='success', data={
        'total': len(items),
        'total_invest': total_invest,
        'stage_count': stage_count,
        'type_count': type_count,
        'area_count': area_count,
        'risk_summary': {
            'overdue': overdue,
            'near_due': near_due,
            'normal': normal,
        },
    })


# =========================== 预警列表 ===========================

@project_bp.route('/projects/alerts', methods=['GET'])
@jwt_required()
def project_alerts():
    items = ProjectInfo.query.all()
    today_date = date.today()
    sep_first = date(2026, 9, 1)
    alerts = []

    for p in items:
        plan_end = _parse_date(p.plan_end_date)
        if not plan_end:
            continue
        if plan_end < today_date and p.progress < 100:
            days = (today_date - plan_end).days
            alerts.append({
                'project_id': p.id,
                'project_name': p.name,
                'alert_type': 'overdue',
                'alert_label': '逾期',
                'days': days,
                'plan_end': p.plan_end_date,
                'progress': p.progress,
                'stage': p.stage,
            })
        elif today_date <= plan_end <= sep_first and p.progress < 80:
            alerts.append({
                'project_id': p.id,
                'project_name': p.name,
                'alert_type': 'near_due',
                'alert_label': '临近',
                'plan_end': p.plan_end_date,
                'progress': p.progress,
                'stage': p.stage,
                'days': None,
            })

    # 逾期排最前
    alerts.sort(key=lambda x: (0 if x['alert_type'] == 'overdue' else 1, x.get('plan_end', '')))

    return jsonify(code=200, message='success', data={
        'total': len(alerts),
        'list': alerts,
    })


# =========================== 待审批列表 ===========================

@project_bp.route('/projects/pending-approvals', methods=['GET'])
@jwt_required()
def pending_approvals():
    items = ApprovalRecord.query.filter_by(status='待审批').order_by(
        ApprovalRecord.apply_date.asc()).all()
    result = []
    for a in items:
        p = ProjectInfo.query.get(a.project_id)
        d = a.to_dict()
        d['project_name'] = p.name if p else ''
        result.append(d)
    return jsonify(code=200, message='success', data={'total': len(result), 'list': result})
