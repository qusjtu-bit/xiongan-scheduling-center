# -*- coding: utf-8 -*-
"""
建交数据中枢模型（Step 3）

数据资源目录、标准指标、指标数据、四大主题库代表性实体
"""
from datetime import datetime
from app import db


# ========== 数据资源目录 ==========
class DataResource(db.Model):
    __tablename__ = 'dc_resource'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(64), unique=True, nullable=False, comment='资源编码')
    name = db.Column(db.String(128), nullable=False, comment='资源名称')
    domain = db.Column(db.SmallInteger, default=1, comment='领域：1城乡建设 2交通运输 3水利水务 4城市管理 5综合')
    source_system = db.Column(db.String(64), comment='来源系统（唯一数据源头）')
    table_name = db.Column(db.String(64), comment='物理表/接口名')
    data_type = db.Column(db.String(32), default='基础数据', comment='数据类型：基础数据/业务数据/指标数据/实时监测/文件档案')
    update_freq = db.Column(db.String(32), default='每日', comment='更新频率：实时/每小时/每日/每周/每月/每季度/每年')
    owner_dept = db.Column(db.String(128), default='', comment='归属更新责任处室（唯一源头处室）')
    owner_person = db.Column(db.String(64), default='', comment='责任人')
    quality_status = db.Column(db.String(16), default='良好', comment='数据质量状态：良好/一般/待改善')
    description = db.Column(db.Text, comment='资源描述')
    fields_schema = db.Column(db.Text, default='[]', comment='字段定义 JSON')
    record_count = db.Column(db.Integer, default=0, comment='记录数量')
    status = db.Column(db.SmallInteger, default=0)

    def to_dict(self):
        return {
            'id': self.id, 'code': self.code, 'name': self.name,
            'domain': self.domain,
            'domain_name': {1: '城乡建设', 2: '交通运输', 3: '水利水务', 4: '城市管理', 5: '综合'}.get(self.domain, '综合'),
            'source_system': self.source_system, 'table_name': self.table_name,
            'data_type': self.data_type, 'update_freq': self.update_freq,
            'owner_dept': self.owner_dept, 'owner_person': self.owner_person,
            'quality_status': self.quality_status,
            'description': self.description,
            'fields_schema': self.fields_schema, 'record_count': self.record_count,
            'status': self.status,
        }


# ========== 标准指标定义 ==========
class Indicator(db.Model):
    __tablename__ = 'dc_indicator'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(64), unique=True, nullable=False, comment='指标编码')
    name = db.Column(db.String(128), nullable=False, comment='指标名称')
    domain = db.Column(db.SmallInteger, default=1, comment='领域')
    unit = db.Column(db.String(16), default='', comment='单位')
    definition = db.Column(db.Text, comment='指标定义')
    calc_expr = db.Column(db.Text, comment='计算口径')
    source_system = db.Column(db.String(64), default='', comment='指标数据源头系统')
    owner_dept = db.Column(db.String(128), default='', comment='归属更新责任处室')
    owner_person = db.Column(db.String(64), default='', comment='责任人')
    update_freq = db.Column(db.String(32), default='每月', comment='更新频率')
    sort = db.Column(db.Integer, default=0)
    status = db.Column(db.SmallInteger, default=0)

    def to_dict(self):
        return {
            'id': self.id, 'code': self.code, 'name': self.name,
            'domain': self.domain,
            'domain_name': {1: '城乡建设', 2: '交通运输', 3: '水利水务', 4: '城市管理', 5: '综合'}.get(self.domain, '综合'),
            'unit': self.unit, 'definition': self.definition, 'calc_expr': self.calc_expr,
            'source_system': self.source_system, 'owner_dept': self.owner_dept,
            'owner_person': self.owner_person, 'update_freq': self.update_freq,
            'sort': self.sort, 'status': self.status,
        }


# ========== 指标数据 ==========
class IndicatorData(db.Model):
    __tablename__ = 'dc_indicator_data'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    indicator_code = db.Column(db.String(64), nullable=False, comment='指标编码')
    period = db.Column(db.String(16), comment='周期 YYYY-MM')
    value = db.Column(db.Float, default=0, comment='数值')
    update_time = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'indicator_code': self.indicator_code, 'period': self.period,
            'value': self.value,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M') if self.update_time else None,
        }


# ===== 四大主题库代表性实体（为 Step 4/5/6 铺垫）=====

class ProjectInfo(db.Model):
    """城建项目"""
    __tablename__ = 'dc_project'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    ptype = db.Column(db.String(32), comment='类型：房建/市政/交通/水利/园林')
    area = db.Column(db.String(32), comment='片区')
    build_unit = db.Column(db.String(128), comment='建设单位')
    contractor = db.Column(db.String(128), comment='施工单位')
    supervisor = db.Column(db.String(128), comment='监理单位')
    invest = db.Column(db.Float, default=0, comment='投资额万元')
    scale = db.Column(db.Float, default=0, comment='建设规模')
    scale_unit = db.Column(db.String(16), default='m²', comment='规模单位')
    stage = db.Column(db.String(16), default='建设', comment='当前阶段')
    progress = db.Column(db.Integer, default=0, comment='进度0-100')
    start_date = db.Column(db.String(16), comment='开工日期')
    plan_end_date = db.Column(db.String(16), comment='计划竣工')
    actual_end_date = db.Column(db.String(16), comment='实际竣工')
    status = db.Column(db.SmallInteger, default=0)
    lng = db.Column(db.Float, default=116.10)
    lat = db.Column(db.Float, default=39.02)

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'ptype': self.ptype,
                'area': self.area, 'build_unit': self.build_unit,
                'contractor': self.contractor, 'supervisor': self.supervisor,
                'invest': self.invest, 'scale': self.scale, 'scale_unit': self.scale_unit,
                'stage': self.stage, 'progress': self.progress,
                'start_date': self.start_date, 'plan_end_date': self.plan_end_date,
                'actual_end_date': self.actual_end_date, 'status': self.status,
                'lng': self.lng, 'lat': self.lat}


# ===== Step 5: 规建管一体化模型 =====

class ProjectStage(db.Model):
    """项目阶段里程碑"""
    __tablename__ = 'dc_project_stage'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, nullable=False, comment='关联项目')
    stage_name = db.Column(db.String(32), comment='阶段名称')
    stage_order = db.Column(db.Integer, default=0, comment='顺序')
    start_date = db.Column(db.String(16))
    plan_end_date = db.Column(db.String(16), comment='计划完成')
    actual_end_date = db.Column(db.String(16), comment='实际完成')
    status = db.Column(db.String(8), default='未开始', comment='未开始/进行中/已完成/超期')
    resp_dept = db.Column(db.String(128), default='', comment='责任处室（可多个，逗号分隔）')
    remark = db.Column(db.String(256), default='')

    def to_dict(self):
        return {k: getattr(self, k) for k in [
            'id', 'project_id', 'stage_name', 'stage_order',
            'start_date', 'plan_end_date', 'actual_end_date', 'status',
            'resp_dept', 'remark'
        ]}


class ApprovalRecord(db.Model):
    """审批记录"""
    __tablename__ = 'dc_approval'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, nullable=False, comment='关联项目')
    approval_type = db.Column(db.String(32), comment='施工许可/规划验收/消防验收/竣工备案')
    apply_date = db.Column(db.String(16))
    approve_date = db.Column(db.String(16))
    status = db.Column(db.String(8), default='待审批', comment='待审批/已通过/已驳回')
    approver = db.Column(db.String(32))
    remark = db.Column(db.String(256), default='')

    def to_dict(self):
        return {k: getattr(self, k) for k in [
            'id', 'project_id', 'approval_type', 'apply_date',
            'approve_date', 'status', 'approver', 'remark'
        ]}


class BusinessLicense(db.Model):
    """建筑业企业"""
    __tablename__ = 'dc_business'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    cert_level = db.Column(db.String(16), comment='资质等级')
    cert_type = db.Column(db.String(32), comment='资质类别')
    area = db.Column(db.String(32))
    workers = db.Column(db.Integer, default=0)
    status = db.Column(db.SmallInteger, default=0)

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'cert_level': self.cert_level,
                'cert_type': self.cert_type, 'area': self.area,
                'workers': self.workers, 'status': self.status}


class TransportStation(db.Model):
    """公交站点"""
    __tablename__ = 'dc_bus_station'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False)
    lines = db.Column(db.String(128), comment='途经线路')
    area = db.Column(db.String(32))
    daily_flow = db.Column(db.Integer, default=0, comment='日均客流')
    lng = db.Column(db.Float, default=116.10)
    lat = db.Column(db.Float, default=39.02)

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'lines': self.lines,
                'area': self.area, 'daily_flow': self.daily_flow,
                'lng': self.lng, 'lat': self.lat}


class WaterBody(db.Model):
    """河湖"""
    __tablename__ = 'dc_water'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False)
    wtype = db.Column(db.String(16), comment='河/湖/水库')
    area = db.Column(db.String(32))
    water_area = db.Column(db.Float, default=0, comment='水域面积km²')
    quality = db.Column(db.String(8), comment='水质 I-V')
    level = db.Column(db.Float, default=0, comment='水位m')

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'wtype': self.wtype,
                'area': self.area, 'water_area': self.water_area,
                'quality': self.quality, 'level': self.level}


class MunicipalNode(db.Model):
    """市政设施"""
    __tablename__ = 'dc_municipal'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    ftype = db.Column(db.String(32), comment='道路/桥梁/路灯/井盖/管廊/供热/燃气')
    area = db.Column(db.String(32))
    status = db.Column(db.String(16), default='正常')
    lng = db.Column(db.Float, default=116.10)
    lat = db.Column(db.Float, default=39.02)

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'ftype': self.ftype,
                'area': self.area, 'status': self.status,
                'lng': self.lng, 'lat': self.lat}
