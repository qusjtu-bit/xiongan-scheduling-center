# -*- coding: utf-8 -*-
"""
统一身份认证服务（auth-service）
- 登录 / 刷新Token / 当前用户信息 / 用户菜单 / 退出
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, current_user
)
from app import db
from app.models import User, Permission

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """登录接口"""
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify(code=400, message='请输入账号和密码'), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify(code=401, message='账号不存在'), 401

    if user.status != 0:
        return jsonify(code=403, message='账号已禁用，请联系管理员'), 403

    if not user.check_password(password):
        return jsonify(code=401, message='密码错误'), 401

    # 更新最后登录时间
    user.last_login_time = datetime.now()
    db.session.commit()

    # 生成Token（identity存用户ID字符串）
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify(code=200, message='登录成功', data={
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'user': user.to_dict(include_roles=True),
    })


@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """刷新Token"""
    from flask_jwt_extended import decode_token
    from flask import current_app

    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify(code=401, message='缺少Refresh Token'), 401

    refresh_token = auth_header[7:]
    try:
        decoded = decode_token(refresh_token)
        user_id = int(decoded['sub'])
        user = User.query.get(user_id)
        if not user or user.status != 0:
            return jsonify(code=401, message='用户不存在或已禁用'), 401

        new_access_token = create_access_token(identity=str(user.id))
        return jsonify(code=200, message='刷新成功', data={
            'access_token': new_access_token,
            'token_type': 'Bearer',
        })
    except Exception as e:
        return jsonify(code=401, message=f'Refresh Token无效或已过期'), 401


@auth_bp.route('/userinfo', methods=['GET'])
@jwt_required()
def userinfo():
    """获取当前用户信息"""
    user = current_user
    return jsonify(code=200, message='success', data=user.to_dict(include_roles=True))


@auth_bp.route('/menus', methods=['GET'])
@jwt_required()
def menus():
    """获取当前用户的菜单树（按角色权限过滤）"""
    user = current_user

    # 收集该用户所有角色关联的权限
    perm_ids = set()
    for role in user.roles:
        for perm in role.permissions:
            perm_ids.add(perm.id)

    # 查询菜单类型权限（type=1），构建树
    all_perms = Permission.query.filter_by(perm_type=1, status=0).order_by(Permission.sort).all()
    menu_list = [p.to_dict() for p in all_perms if p.id in perm_ids]

    # 构建树结构
    menu_tree = build_menu_tree(menu_list, 0)

    return jsonify(code=200, message='success', data=menu_tree)


def build_menu_tree(perms_list, parent_id):
    """递归构建菜单树"""
    tree = []
    for p in perms_list:
        if p['parent_id'] == parent_id:
            children = build_menu_tree(perms_list, p['id'])
            node = dict(p)
            if children:
                node['children'] = children
            tree.append(node)
    return tree


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """退出登录"""
    # JWT是无状态的，前端删除Token即可
    return jsonify(code=200, message='退出成功')


@auth_bp.route('/permissions', methods=['GET'])
@jwt_required()
def get_permissions():
    """获取当前用户的所有权限标识列表"""
    user = current_user
    perm_codes = set()
    for role in user.roles:
        for perm in role.permissions:
            if perm.perm_code:
                perm_codes.add(perm.perm_code)
    return jsonify(code=200, message='success', data=list(perm_codes))
