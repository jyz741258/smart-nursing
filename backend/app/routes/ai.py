from flask import request, current_app
import json
import hashlib
import hmac
import base64
import uuid
import asyncio
from datetime import datetime
from threading import Thread
from queue import Queue, Empty
from urllib.parse import urlencode, quote
from . import ai_bp
from ..utils.response import api_response, api_error
from ..utils.auth import require_token


def get_system_prompt():
    """获取AI系统提示词"""
    return """你是一个专业的智慧养老护理助手，名为"护护"。你的职责包括：

1. 健康咨询：提供老年人健康相关的科普知识和建议
2. 护理建议：针对常见老年护理问题提供指导
3. 心理关怀：提供情绪疏导和心理支持
4. 生活建议：提供老年人日常生活护理建议
5. 紧急情况指导：在紧急情况下指导用户寻求专业医疗帮助

注意：
- 你不是医生，不能提供正式的医疗诊断
- 对于严重的健康问题或紧急情况，应建议用户立即就医
- 回答应简洁、温暖、易于理解
- 你应该以关心、耐心、专业的态度回应用户"""


def generate_auth_url():
    """生成讯飞星火v2.1 API鉴权后的WebSocket URL"""
    config = current_app.config
    host = 'wss://spark-api.xf-yun.com'
    path = '/v2.1/chat'

    appid = config.get('XFYUN_APPID', '')
    api_key = config.get('XFYUN_API_KEY', '')
    api_secret = config.get('XFYUN_API_SECRET', '')

    now = datetime.utcnow()
    date = now.strftime('%a, %d %b %Y %H:%M:%S GMT')

    signature_origin = f"host: spark-api.xf-yun.com\ndate: {date}\nGET {path} HTTP/1.1"

    signature_sha = hmac.new(
        api_secret.encode('utf-8'),
        signature_origin.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    signature_sha_base64 = base64.b64encode(signature_sha).decode('utf-8')

    authorization_origin = (
        f'api_key="{api_key}", algorithm="hmac-sha256", '
        f'headers="host date request-line", signature="{signature_sha_base64}"'
    )
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')

    # 正确编码所有参数
    encoded_date = quote(date, safe='')
    encoded_signature = quote(signature_sha_base64, safe='')

    url = f"{host}{path}?appid={appid}&signature={encoded_signature}&date={encoded_date}&host=spark-api.xf-yun.com"

    return url


def call_xfyun_ws(message):
    """通过WebSocket调用讯飞星火API"""
    try:
        import websocket
    except ImportError:
        return None, "缺少 websocket-client 库，请运行: pip install websocket-client"

    config = current_app.config
    appid = config.get('XFYUN_APPID', '')
    api_key = config.get('XFYUN_API_KEY', '')
    api_secret = config.get('XFYUN_API_SECRET', '')

    if not api_key or not api_secret or not appid:
        return None, "讯飞星火API未配置完整，请检查APPID、APIKey和APISecret"

    url = generate_auth_url()
    
    result_text = []
    response_queue = Queue()
    
    def on_message(ws, message):
        try:
            data = json.loads(message)
            if 'payload' in data and 'choices' in data['payload']:
                content = data['payload']['choices']['text'][0]['content']
                result_text.append(content)
            if data.get('header', {}).get('code') == 0 and data.get('payload', {}).get('choices', {}).get('status') == 2:
                response_queue.put('done')
                ws.close()
        except Exception as e:
            pass
    
    def on_error(ws, error):
        response_queue.put(f'error:{str(error)}')
    
    def on_close(ws, close_status_code, close_msg):
        if not response_queue.full():
            response_queue.put('closed')

    def on_open(ws):
        payload = {
            "header": {
                "app_id": appid,
                "uid": str(uuid.uuid4())
            },
            "parameter": {
                "chat": {
                    "domain": "generalv2",
                    "temperature": 0.5,
                    "max_tokens": 2048,
                    "auditing": ""
                }
            },
            "payload": {
                "message": {
                    "text": [
                        {"role": "system", "content": get_system_prompt()},
                        {"role": "user", "content": message}
                    ]
                }
            }
        }
        ws.send(json.dumps(payload))

    try:
        ws = websocket.WebSocketApp(
            url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        ws.on_open = on_open
        
        # 运行WebSocket，5秒超时
        import time
        ws.run_forever(ping_timeout=10)
        
        # 等待结果
        try:
            result = response_queue.get(timeout=15)
            if result.startswith('error:'):
                return None, result[6:]
            if result == 'closed' and result_text:
                return ''.join(result_text), None
        except Empty:
            pass
        
        if result_text:
            return ''.join(result_text), None
        
        return None, "未收到响应"
        
    except Exception as e:
        return None, f"WebSocket错误: {str(e)}"


@ai_bp.route('/chat', methods=['POST'])
@require_token
def ai_chat(current_user):
    """AI对话接口"""
    data = request.get_json()
    message = data.get('message', '').strip()

    if not message:
        return api_error('请输入消息内容')

    config = current_app.config
    if not config.get('XFYUN_API_KEY'):
        return api_error('AI服务未配置，请联系管理员设置讯飞星火API密钥')

    response, error = call_xfyun_ws(message)

    if error:
        return api_error(error)

    return api_response({
        'reply': response,
        'model': 'Spark Lite (讯飞星火)'
    }, '对话成功')


@ai_bp.route('/health-check', methods=['GET'])
def ai_health_check():
    """AI服务健康检查"""
    config = current_app.config

    if not config.get('XFYUN_API_KEY'):
        return api_response({
            'status': 'not_configured',
            'message': '讯飞星火API未配置'
        })

    response, error = call_xfyun_ws("你好")

    if error:
        return api_response({
            'status': 'error',
            'message': error
        })

    return api_response({
        'status': 'ok',
        'message': '讯飞星火服务运行正常',
        'model': 'Spark Lite'
    })


@ai_bp.route('/models', methods=['GET'])
def list_models():
    """获取支持的模型列表"""
    return api_response([
        {"id": "generalv2", "name": "讯飞星火 v2 (Lite)", "provider": "讯飞"},
        {"id": "general", "name": "讯飞星火 v3", "provider": "讯飞"}
    ])


@ai_bp.route('/config', methods=['GET'])
@require_token
def get_ai_config(current_user):
    """获取AI配置状态（仅管理员可访问）"""
    if current_user.user_type != 3:
        return api_error('无权限', 403)

    config = current_app.config
    return api_response({
        'provider': 'xfyun',
        'appid_configured': bool(config.get('XFYUN_APPID')),
        'api_key_configured': bool(config.get('XFYUN_API_KEY')),
        'api_secret_configured': bool(config.get('XFYUN_API_SECRET')),
        'model': 'generalv2'
    })


@ai_bp.route('/config', methods=['PUT'])
@require_token
def update_ai_config(current_user):
    """更新AI配置（仅管理员可访问）"""
    if current_user.user_type != 3:
        return api_error('无权限', 403)

    data = request.get_json()
    config = current_app.config

    if 'appid' in data:
        config['XFYUN_APPID'] = data['appid']
    if 'api_key' in data:
        config['XFYUN_API_KEY'] = data['api_key']
    if 'api_secret' in data:
        config['XFYUN_API_SECRET'] = data['api_secret']

    return api_response(message='配置更新成功')