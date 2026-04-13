# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

from app import create_app
import json

app = create_app('default')

# 测试客户端
with app.test_client() as client:
    # 1. 先登录获取token
    login_response = client.post('/api/users/login', 
        json={'phone': '13800138000', 'password': '123456'})
    login_data = json.loads(login_response.data)
    print('登录结果:', login_data.get('code'), login_data.get('message'))
    
    if login_data.get('code') == 200:
        token = login_data['data']['token']
        print(f'Token获取成功')
        
        # 2. 使用token访问护理记录API
        headers = {'Authorization': f'Bearer {token}'}
        records_response = client.get('/api/nursing/records', headers=headers)
        records_data = json.loads(records_response.data)
        
        print('\n=== 护理记录API响应 ===')
        print(f'Code: {records_data.get("code")}')
        print(f'Message: {records_data.get("message")}')
        print(f'Total: {records_data.get("data", {}).get("total")}')
        print(f'Items count: {len(records_data.get("data", {}).get("items", []))}')
        
        if records_data.get('data', {}).get('items'):
            print('\n第一条记录:')
            item = records_data['data']['items'][0]
            for key, value in item.items():
                print(f'  {key}: {value}')
    else:
        print('登录失败，无法继续测试')