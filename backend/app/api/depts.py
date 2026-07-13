# -*- coding: utf-8 -*-
"""
部门管理 CRUD（树形结构）
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, current_user
from app import db
from app.models import Dept

depts_bp = Blueprint('depts', __name__)


def check_perm(code):
    if not current_user:
        return False
    for role in current_user.roles:
        for perm in role.permissions:
            if perm.perm_code == code:
                return True
    return False


def build_tree(items, parent_id):
    tree = []
    for item in items:
        if item['parent_id'] == parent_id:
            children = build_tree(items, item['id'])
            node = dict(item)
            if children:
                node['children'] = children
            tree.append(node)
    return tree


@depts_bp.route('', methods=['GET'])
@jwt_required()
def list_depts():
    """部门列表（树形）"""
    if not check_perm('system:dept:list'):
        return jsonify(code=403, message='无权限'), 403

    depts = Dept.query.order_by(Dept.sort).all()
    dept_list = [d.to_dict() for d in depts]
    tree = build_tree(dept_list, 0)
    return jsonify(code=200, message='success', data=tree)


@depts_bp.route('/flat', methods=['GET'])
@jwt_required()
def list_depts_flat():
    """部门列表（扁平，供下拉选择用）"""
    depts = Dept.query.order_by(Dept.sort).all()
    return jsonify(code=200, message='success', data=[d.to_dict() for d in depts])


@depts_bp.route('', methods=['POST'])
@jwt_required()
def add_dept():
    if not check_perm('system:dept:add'):
        return jsonify(code=403, message='无权限'), 403
    data = request.get_json(silent=True) or {}
    dept = Dept(
        parent_id=data.get('parent_id', 0),
        dept_name=data.get('dept_name', ''),
        dept_type=data.get('dept_type', 3),
        leader=data.get('leader', ''),
        phone=data.get('phone', ''),
        sort=data.get('sort', 0),
        status=data.get('status', 0),
    )
    db.session.add(dept)
    db.session.commit()
    return jsonify(code=200, message='新增成功', data=dept.to_dict())


@depts_bp.route('/<int:dept_id>', methods=['PUT'])
@jwt_required()
def update_dept(dept_id):
    if not check_perm('system:dept:update'):
        return jsonify(code=403, message='无权限'), 403
    dept = Dept.query.get_or_404(dept_id)
    data = request.get_json(silent=True) or {}
    for field in ['parent_id', 'dept_name', 'dept_type', 'leader', 'phone', 'sort', 'status']:
        if field in data:
            setattr(dept, field, data[field])
    db.session.commit()
    return jsonify(code=200, message='更新成功', data=dept.to_dict())


@depts_bp.route('/<int:dept_id>', methods=['DELETE'])
@jwt_required()
def delete_dept(dept_id):
    if not check_perm('system:dept:delete'):
        return jsonify(code=403, message='无权限'), 403
    children = Dept.query.filter_by(parent_id=dept_id).count()
    if children > 0:
        return jsonify(code=400, message='该部门下有子部门，不允许删除'), 400
    dept = Dept.query.get_or_404(dept_id)
    db.session.delete(dept)
    db.session.commit()
    return jsonify(code=200, message='删除成功')
