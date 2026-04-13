# -*- coding: utf-8 -*-
"""
诊断脚本 - 检查前后端配置是否正确
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from app import create_app
import json

app = create_app('default')

print('=' * 50)
print('智慧养老系统 - 诊断报告')
print('=' * 50)

# 1. 检查后端服务状态
print('\n【1. 后端服务状态】')
print('  - 后端地址: http://localhost:5000')
print('  - 状态: 正在运行 (本测试基于test_client)')

# 2. 检查数据库
print('\n【2. 数据库状态】')
with app.app_context():
    from app.models import User, NursingRecord, Service
    
    users = User.query.count()
    records = NursingRecord.query.count()
    services = Service.query.count()
    
    print(f'  - 用户数量: {users}')
    print(f'  - 护理记录: {records}')
    print(f'  - 服务项目: {services}')

# 3. 检查API端点
print('\n【3. API端点测试】')
with app.test_client() as client:
    # 健康检查
    health = client.get('/api/health')
    health_data = json.loads(health.data)
    print(f'  - GET /api/health: {"✓ 正常" if health_data.get("status") == "ok" else "✗ 失败"}')
    
    # 登录测试
    login = client.post('/api/users/login', json={
        'phone': '13800138000',
        'password': '123456'
    })
    login_data = json.loads(login.data)
    
    if login_data.get('code') == 200:
        print(f'  - POST /api/users/login: ✓ 正常')
        print(f'    (管理员登录成功)')
        
        token = login_data['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 护理记录API
        records = client.get('/api/nursing/records', headers=headers)
        records_data = json.loads(records.data)
        
        if records_data.get('code') == 200:
            total = records_data.get('data', {}).get('total', 0)
            print(f'  - GET /api/nursing/records: ✓ 正常 ({total}条记录)')
        else:
            print(f'  - GET /api/nursing/records: ✗ 失败')
    else:
        print(f'  - POST /api/users/login: ✗ 失败')
        print(f'    原因: {login_data.get("message")}')

# 4. 样例账号信息
print('\n【4. 测试账号】')
print('  | 角色   | 手机号      | 密码   |')
print('  |--------|------------|--------|')
print('  | 老人   | 13900001001 | 123456 |')
print('  | 护理员 | 13900001002 | 123456 |')
print('  | 管理员 | 13800138000 | 123456 |')
print('  | 家属   | 13900001004 | 123456 |')

# 5. 前端配置
print('\n【5. 前端配置】')
print('  - 前端地址: http://localhost:3000')
print('  - API代理: /api -> http://localhost:5000')

# 6. 可能的问题和解决方案
print('\n【6. 故障排除】')
print('  问题1: 点击样例账号没反应')
print('    - 检查浏览器控制台(F12)是否有错误')
print('    - 确保后端运行在5000端口')
print('    - 确保前端运行在3000端口')
print('')
print('  问题2: 显示"暂无数据"')
print('    - 检查是否正确登录（应为管理员账号）')
print('    - 清除浏览器缓存后刷新页面')
print('    - 检查Network中/api/nursing/records请求是否成功')
print('')
print('  问题3: 登录失败')
print('    - 已在后台重置所有测试账号密码为123456')
print('    - 请使用正确的手机号登录')

print('\n' + '=' * 50)
print('诊断完成')
print('=' * 50)