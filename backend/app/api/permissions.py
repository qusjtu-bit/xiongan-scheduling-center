# -*- coding: utf-8 -*-
"""
权限管理 - 权限树查询
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import Permission

perms_bp = Blueprint('permissions', __name__)


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


@perms_bp.route('', methods=['GET'])
@jwt_required()
def list_permissions():
    """权限树（全部权限）"""
    perms = Permission.query.order_by(Permission.sort).all()
    perm_list = [p.to_dict() for p in perms]
    tree = build_tree(perm_list, 0)
    return jsonify(code=200, message='success', data=tree)


@perms_bp.route('/flat', methods=['GET'])
@jwt_required()
def list_permissions_flat():
    """权限扁平列表"""
    perms = Permission.query.order_by(Permission.sort).all()
    return jsonify(code=200, message='success', data=[p.to_dict() for p in perms])
