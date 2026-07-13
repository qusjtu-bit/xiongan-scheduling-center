# -*- coding: utf-8 -*-
"""
角色管理 CRUD + 权限分配
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, current_user
from app import db
from app.models import Role, Permission, role_permission

roles_bp = Blueprint('roles', __name__)


def check_perm(code):
    if not current_user:
        return False
    for role in current_user.roles:
        for perm in role.permissions:
            if perm.perm_code == code:
                return True
    return False


@roles_bp.route('', methods=['GET'])
@jwt_required()
def list_roles():
    """角色列表"""
    if not check_perm('system:role:list'):
        return jsonify(code=403, message='无权限'), 403
    roles = Role.query.order_by(Role.id).all()
    return jsonify(code=200, message='success', data=[r.to_dict(include_perms=True) for r in roles])


@roles_bp.route('/<int:role_id>', methods=['GET'])
@jwt_required()
def get_role(role_id):
    role = Role.query.get_or_404(role_id)
    return jsonify(code=200, message='success', data=role.to_dict(include_perms=True))


@roles_bp.route('', methods=['POST'])
@jwt_required()
def add_role():
    if not check_perm('system:role:add'):
        return jsonify(code=403, message='无权限'), 403
    data = request.get_json(silent=True) or {}
    role_code = data.get('role_code', '').strip()
    if not role_code:
        return jsonify(code=400, message='角色编码不能为空'), 400
    if Role.query.filter_by(role_code=role_code).first():
        return jsonify(code=400, message='角色编码已存在'), 400

    role = Role(
        role_name=data.get('role_name', ''),
        role_code=role_code,
        data_scope=data.get('data_scope', 4),
        status=data.get('status', 0),
        remark=data.get('remark', ''),
    )
    db.session.add(role)
    db.session.flush()

    # 分配权限
    perm_ids = data.get('permission_ids', [])
    for pid in perm_ids:
        db.session.execute(role_permission.insert().values(role_id=role.id, permission_id=pid))

    db.session.commit()
    return jsonify(code=200, message='新增成功', data=role.to_dict(include_perms=True))


@roles_bp.route('/<int:role_id>', methods=['PUT'])
@jwt_required()
def update_role(role_id):
    if not check_perm('system:role:update'):
        return jsonify(code=403, message='无权限'), 403
    role = Role.query.get_or_404(role_id)
    data = request.get_json(silent=True) or {}

    for field in ['role_name', 'data_scope', 'status', 'remark']:
        if field in data:
            setattr(role, field, data[field])

    # 更新权限
    if 'permission_ids' in data:
        db.session.execute(role_permission.delete().where(role_permission.c.role_id == role_id))
        for pid in data['permission_ids']:
            db.session.execute(role_permission.insert().values(role_id=role_id, permission_id=pid))

    db.session.commit()
    return jsonify(code=200, message='更新成功', data=role.to_dict(include_perms=True))


@roles_bp.route('/<int:role_id>', methods=['DELETE'])
@jwt_required()
def delete_role(role_id):
    if not check_perm('system:role:delete'):
        return jsonify(code=403, message='无权限'), 403
    role = Role.query.get_or_404(role_id)
    if role.role_code in ('ADMIN', 'LEADER'):
        return jsonify(code=400, message='系统内置角色不允许删除'), 400

    db.session.execute(role_permission.delete().where(role_permission.c.role_id == role_id))
    db.session.delete(role)
    db.session.commit()
    return jsonify(code=200, message='删除成功')


@roles_bp.route('/<int:role_id>/permissions', methods=['PUT'])
@jwt_required()
def assign_permissions(role_id):
    """单独分配权限"""
    if not check_perm('system:role:update'):
        return jsonify(code=403, message='无权限'), 403
    role = Role.query.get_or_404(role_id)
    data = request.get_json(silent=True) or {}
    perm_ids = data.get('permission_ids', [])

    db.session.execute(role_permission.delete().where(role_permission.c.role_id == role_id))
    for pid in perm_ids:
        db.session.execute(role_permission.insert().values(role_id=role_id, permission_id=pid))

    db.session.commit()
    return jsonify(code=200, message='权限分配成功')
