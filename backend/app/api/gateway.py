# -*- coding: utf-8 -*-
"""
API网关（gateway-service）
- 统一入口路由
- 请求日志记录
- 简单限流
"""
import time
from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt
from functools import wraps
from collections import defaultdict
from datetime import datetime

gateway_bp = Blueprint('gateway', __name__)

# 简单内存限流：{user_id: [(timestamp, ...)]}
_rate_limit_store = defaultdict(list)


def rate_limit(max_requests=100, window=60):
    """简单限流装饰器：每个用户 window秒内最多 max_requests 次请求"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            from flask_jwt_extended import get_jwt_identity
            user_id = get_jwt_identity() or 'anonymous'
            now = time.time()
            # 清理过期记录
            _rate_limit_store[user_id] = [
                ts for ts in _rate_limit_store[user_id] if now - ts < window
            ]
            if len(_rate_limit_store[user_id]) >= max_requests:
                return jsonify(code=429, message=f'请求过于频繁，请{window}秒后重试'), 429
            _rate_limit_store[user_id].append(now)
            return f(*args, **kwargs)
        return wrapped
    return decorator


@gateway_bp.route('/gateway/stats', methods=['GET'])
@jwt_required()
def gateway_stats():
    """网关状态统计"""
    return jsonify(code=200, message='success', data={
        'service': '建交协同调度中心 API网关',
        'version': '1.0',
        'status': 'running',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'active_users': len(_rate_limit_store),
        'total_requests': sum(len(v) for v in _rate_limit_store.values()),
    })


@gateway_bp.route('/gateway/logs', methods=['GET'])
@jwt_required()
def gateway_logs():
    """查看网关日志（简化版）"""
    # 实际应在中间件中记录完整日志，这里返回简化信息
    return jsonify(code=200, message='success', data={
        'note': '完整日志需查看服务器日志文件',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    })
