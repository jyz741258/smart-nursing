# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

from app import create_app
import json

app = create_app('default')

print('=== 完整流程测试 ===')

# 测试客户端
with app.test_client() as client:
    # 1. 测试所有样例账号登录
    test_users = [
        ('老人', '13900001001', '123456'),
        ('护理员', '13900001002', '123456'),
        ('管理员', '13800138000', '123456'),
        ('家属', '13900001004', '123456'),
    ]
    
    for role, phone, password in test_users:
        login_response = client.post('/api/users/login', 
            json={'phone': phone, 'password': password})
        login_data = json.loads(login_response.data)
        
        print(f'\n{role}账号 ({phone}):')
        print(f'  登录结果: {"成功" if login_data.get("code") == 200 else "失败"}')
        
        if login_data.get('code') == 200:
            token = login_data['data']['token']
            print(f'  Token获取: 成功')
            
            # 测试护理记录API
            headers = {'Authorization': f'Bearer {token}'}
            records_response = client.get('/api/nursing/records', headers=headers)
            records_data = json.loads(records_response.data)
            
            if records_data.get('code') == 200:
                total = records_data.get('data', {}).get('total', 0)
                print(f'  护理记录: {total} 条')
            else:
                print(f'  护理记录: 获取失败 - {records_data.get("message")}')
        else:
            print(f'  登录失败: {login_data.get("message")}')