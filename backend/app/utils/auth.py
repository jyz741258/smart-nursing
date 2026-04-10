import jwt
import random
import string
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request, g
from .response import api_error
from .. import get_redis
from ..models import User


def require_token(f):
    """Token验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return api_error('请先登录', 401)

        # 移除Bearer前缀
        if token.startswith('Bearer '):
            token = token[7:]

        payload = verify_token(token)
        if not payload:
            return api_error('登录已过期，请重新登录', 401)

        # 获取用户信息
        user = User.query.get(payload['user_id'])
        if not user:
            return api_error('用户不存在', 401)

        if user.status != 1:
            return api_error('账号已被禁用', 403)

        g.current_user = user
        return f(user, *args, **kwargs)
    return decorated_function


def generate_token(user_id, user_type=1):
    """生成JWT Token"""
    expires = current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
    if isinstance(expires, int):
        expires = timedelta(seconds=expires)
    payload = {
        'user_id': user_id,
        'user_type': user_type,
        'exp': datetime.utcnow() + expires,
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    return token


def verify_token(token):
    """验证JWT Token"""
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def generate_sms_code(length=6):
    """生成随机短信验证码"""
    return ''.join(random.choices(string.digits, k=length))


def send_sms_code(phone, code):
    """发送短信验证码（模拟，实际项目中需要接入短信网关）"""
    redis = get_redis()
    key = f'sms_code:{phone}'
    redis.setex(key, current_app.config['SMS_CODE_EXPIRES'], code)
    print(f"[模拟短信] 向手机号 {phone} 发送验证码: {code}")
    return True


def verify_sms_code(phone, code):
    """验证短信验证码"""
    redis = get_redis()
    key = f'sms_code:{phone}'
    stored_code = redis.get(key)
    if stored_code and stored_code == code:
        redis.delete(key)
        return True
    return False
