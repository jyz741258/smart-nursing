"""
测试讯飞星火 HTTP 接口 - 直接请求验证
"""
import requests
import json

# 序号1应用的配置
APPID = "10b602f2"
HTTP_PASSWORD = "COJUnmEJCpsUJKqlVXIL:ScBUnadIeSbLAlpAIJhy"

def test_http_api():
    print("=" * 60)
    print("讯飞星火 HTTP API 测试")
    print("=" * 60)

    url = "https://spark-api-open.xf-yun.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {HTTP_PASSWORD}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "lite",
        "messages": [
            {"role": "system", "content": "你是一个助手"},
            {"role": "user", "content": "你好"}
        ],
        "temperature": 0.5,
        "max_tokens": 10
    }

    print(f"\n请求URL: {url}")
    print(f"Authorization: Bearer {HTTP_PASSWORD[:20]}...")
    print(f"\n请求体: {json.dumps(payload, ensure_ascii=False)[:100]}...")

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应体: {response.text[:500]}")

        if response.status_code == 200:
            result = response.json()
            if 'choices' in result:
                reply = result['choices'][0]['message']['content']
                print(f"\n✅ 成功！回复: {reply}")
            else:
                print(f"\n⚠️ 200但格式异常: {json.dumps(result, ensure_ascii=False)[:300]}")
        else:
            print(f"\n❌ 失败")

    except Exception as e:
        print(f"\n❌ 异常: {e}")

if __name__ == "__main__":
    test_http_api()
