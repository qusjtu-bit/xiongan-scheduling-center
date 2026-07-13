# -*- coding: utf-8 -*-
"""
数据模型定义
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

# 多对多关联表：用户-角色
user_role = db.Table(
    'sys_user_role',
    db.Column('user_id', db.Integer, db.ForeignKey('sys_user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('sys_role.id'), primary_key=True),
)

# 多对多关联表：角色-权限
role_permission = db.Table(
    'sys_role_permission',
    db.Column('role_id', db.Integer, db.ForeignKey('sys_role.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('sys_permission.id'), primary_key=True),
)


class User(db.Model):
    """用户表"""
    __tablename__ = 'sys_user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True, nullable=False, comment='登录账号')
    password = db.Column(db.String(256), nullable=False, comment='密码（哈希）')
    real_name = db.Column(db.String(64), nullable=False, comment='真实姓名')
    phone = db.Column(db.String(20), comment='手机号')
    email = db.Column(db.String(128), comment='邮箱')
    avatar = db.Column(db.String(256), comment='头像URL')
    dept_id = db.Column(db.Integer, db.ForeignKey('sys_dept.id'), comment='所属部门ID')
    status = db.Column(db.SmallInteger, default=0, comment='状态：0启用 1禁用')
    remark = db.Column(db.String(256), comment='备注')
    last_login_time = db.Column(db.DateTime, comment='最后登录时间')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # 关联
    dept = db.relationship('Dept', backref='users', foreign_keys=[dept_id])
    roles = db.relationship('Role', secondary=user_role, backref='users')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self, include_roles=False):
        data = {
            'id': self.id,
            'username': self.username,
            'real_name': self.real_name,
            'phone': self.phone,
            'email': self.email,
            'avatar': self.avatar,
            'dept_id': self.dept_id,
            'dept_name': self.dept.dept_name if self.dept else None,
            'status': self.status,
            'remark': self.remark,
            'last_login_time': self.last_login_time.strftime('%Y-%m-%d %H:%M:%S') if self.last_login_time else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }
        if include_roles:
            data['roles'] = [{'id': r.id, 'name': r.role_name, 'code': r.role_code} for r in self.roles]
        return data


class Dept(db.Model):
    """部门表"""
    __tablename__ = 'sys_dept'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, default=0, comment='上级部门ID，0为顶级')
    dept_name = db.Column(db.String(128), nullable=False, comment='部门名称')
    dept_type = db.Column(db.SmallInteger, comment='类型：1局 2处室 3科室 4片区')
    leader = db.Column(db.String(64), comment='负责人')
    phone = db.Column(db.String(20), comment='联系电话')
    sort = db.Column(db.Integer, default=0, comment='排序')
    status = db.Column(db.SmallInteger, default=0, comment='状态：0启用 1禁用')
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'parent_id': self.parent_id,
            'dept_name': self.dept_name,
            'dept_type': self.dept_type,
            'leader': self.leader,
            'phone': self.phone,
            'sort': self.sort,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }


class Role(db.Model):
    """角色表"""
    __tablename__ = 'sys_role'

    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(64), nullable=False, comment='角色名称')
    role_code = db.Column(db.String(64), unique=True, nullable=False, comment='角色编码')
    data_scope = db.Column(db.SmallInteger, default=4, comment='数据范围：1全部 2本处室 3本片区 4本人')
    status = db.Column(db.SmallInteger, default=0, comment='状态：0启用 1禁用')
    remark = db.Column(db.String(256), comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 关联
    permissions = db.relationship('Permission', secondary=role_permission, backref='roles')

    def to_dict(self, include_perms=False):
        data = {
            'id': self.id,
            'role_name': self.role_name,
            'role_code': self.role_code,
            'data_scope': self.data_scope,
            'status': self.status,
            'remark': self.remark,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }
        if include_perms:
            data['permissions'] = [{'id': p.id, 'name': p.perm_name, 'code': p.perm_code} for p in self.permissions]
        return data


class Permission(db.Model):
    """权限表"""
    __tablename__ = 'sys_permission'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, default=0, comment='上级权限ID')
    perm_name = db.Column(db.String(64), nullable=False, comment='权限名称')
    perm_type = db.Column(db.SmallInteger, comment='类型：1菜单 2按钮 3API 4数据')
    perm_code = db.Column(db.String(128), comment='权限标识')
    icon = db.Column(db.String(64), comment='图标')
    path = db.Column(db.String(256), comment='前端路由')
    component = db.Column(db.String(256), comment='前端组件')
    sort = db.Column(db.Integer, default=0, comment='排序')
    status = db.Column(db.SmallInteger, default=0, comment='状态：0启用 1禁用')
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'parent_id': self.parent_id,
            'perm_name': self.perm_name,
            'perm_type': self.perm_type,
            'perm_code': self.perm_code,
            'icon': self.icon,
            'path': self.path,
            'component': self.component,
            'sort': self.sort,
            'status': self.status,
        }


class Message(db.Model):
    """站内消息表"""
    __tablename__ = 'sys_message'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(128), nullable=False, comment='消息标题')
    content = db.Column(db.Text, comment='消息内容')
    msg_type = db.Column(db.SmallInteger, default=1, comment='类型：1通知 2预警 3待办提醒 4系统')
    level = db.Column(db.SmallInteger, default=1, comment='级别：1普通 2重要 3紧急')
    sender = db.Column(db.String(64), default='系统', comment='发送方')
    scope = db.Column(db.SmallInteger, default=1, comment='可见范围：1全部 2角色 3部门 4用户')
    scope_id = db.Column(db.Integer, default=0, comment='范围ID（角色/部门/用户ID）')
    read_users = db.Column(db.Text, default='', comment='已读用户ID，逗号分隔')
    created_at = db.Column(db.DateTime, default=datetime.now)

    def is_read_by(self, user_id):
        if not self.read_users:
            return False
        return str(user_id) in [u.strip() for u in self.read_users.split(',') if u.strip()]

    def to_dict(self, user_id=None):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'msg_type': self.msg_type,
            'msg_type_name': {1: '通知', 2: '预警', 3: '待办提醒', 4: '系统'}.get(self.msg_type, '通知'),
            'level': self.level,
            'level_name': {1: '普通', 2: '重要', 3: '紧急'}.get(self.level, '普通'),
            'sender': self.sender,
            'scope': self.scope,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None,
            'is_read': self.is_read_by(user_id) if user_id else False,
        }


class Todo(db.Model):
    """待办任务表"""
    __tablename__ = 'sys_todo'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(128), nullable=False, comment='待办标题')
    todo_type = db.Column(db.SmallInteger, default=1, comment='类型：1审批 2整改 3备案 4报告 5其他')
    source_system = db.Column(db.String(64), comment='来源系统')
    urgency = db.Column(db.SmallInteger, default=1, comment='紧急程度：1普通 2紧急 3特急')
    due_date = db.Column(db.String(20), comment='截止日期 YYYY-MM-DD')
    status = db.Column(db.SmallInteger, default=0, comment='状态：0待办 1已办 2已逾期')
    link = db.Column(db.String(256), default='', comment='处理跳转锚点')
    scope = db.Column(db.SmallInteger, default=1, comment='可见范围：1全部 2角色 3部门 4用户')
    scope_id = db.Column(db.Integer, default=0, comment='范围ID')
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'todo_type': self.todo_type,
            'todo_type_name': {1: '审批', 2: '整改', 3: '备案', 4: '报告', 5: '其他'}.get(self.todo_type, '其他'),
            'source_system': self.source_system,
            'urgency': self.urgency,
            'urgency_name': {1: '普通', 2: '紧急', 3: '特急'}.get(self.urgency, '普通'),
            'due_date': self.due_date,
            'status': self.status,
            'status_name': {0: '待办', 1: '已办', 2: '已逾期'}.get(self.status, '待办'),
            'link': self.link,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None,
        }


from app.data_models import *  # noqa — 数据中枢模型（Step 3）
