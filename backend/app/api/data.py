# -*- coding: utf-8 -*-
"""
建交数据中枢 API（Step 3）

数据资源目录 + 通用数据查询 + 标准指标 + 数据中枢概览
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, current_user
from app import db
from app.data_models import DataResource, Indicator, IndicatorData
from app.data_models import ProjectInfo, BusinessLicense, TransportStation, WaterBody, MunicipalNode

data_bp = Blueprint('data', __name__)

# 资源编码 → 物理表Model映射
TABLE_MAP = {
    'proj_list': ProjectInfo,
    'biz_list': BusinessLicense,
    'bus_station': TransportStation,
    'water_list': WaterBody,
    'muni_list': MunicipalNode,
}


def admin_only():
    """只有系统管理员才能维护数据中枢"""
    for role in current_user.roles:
        if role.role_code == 'ADMIN':
            return True
    return False


# =========================== 数据资源目录 ===========================

@data_bp.route('/data-resources', methods=['GET'])
@jwt_required()
def list_resources():
    domain = request.args.get('domain', type=int)  # 可选领域筛选
    q = DataResource.query
    if domain:
        q = q.filter_by(domain=domain)
    items = q.order_by(DataResource.domain, DataResource.id).all()
    return jsonify(code=200, message='success', data=[r.to_dict() for r in items])


@data_bp.route('/data-resources', methods=['POST'])
@jwt_required()
def add_resource():
    if not admin_only():
        return jsonify(code=403, message='仅系统管理员可操作'), 403
    d = request.get_json(silent=True) or {}
    r = DataResource(
        code=d.get('code', ''), name=d.get('name', ''),
        domain=d.get('domain', 1), source_system=d.get('source_system', ''),
        table_name=d.get('table_name', ''),
        data_type=d.get('data_type', '基础数据'),
        update_freq=d.get('update_freq', '每日'),
        owner_dept=d.get('owner_dept', ''), owner_person=d.get('owner_person', ''),
        quality_status=d.get('quality_status', '良好'),
        description=d.get('description', ''), fields_schema=d.get('fields_schema', '[]'),
        record_count=d.get('record_count', 0),
    )
    db.session.add(r)
    db.session.commit()
    return jsonify(code=200, message='新增成功', data=r.to_dict())


@data_bp.route('/data-resources/<int:rid>', methods=['PUT'])
@jwt_required()
def update_resource(rid):
    if not admin_only():
        return jsonify(code=403, message='仅系统管理员可操作'), 403
    r = DataResource.query.get_or_404(rid)
    d = request.get_json(silent=True) or {}
    for f in ['name', 'description', 'update_freq', 'data_type', 'owner_dept', 'owner_person',
              'quality_status', 'fields_schema', 'record_count']:
        if f in d:
            setattr(r, f, d[f])
    db.session.commit()
    return jsonify(code=200, message='更新成功', data=r.to_dict())


@data_bp.route('/data-resources/<int:rid>', methods=['DELETE'])
@jwt_required()
def delete_resource(rid):
    if not admin_only():
        return jsonify(code=403, message='仅系统管理员可操作'), 403
    r = DataResource.query.get_or_404(rid)
    db.session.delete(r)
    db.session.commit()
    return jsonify(code=200, message='删除成功')


# =========================== 通用数据查询 ===========================

@data_bp.route('/data/<code>', methods=['GET'])
@jwt_required()
def query_data(code):
    """根据资源编码查询对应主题库数据"""
    resource = DataResource.query.filter_by(code=code).first()
    if not resource:
        return jsonify(code=404, message=f'资源 {code} 不存在'), 404

    model = TABLE_MAP.get(code)
    if not model:
        return jsonify(code=200, message='success', data={
            'resource': resource.to_dict(), 'list': [], 'total': 0,
            'hint': '该资源为指标或统计数据，请通过 /api/indicators 查询',
        })

    q = model.query
    keyword = request.args.get('keyword', '').strip()
    area = request.args.get('area', '').strip()

    # 通用搜索（对 name 字段模糊匹配）
    if keyword and hasattr(model, 'name'):
        q = q.filter(model.name.like(f'%{keyword}%'))
    if area and hasattr(model, 'area'):
        q = q.filter_by(area=area)

    total = q.count()
    items = q.limit(200).all()
    return jsonify(code=200, message='success', data={
        'resource': resource.to_dict(),
        'list': [m.to_dict() for m in items],
        'total': total,
    })


# =========================== 标准指标 ===========================

@data_bp.route('/indicators', methods=['GET'])
@jwt_required()
def list_indicators():
    domain = request.args.get('domain', type=int)
    q = Indicator.query
    if domain:
        q = q.filter_by(domain=domain)
    items = q.order_by(Indicator.domain, Indicator.sort).all()
    return jsonify(code=200, message='success', data=[i.to_dict() for i in items])


@data_bp.route('/indicators/<code>/data', methods=['GET'])
@jwt_required()
def indicator_data(code):
    ind = Indicator.query.filter_by(code=code).first()
    if not ind:
        return jsonify(code=404, message=f'指标 {code} 不存在'), 404

    # 最近12个月数据
    rows = IndicatorData.query.filter_by(indicator_code=code).order_by(
        IndicatorData.period.desc()).limit(12).all()
    data = [r.to_dict() for r in rows]

    # 最新值
    latest = data[0] if data else None
    return jsonify(code=200, message='success', data={
        'indicator': ind.to_dict(),
        'latest': latest,
        'trend': list(reversed(data)),
    })


# =========================== 数据中枢概览 ===========================

@data_bp.route('/data-overview', methods=['GET'])
@jwt_required()
def data_overview():
    """数据中枢首页概览统计"""
    # 资源数（按领域）
    domain_count = {1: 0, 2: 0, 3: 0, 4: 0}
    for r in DataResource.query.all():
        if r.domain in domain_count:
            domain_count[r.domain] += 1

    # 指标数（按领域）
    ind_count = {1: 0, 2: 0, 3: 0, 4: 0}
    for ind in Indicator.query.all():
        if ind.domain in ind_count:
            ind_count[ind.domain] += 1

    # 主题库记录数（代表性快照）
    record_snap = {
        'project': ProjectInfo.query.count(),
        'business': BusinessLicense.query.count(),
        'bus_station': TransportStation.query.count(),
        'water': WaterBody.query.count(),
        'municipal': MunicipalNode.query.count(),
    }

    return jsonify(code=200, message='success', data={
        'resource_count': DataResource.query.count(),
        'indicator_count': Indicator.query.count(),
        'domain_resources': [
            {'domain': 1, 'name': '城乡建设', 'resources': domain_count.get(1, 0), 'indicators': ind_count.get(1, 0)},
            {'domain': 2, 'name': '交通运输', 'resources': domain_count.get(2, 0), 'indicators': ind_count.get(2, 0)},
            {'domain': 3, 'name': '水利水务', 'resources': domain_count.get(3, 0), 'indicators': ind_count.get(3, 0)},
            {'domain': 4, 'name': '城市管理', 'resources': domain_count.get(4, 0), 'indicators': ind_count.get(4, 0)},
        ],
        'record_snapshot': record_snap,
        'total_records': sum(record_snap.values()),
    })


# =========================== 数据源状态 ===========================

@data_bp.route('/data-sources', methods=['GET'])
@jwt_required()
def data_sources():
    """数据源配置状态（Mock）"""
    from datetime import datetime
    sources = [
        {'name': '规建管平台', 'system': '规建管一体化平台', 'status': 1, 'status_label': '运行中',
         'last_sync': '2026-07-06 08:30', 'records': ProjectInfo.query.count()},
        {'name': '建筑市场系统', 'system': '建筑市场监管平台', 'status': 1, 'status_label': '运行中',
         'last_sync': '2026-07-06 08:00', 'records': BusinessLicense.query.count()},
        {'name': '交通运行监测', 'system': '交通运输监测平台', 'status': 1, 'status_label': '运行中',
         'last_sync': '2026-07-06 08:15', 'records': TransportStation.query.count()},
        {'name': '水文监测系统', 'system': '水利水务监测平台', 'status': 1, 'status_label': '运行中',
         'last_sync': '2026-07-06 07:45', 'records': WaterBody.query.count()},
        {'name': '城市管理平台', 'system': '城管综合平台', 'status': 1, 'status_label': '运行中',
         'last_sync': '2026-07-06 08:10', 'records': MunicipalNode.query.count()},
    ]
    return jsonify(code=200, message='success', data=sources)


# =========================== 数据治理概览 ===========================

@data_bp.route('/data-governance', methods=['GET'])
@jwt_required()
def data_governance():
    """数据治理全貌 - 一个数据一个源头"""
    resources = DataResource.query.all()
    indicators = Indicator.query.all()

    # 按数据类型统计资源
    type_count = {}
    for r in resources:
        dt = r.data_type or '未分类'
        type_count[dt] = type_count.get(dt, 0) + 1

    # 按责任处室统计（资源+指标合并）
    dept_res = {}
    for r in resources:
        if r.owner_dept:
            for dept in r.owner_dept.split(','):
                dept = dept.strip()
                if dept not in dept_res:
                    dept_res[dept] = {'resources': 0, 'indicators': 0}
                dept_res[dept]['resources'] += 1
    for ind in indicators:
        if ind.owner_dept:
            for dept in ind.owner_dept.split(','):
                dept = dept.strip()
                if dept not in dept_res:
                    dept_res[dept] = {'resources': 0, 'indicators': 0}
                dept_res[dept]['indicators'] += 1

    # 按质量状态统计
    quality_count = {}
    for r in resources:
        qs = r.quality_status or '未评估'
        quality_count[qs] = quality_count.get(qs, 0) + 1

    # 按更新频率统计
    freq_count = {}
    for r in resources:
        fq = r.update_freq or '未设定'
        freq_count[fq] = freq_count.get(fq, 0) + 1

    # 治理覆盖率
    total_res = len(resources)
    with_owner = sum(1 for r in resources if r.owner_dept)
    with_person = sum(1 for r in resources if r.owner_person)
    total_ind = len(indicators)
    ind_with_owner = sum(1 for i in indicators if i.owner_dept)

    # 源头去重列表
    source_set = sorted(set(r.source_system for r in resources if r.source_system))

    return jsonify(code=200, message='success', data={
        'resource_count': total_res,
        'indicator_count': total_ind,
        'total_items': total_res + total_ind,
        'type_distribution': [{'type': k, 'count': v} for k, v in sorted(type_count.items())],
        'dept_ownership': [{'dept': k, **v} for k, v in sorted(dept_res.items())],
        'quality_distribution': [{'status': k, 'count': v} for k, v in sorted(quality_count.items())],
        'freq_distribution': [{'freq': k, 'count': v} for k, v in sorted(freq_count.items())],
        'coverage': {
            'resource_owner_pct': round(with_owner / total_res * 100, 1) if total_res else 0,
            'resource_person_pct': round(with_person / total_res * 100, 1) if total_res else 0,
            'indicator_owner_pct': round(ind_with_owner / total_ind * 100, 1) if total_ind else 0,
            'overall_pct': round((with_owner + ind_with_owner) / (total_res + total_ind) * 100, 1) if (total_res + total_ind) else 0,
        },
        'source_systems': [{'system': s, 'item_count': sum(1 for r in resources if r.source_system == s)} for s in source_set],
    })
