# -*- coding: utf-8 -*-
"""
建交协同调度中心 - Flask 应用入口
"""
import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db = SQLAlchemy()
jwt = JWTManager()


def create_app():
    """应用工厂"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # backend/
    project_dir = os.path.dirname(base_dir)  # xiongan-scheduling-center/
    frontend_dir = os.path.join(project_dir, 'frontend')
    app = Flask(__name__, static_folder=frontend_dir, static_url_path='')

    # 配置
    db_path = os.path.join(base_dir, 'db', 'xiongan.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'xiongan-jjzx-secret-key-2025'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600 * 24  # 24小时
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 3600 * 24 * 7  # 7天

    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    # 注册蓝图
    from app.api.auth import auth_bp
    from app.api.users import users_bp
    from app.api.depts import depts_bp
    from app.api.roles import roles_bp
    from app.api.permissions import perms_bp
    from app.api.gateway import gateway_bp
    from app.api.messages import msg_bp
    from app.api.data import data_bp
    from app.api.overview import overview_bp
    from app.api.project import project_bp
    from app.api.ai import ai_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(depts_bp, url_prefix='/api/depts')
    app.register_blueprint(roles_bp, url_prefix='/api/roles')
    app.register_blueprint(perms_bp, url_prefix='/api/permissions')
    app.register_blueprint(gateway_bp, url_prefix='/api')
    app.register_blueprint(msg_bp, url_prefix='/api')
    app.register_blueprint(data_bp, url_prefix='/api')
    app.register_blueprint(overview_bp, url_prefix='/api')
    app.register_blueprint(project_bp, url_prefix='/api')
    app.register_blueprint(ai_bp, url_prefix='/api')

    # JWT回调：根据identity加载用户对象
    from app.models import User

    @jwt.user_lookup_loader
    def user_lookup_callback(jwt_header, jwt_payload):
        user_id = jwt_payload.get('sub')
        if user_id:
            return User.query.get(int(user_id))
        return None

    # JWT错误处理
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify(code=401, message='Token已过期，请重新登录'), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify(code=401, message='无效的Token'), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify(code=401, message='缺少认证Token'), 401

    # 全局错误处理
    @app.errorhandler(404)
    def not_found(e):
        return jsonify(code=404, message='接口不存在'), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify(code=500, message='服务器内部错误'), 500

    # 健康检查
    @app.route('/api/health')
    def health():
        return jsonify(code=200, message='success', data={'status': 'running', 'service': '建交协同调度中心'})

    # 前端页面
    @app.route('/')
    def index():
        from flask import send_from_directory
        return send_from_directory(app.static_folder, 'index.html')

    return app


if __name__ == '__main__':
    app = create_app()
    print('=' * 60)
    print('  雄安新区建设和交通管理局 - 协同调度中心后端')
    print('  Step 1: 基础底座（认证 + 网关 + 用户管理）')
    print('=' * 60)
    print('  服务地址: http://localhost:5000')
    print('  健康检查: http://localhost:5000/api/health')
    print('  API文档:')
    print('    POST /api/auth/login          登录')
    print('    POST /api/auth/refresh         刷新Token')
    print('    GET  /api/auth/userinfo        当前用户信息')
    print('    GET  /api/auth/menus           当前用户菜单')
    print('    GET  /api/auth/logout          退出登录')
    print('    CRUD /api/users                用户管理')
    print('    CRUD /api/depts                部门管理')
    print('    CRUD /api/roles                角色管理')
    print('    GET  /api/permissions          权限树')
    print('    GET  /api/messages             消息列表')
    print('    PUT  /api/messages/<id>/read   标记已读')
    print('    GET  /api/todos                待办列表')
    print('    GET  /api/workbench/overview   工作台聚合')
    print('=' * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
