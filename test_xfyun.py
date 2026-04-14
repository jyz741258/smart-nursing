"""
讯飞星火API密钥验证脚本
直接测试WebSocket连接，输出详细信息
"""
import base64
import hashlib
import hmac
from datetime import datetime
from urllib.parse import quote
import websocket
import json

# 从.env读取的配置
APPID = "10b602f2"
API_KEY = "6bd825ec32372edb8d788cad5e9d4127"
API_SECRET = "YzhhZTFjMjcxZGVlMzM0NzI4MmU2MzEw"

def generate_url():
    """生成鉴权URL"""
    host = "spark-api.xf-yun.com"
    path = "/v1.1/chat"

    now = datetime.utcnow()
    date = now.strftime('%a, %d %b %Y %H:%M:%S GMT')

    signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"

    signature_sha = hmac.new(
        API_SECRET.encode('utf-8'),
        signature_origin.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    signature_sha_base64 = base64.b64encode(signature_sha).decode('utf-8')

    authorization_origin = (
        f'api_key="{API_KEY}", algorithm="hmac-sha256", '
        f'headers="host date request-line", signature="{signature_sha_base64}"'
    )
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')

    wss_url = f"wss://{host}{path}"
    params = f"appid={APPID}&date={quote(date, safe='')}&host={host}&signature={quote(authorization, safe='')}"

    return f"{wss_url}?{params}"

def test_connection():
    """测试WebSocket连接"""
    print("=" * 60)
    print("讯飞星火API密钥测试")
    print("=" * 60)

    print(f"\nAPPID: {APPID}")
    print(f"API_KEY: {API_KEY[:8]}...{API_KEY[-4:]}")
    print(f"API_SECRET: {API_SECRET[:8]}...{API_SECRET[-4:]}")

    url = generate_url()
    print(f"\n生成的URL:\n{url[:100]}...")

    print("\n尝试连接...")
    ws = websocket.WebSocketApp(
        url,
        on_message=lambda ws, msg: print(f"收到消息: {msg[:200]}..."),
        on_error=lambda ws, err: print(f"错误: {err}"),
        on_close=lambda ws, code, msg: print(f"连接关闭: code={code}, msg={msg}"),
    )
    ws.on_open = lambda ws: print("连接成功!")
    ws.run_forever(ping_timeout=5)

if __name__ == "__main__":
    test_connection()
