# -*- coding: utf-8 -*-
"""测试API返回"""
import requests

# 先登录获取token
login_resp = requests.post('http://localhost:5000/api/users/login', json={
    'phone': '13800138000',
    'password': 'admin123'
})
print('登录响应:', login_resp.json())

token = login_resp.json()['data']['token']

# 获取老人列表
headers = {'Authorization': f'Bearer {token}'}
elder_resp = requests.get('http://localhost:5000/api/users/elder/list', headers=headers)
print('\n老人列表状态码:', elder_resp.status_code)
print('老人列表原始响应:', elder_resp.text if elder_resp.text else '(空响应)')

if elder_resp.text:
    print('老人列表响应:', elder_resp.json())