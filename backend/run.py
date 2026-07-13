# -*- coding: utf-8 -*-
"""
启动入口
"""
import os
import sys

# 确保backend目录在path中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

if __name__ == '__main__':
    app = create_app()
    print('=' * 60)
    print('  雄安新区建设和交通管理局 - 协同调度中心后端')
    print('  Step 1: 基础底座（认证 + 网关 + 用户管理）')
    print('=' * 60)
    print('  服务地址: http://localhost:5000')
    print('  健康检查: http://localhost:5000/api/health')
    print('  API接口:')
    print('    POST /api/auth/login          登录')
    print('    POST /api/auth/refresh         刷新Token')
    print('    GET  /api/auth/userinfo        当前用户信息')
    print('    GET  /api/auth/menus           当前用户菜单')
    print('    GET  /api/auth/permissions     当前用户权限')
    print('    POST /api/auth/logout          退出登录')
    print('    CRUD /api/users                用户管理')
    print('    CRUD /api/depts                部门管理')
    print('    CRUD /api/roles                角色管理')
    print('    GET  /api/permissions          权限树')
    print('=' * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
