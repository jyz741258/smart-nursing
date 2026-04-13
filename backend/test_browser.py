# -*- coding: utf-8 -*-
"""
模拟真实浏览器请求测试
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import requests
import json

BASE_URL = "http://localhost:5000"

print("=" * 60)
print("智慧养老系统 - 真实浏览器模拟测试")
print("=" * 60)

# 1. 测试健康检查
print("\n【1. 健康检查】")
try:
    resp = requests.get(f"{BASE_URL}/api/health", timeout=5)
    print(f"    状态码: {resp.status_code}")
    print(f"    响应: {resp.json()}")
except Exception as e:
    print(f"    错误: {e}")
    print("    后端可能未启动！")
    sys.exit(1)

# 2. 测试登录
print("\n【2. 管理员登录】")
try:
    login_data = {
        "phone": "13800138000",
        "password": "123456"
    }
    resp = requests.post(f"{BASE_URL}/api/users/login", json=login_data, timeout=5)
    result = resp.json()
    print(f"    状态码: {resp.status_code}")
    print(f"    响应: {result}")
    
    if result.get("code") == 200:
        token = result["data"]["token"]
        print(f"    Token获取成功: {token[:30]}...")
    else:
        print(f"    登录失败: {result.get('message')}")
        sys.exit(1)
except Exception as e:
    print(f"    错误: {e}")
    sys.exit(1)

# 3. 测试护理记录API
print("\n【3. 获取护理记录】")
try:
    headers = {"Authorization": f"Bearer {token}"}
    params = {"page": 1, "page_size": 10}
    resp = requests.get(f"{BASE_URL}/api/nursing/records", 
                       headers=headers, params=params, timeout=5)
    result = resp.json()
    print(f"    状态码: {resp.status_code}")
    print(f"    code: {result.get('code')}")
    print(f"    message: {result.get('message')}")
    print(f"    total: {result.get('data', {}).get('total')}")
    print(f"    items数量: {len(result.get('data', {}).get('items', []))}")
    
    if result.get("data", {}).get("items"):
        print("\n    第一条记录预览:")
        item = result["data"]["items"][0]
        for k, v in item.items():
            print(f"      {k}: {v}")
except Exception as e:
    print(f"    错误: {e}")

# 4. 测试服务列表API
print("\n【4. 获取服务列表】")
try:
    resp = requests.get(f"{BASE_URL}/api/services", params={"page": 1, "page_size": 10}, timeout=5)
    result = resp.json()
    print(f"    状态码: {resp.status_code}")
    print(f"    total: {result.get('data', {}).get('total')}")
    print(f"    items数量: {len(result.get('data', {}).get('items', []))}")
except Exception as e:
    print(f"    错误: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
print("\n提示：")
print("1. 如果以上测试全部通过，说明后端API正常")
print("2. 如果浏览器仍显示暂无数据，请检查前端是否正确连接")
print("3. 确保前端运行在 http://localhost:3000")
print("4. 清除浏览器缓存后刷新页面")