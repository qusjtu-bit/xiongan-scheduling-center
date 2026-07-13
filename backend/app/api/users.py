# -*- coding: utf-8 -*-
"""
用户管理 CRUD
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, current_user
from app import db
from app.models import User, Dept, user_role
from app.api.auth import build_menu_tree  # 复用树构建逻辑

users_bp = Blueprint('users', __name__)


def check_perm(code):
    """检查当前用户是否拥有某权限"""
    if not current_user:
        return False
    for role in current_user.roles:
        for perm in role.permissions:
            if perm.perm_code == code:
                return True
    return False


@users_bp.route('', methods=['GET'])
@jwt_required()
def list_users():
    """用户列表（分页+搜索）"""
    if not check_perm('system:user:list'):
        return jsonify(code=403, message='无权限'), 403

    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 20))
    keyword = request.args.get('keyword', '').strip()
    dept_id = request.args.get('dept_id', type=int)
    status = request.args.get('status', type=int)

    query = User.query
    if keyword:
        query = query.filter(
            db.or_(User.username.like(f'%{keyword}%'),
                   User.real_name.like(f'%{keyword}%'),
                   User.phone.like(f'%{keyword}%'))
        )
    if dept_id:
        query = query.filter_by(dept_id=dept_id)
    if status is not None:
        query = query.filter_by(status=status)

    total = query.count()
    users = query.order_by(User.id).offset((page - 1) * size).limit(size).all()

    return jsonify(code=200, message='success', data={
        'list': [u.to_dict(include_roles=True) for u in users],
        'total': total,
        'page': page,
        'size': size,
    })


@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """用户详情"""
    if not check_perm('system:user:list'):
        return jsonify(code=403, message='无权限'), 403
    user = User.query.get_or_404(user_id)
    return jsonify(code=200, message='success', data=user.to_dict(include_roles=True))


@users_bp.route('', methods=['POST'])
@jwt_required()
def add_user():
    """新增用户"""
    if not check_perm('system:user:add'):
        return jsonify(code=403, message='无权限'), 403

    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    if not username:
        return jsonify(code=400, message='账号不能为空'), 400
    if User.query.filter_by(username=username).first():
        return jsonify(code=400, message='账号已存在'), 400

    user = User(
        username=username,
        real_name=data.get('real_name', ''),
        phone=data.get('phone', ''),
        email=data.get('email', ''),
        dept_id=data.get('dept_id'),
        status=data.get('status', 0),
        remark=data.get('remark', ''),
    )
    user.set_password(data.get('password', '123456'))

    db.session.add(user)
    db.session.flush()

    # 分配角色
    role_ids = data.get('role_ids', [])
    if role_ids:
        for rid in role_ids:
            db.session.execute(user_role.insert().values(user_id=user.id, role_id=rid))

    db.session.commit()
    return jsonify(code=200, message='新增成功', data=user.to_dict(include_roles=True))


@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """编辑用户"""
    if not check_perm('system:user:update'):
        return jsonify(code=403, message='无权限'), 403

    user = User.query.get_or_404(user_id)
    data = request.get_json(silent=True) or {}

    if 'real_name' in data:
        user.real_name = data['real_name']
    if 'phone' in data:
        user.phone = data['phone']
    if 'email' in data:
        user.email = data['email']
    if 'dept_id' in data:
        user.dept_id = data['dept_id']
    if 'status' in data:
        user.status = data['status']
    if 'remark' in data:
        user.remark = data['remark']
    if data.get('password'):
        user.set_password(data['password'])

    # 更新角色
    if 'role_ids' in data:
        db.session.execute(user_role.delete().where(user_role.c.user_id == user.id))
        for rid in data['role_ids']:
            db.session.execute(user_role.insert().values(user_id=user.id, role_id=rid))

    db.session.commit()
    return jsonify(code=200, message='更新成功', data=user.to_dict(include_roles=True))


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """删除用户"""
    if not check_perm('system:user:delete'):
        return jsonify(code=403, message='无权限'), 403

    user = User.query.get_or_404(user_id)
    if user.username == 'admin':
        return jsonify(code=400, message='不允许删除超级管理员'), 400

    db.session.execute(user_role.delete().where(user_role.c.user_id == user_id))
    db.session.delete(user)
    db.session.commit()
    return jsonify(code=200, message='删除成功')


@users_bp.route('/reset-password/<int:user_id>', methods=['PUT'])
@jwt_required()
def reset_password(user_id):
    """重置密码"""
    if not check_perm('system:user:update'):
        return jsonify(code=403, message='无权限'), 403

    user = User.query.get_or_404(user_id)
    data = request.get_json(silent=True) or {}
    new_password = data.get('password', '123456')
    user.set_password(new_password)
    db.session.commit()
    return jsonify(code=200, message='密码重置成功')
