from flask import request, current_app
import json
import requests
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


def call_xfyun_http(message):
    """通过HTTP接口调用讯飞星火API - 使用APIPassword认证"""
    config = current_app.config

    # HTTP接口使用APIPassword（不是APIKey/APISecret）
    api_password = config.get('XFYUN_HTTP_PASSWORD', '')

    if not api_password:
        # 尝试使用旧的API Key（兼容）
        api_key = config.get('XFYUN_API_KEY', '')
        if api_key:
            api_password = api_key
        else:
            return None, "讯飞星火API未配置，请检查.env中的XFYUN_HTTP_PASSWORD"

    try:
        # HTTP接口地址
        url = "https://spark-api-open.xf-yun.com/v1/chat/completions"

        # 请求头 - 使用APIPassword作为Bearer Token
        headers = {
            "Authorization": f"Bearer {api_password}",
            "Content-Type": "application/json"
        }

        # 请求体 - Spark Lite
        payload = {
            "model": "lite",
            "messages": [
                {"role": "system", "content": get_system_prompt()},
                {"role": "user", "content": message}
            ],
            "temperature": 0.5,
            "max_tokens": 2048
        }

        current_app.logger.info(f"调用讯飞星火HTTP API")

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )

        current_app.logger.info(f"讯飞API响应状态: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            current_app.logger.info(f"讯飞API响应成功")

            # 提取回复内容
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                return content, None
            elif 'text' in result:
                return result['text'], None
            else:
                return None, f"API返回格式异常"

        elif response.status_code == 401:
            return None, "API认证失败(401)，请检查APIPassword是否正确，或是否已开通HTTP接口权限"
        elif response.status_code == 403:
            return None, "API访问被拒绝(403)，请确认应用已开通星火大模型能力"
        elif response.status_code == 429:
            return None, "API调用频率超限，请稍后再试"
        else:
            error_detail = response.text[:200] if response.text else "无详细信息"
            return None, f"HTTP {response.status_code}: {error_detail}"

    except requests.exceptions.Timeout:
        return None, "API调用超时，请检查网络连接"
    except requests.exceptions.ConnectionError as e:
        return None, f"网络连接失败: {str(e)}"
    except Exception as e:
        current_app.logger.error(f"讯飞API异常: {str(e)}")
        return None, f"API调用异常: {str(e)}"


@ai_bp.route('/chat', methods=['POST'])
@require_token
def ai_chat(current_user):
    """AI对话接口"""
    data = request.get_json()
    message = data.get('message', '').strip()

    if not message:
        return api_error('请输入消息内容')

    config = current_app.config
    if not config.get('XFYUN_HTTP_PASSWORD') and not config.get('XFYUN_API_KEY'):
        return api_error('AI服务未配置，请联系管理员设置讯飞星火API密钥')

    response, error = call_xfyun_http(message)

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

    if not config.get('XFYUN_HTTP_PASSWORD') and not config.get('XFYUN_API_KEY'):
        return api_response({
            'status': 'not_configured',
            'message': '讯飞星火API未配置'
        })

    response, error = call_xfyun_http("你好")

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
        {"id": "lite", "name": "讯飞星火 Lite", "provider": "讯飞", "version": "v1"}
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
        'http_password_configured': bool(config.get('XFYUN_HTTP_PASSWORD')),
        'api_key_configured': bool(config.get('XFYUN_API_KEY')),
        'model': 'lite'
    })


@ai_bp.route('/config', methods=['PUT'])
@require_token
def update_ai_config(current_user):
    """更新AI配置（仅管理员可访问）"""
    if current_user.user_type != 3:
        return api_error('无权限', 403)

    data = request.get_json()
    config = current_app.config

    if 'http_password' in data:
        config['XFYUN_HTTP_PASSWORD'] = data['http_password']
    if 'appid' in data:
        config['XFYUN_APPID'] = data['appid']

    return api_response(message='配置更新成功')