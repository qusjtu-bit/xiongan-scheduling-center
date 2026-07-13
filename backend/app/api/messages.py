# -*- coding: utf-8 -*-
"""
消息中心 + 工作台聚合（message-service）

提供站内消息、待办任务、工作台首页聚合数据接口。
可见范围(scope)：1全部 2按角色 3按部门 4按用户
"""
from sqlalchemy import and_, or_

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, current_user
from app import db
from app.models import Message, Todo

msg_bp = Blueprint('message', __name__)


def scope_filter(model):
    """根据当前用户的角色/部门/ID构造可见范围过滤条件"""
    user = current_user
    role_ids = [r.id for r in user.roles]
    conditions = [model.scope == 1]  # 全部可见
    for rid in role_ids:
        conditions.append(and_(model.scope == 2, model.scope_id == rid))
    if user.dept_id:
        conditions.append(and_(model.scope == 3, model.scope_id == user.dept_id))
    conditions.append(and_(model.scope == 4, model.scope_id == user.id))
    return or_(*conditions)


@msg_bp.route('/messages', methods=['GET'])
@jwt_required()
def message_list():
    """站内消息列表（支持 unread=1 仅看未读）"""
    only_unread = request.args.get('unread') == '1'
    msgs = Message.query.filter(scope_filter(Message)).order_by(Message.created_at.desc()).all()
    data = [m.to_dict(user_id=current_user.id) for m in msgs]
    if only_unread:
        data = [m for m in data if not m['is_read']]
    unread_count = sum(1 for m in data if not m['is_read'])
    return jsonify(code=200, message='success',
                   data={'list': data, 'total': len(data), 'unread': unread_count})


@msg_bp.route('/messages/<int:mid>/read', methods=['PUT'])
@jwt_required()
def read_message(mid):
    """标记消息已读"""
    m = Message.query.get(mid)
    if not m:
        return jsonify(code=404, message='消息不存在'), 404
    if not m.is_read_by(current_user.id):
        read = [u for u in (m.read_users or '').split(',') if u.strip()]
        read.append(str(current_user.id))
        m.read_users = ','.join(read)
        db.session.commit()
    return jsonify(code=200, message='success')


@msg_bp.route('/messages/<int:mid>', methods=['DELETE'])
@jwt_required()
def delete_message(mid):
    """删除消息"""
    m = Message.query.get(mid)
    if not m:
        return jsonify(code=404, message='消息不存在'), 404
    db.session.delete(m)
    db.session.commit()
    return jsonify(code=200, message='success')


@msg_bp.route('/todos', methods=['GET'])
@jwt_required()
def todo_list():
    """待办任务列表"""
    todos = Todo.query.filter(scope_filter(Todo)).order_by(
        Todo.urgency.desc(), Todo.created_at.desc()).all()
    data = [t.to_dict() for t in todos]
    return jsonify(code=200, message='success', data={'list': data, 'total': len(data)})


@msg_bp.route('/workbench/overview', methods=['GET'])
@jwt_required()
def workbench_overview():
    """工作台首页聚合数据"""
    user = current_user
    role_ids = [r.id for r in user.roles]

    # —— 我的待办 ——
    todos = Todo.query.filter(scope_filter(Todo)).filter(Todo.status == 0).all()
    todo_count = len(todos)
    urgent_todo_count = sum(1 for t in todos if t.urgency >= 2)
    todo_top = [t.to_dict() for t in todos[:8]]

    # —— 消息 ——
    msgs = Message.query.filter(scope_filter(Message)).all()
    msg_list = [m.to_dict(user_id=user.id) for m in msgs]
    unread_count = sum(1 for m in msg_list if not m['is_read'])
    warning_list = [m for m in msg_list if m['msg_type'] == 2][:5]  # 预警TOP5

    # —— 快捷入口（按角色）——
    quick_entries = get_quick_entries(user, role_ids)

    # —— 工作统计（Mock，体现个性化）——
    stats = {
        'month_handled': 28 + (user.id * 5) % 24,   # 本月办件量
        'avg_duration': '1.6 天',                     # 平均审批时效
        'on_time_rate': '95.8%',                      # 按时办结率
        'pending': todo_count,                         # 在办事项
    }

    return jsonify(code=200, message='success', data={
        'todo_count': todo_count,
        'urgent_todo_count': urgent_todo_count,
        'unread_count': unread_count,
        'warning_list': warning_list,
        'todo_top': todo_top,
        'quick_entries': quick_entries,
        'stats': stats,
    })


def get_quick_entries(user, role_ids):
    """按角色返回常用快捷入口"""
    # 局领导：全局视角
    if 1 in role_ids:
        return [
            {'name': '全局总览', 'icon': '🛰️', 'route': '/overview'},
            {'name': '态势大屏', 'icon': '📊', 'route': '/overview'},
            {'name': '规建管一体化', 'icon': '🏗️', 'route': '/project'},
            {'name': '业务专题', 'icon': '🗺️', 'route': '/topic'},
        ]
    # 系统管理员：管理视角
    if 4 in role_ids:
        return [
            {'name': '用户管理', 'icon': '👤', 'route': '/system/users'},
            {'name': '角色管理', 'icon': '🔑', 'route': '/system/roles'},
            {'name': '部门管理', 'icon': '🏢', 'route': '/system/depts'},
            {'name': '网关监控', 'icon': '🌐', 'route': '/system'},
        ]
    # 处室负责人：业务+管理
    if 2 in role_ids:
        return [
            {'name': '规建管一体化', 'icon': '🏗️', 'route': '/project'},
            {'name': '本处室专题', 'icon': '🗂️', 'route': '/topic'},
            {'name': '审批中心', 'icon': '✅', 'route': '/todos'},
            {'name': '消息中心', 'icon': '📬', 'route': '/messages'},
        ]
    # 业务经办人 / 默认
    return [
        {'name': '我的待办', 'icon': '📋', 'route': '/todos'},
        {'name': '规建管一体化', 'icon': '🏗️', 'route': '/project'},
        {'name': '业务专题', 'icon': '🗺️', 'route': '/topic'},
        {'name': '备案中心', 'icon': '📝', 'route': '/todos'},
    ]
