import jwt
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
    if redis is None:
        # 无Redis时，仅打印验证码（用于测试）
        print(f"[模拟短信] 向手机号 {phone} 发送验证码: {code} (Redis未连接，仅显示)")
        return True
    key = f'sms_code:{phone}'
    redis.setex(key, current_app.config['SMS_CODE_EXPIRES'], code)
    print(f"[模拟短信] 向手机号 {phone} 发送验证码: {code}")
    return True


def verify_sms_code(phone, code):
    """验证短信验证码"""
    redis = get_redis()
    if redis is None:
        # 无Redis时，验证码通过（用于测试）
        print(f"[模拟验证] 验证码 {code} 验证通过 (Redis未连接)")
        return True
    key = f'sms_code:{phone}'
    stored_code = redis.get(key)
    if stored_code and stored_code == code:
        redis.delete(key)
        return True
    return False


def send_email_code(email, code):
    """发送邮箱验证码（使用SMTP发送真实邮件）"""
    redis = get_redis()
    if redis is None:
        # 无Redis时，仅打印验证码（用于测试）
        print(f"[模拟邮箱] 向邮箱 {email} 发送验证码: {code} (Redis未连接，仅显示)")
        return True

    # 存储验证码到Redis
    key = f'email_code:{email}'
    redis.setex(key, current_app.config.get('SMS_CODE_EXPIRES', 300), code)

    # 获取邮件配置
    mail_config = {
        'server': current_app.config.get('MAIL_SERVER'),
        'port': current_app.config.get('MAIL_PORT', 587),
        'use_tls': current_app.config.get('MAIL_USE_TLS', True),
        'username': current_app.config.get('MAIL_USERNAME'),
        'password': current_app.config.get('MAIL_PASSWORD'),
        'sender': current_app.config.get('MAIL_DEFAULT_SENDER')
    }

    # 检查邮件配置是否完整
    if not all([mail_config['server'], mail_config['username'], mail_config['password'], mail_config['sender']]):
        # 配置不完整，仅打印验证码
        print(f"[模拟邮箱] 向邮箱 {email} 发送验证码: {code} (邮件配置不完整，仅显示)")
        return True

    try:
        # 创建邮件
        msg = MIMEMultipart('alternative')
        msg['Subject'] = '【智慧养老系统】注册验证码'
        msg['From'] = mail_config['sender']
        msg['To'] = email

        # HTML邮件内容
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea, #764ba2); padding: 30px; text-align: center; color: white; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .content {{ padding: 40px 30px; text-align: center; }}
                .code-box {{ background: linear-gradient(135deg, #f0f9ff, #e0f2fe); border: 2px dashed #409eff; border-radius: 16px; padding: 30px; margin: 20px 0; }}
                .code {{ font-size: 42px; font-weight: bold; color: #1565c0; letter-spacing: 12px; font-family: 'Courier New', monospace; }}
                .tips {{ color: #666; font-size: 14px; margin-top: 20px; line-height: 1.6; }}
                .warning {{ color: #f56c6c; font-size: 12px; margin-top: 30px; }}
                .footer {{ background: #f9f9f9; padding: 20px; text-align: center; color: #999; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 智慧养老系统</h1>
                </div>
                <div class="content">
                    <p style="font-size: 18px; color: #333;">您好！</p>
                    <p style="font-size: 16px; color: #666;">感谢您注册智慧养老系统，您的验证码是：</p>
                    <div class="code-box">
                        <div class="code">{code}</div>
                    </div>
                    <p class="tips">
                        验证码 <strong>5分钟</strong> 内有效，请尽快完成验证<br>
                        如非本人操作，请忽略此邮件
                    </p>
                    <p class="warning">⚠️ 请勿向任何人透露此验证码，谨防诈骗！</p>
                </div>
                <div class="footer">
                    <p>智慧养老系统 - 让科技守护每一位老人</p>
                    <p>此邮件由系统自动发送，请勿回复</p>
                </div>
            </div>
        </body>
        </html>
        """

        # 纯文本版本（兼容不支持HTML的邮件客户端）
        text_content = f"""
        智慧养老系统 - 注册验证码

        您好！

        感谢您注册智慧养老系统，您的验证码是：{code}

        验证码 5分钟 内有效，请尽快完成验证。
        如非本人操作，请忽略此邮件。

        请勿向任何人透露此验证码，谨防诈骗！

        ---
        智慧养老系统
        此邮件由系统自动发送，请勿回复
        """

        # 添加邮件内容
        msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        # 发送邮件
        server = smtplib.SMTP(mail_config['server'], mail_config['port'])
        server.ehlo()

        if mail_config['use_tls']:
            server.starttls()

        server.login(mail_config['username'], mail_config['password'])
        server.sendmail(mail_config['sender'], [email], msg.as_string())
        server.quit()

        print(f"[真实邮件] 向邮箱 {email} 发送验证码: {code}")
        return True

    except smtplib.SMTPAuthenticationError:
        print(f"[邮件错误] SMTP认证失败，请检查邮箱用户名和授权码")
        return False
    except smtplib.SMTPException as e:
        print(f"[邮件错误] SMTP发送失败: {str(e)}")
        # 即使发送失败，验证码仍然保存在Redis中，可以用于调试或备用验证
        return False
    except Exception as e:
        print(f"[邮件错误] 发送邮件时发生异常: {str(e)}")
        return False


def verify_email_code(email, code):
    """验证邮箱验证码"""
    redis = get_redis()
    if redis is None:
        # 无Redis时，验证码通过（用于测试）
        print(f"[模拟验证] 邮箱验证码 {code} 验证通过 (Redis未连接)")
        return True
    key = f'email_code:{email}'
    stored_code = redis.get(key)
    if stored_code and stored_code == code:
        redis.delete(key)
        return True
    return False
