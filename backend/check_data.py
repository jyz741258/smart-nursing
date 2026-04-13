# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

from app import create_app
from app.extensions import db
from app.models import NursingRecord, User

app = create_app('default')

with app.app_context():
    print('=== 检查护理记录数据 ===')
    records = NursingRecord.query.all()
    print(f'总数: {len(records)}')
    
    # 检查老人是否存在
    for r in records[:3]:
        elder = User.query.get(r.elder_id)
        elder_name = elder.real_name if elder else "不存在"
        staff = User.query.get(r.staff_id)
        staff_name = staff.real_name if staff else "不存在"
        print(f'记录ID:{r.id}, elder_id:{r.elder_id}, 老人:{elder_name}, 护理人员:{staff_name}')
        print(f'  类型:{r.nursing_type}, 描述:{r.description[:30] if r.description else None}...')
    
    # 模拟后端返回的数据格式
    print('\n=== 模拟API返回 ===')
    items = [{
        'id': r.id,
        'elder_id': r.elder_id,
        'elder_name': r.elder.name if r.elder else None,
        'nursing_type': r.nursing_type,
        'nursing_type_name': r.get_nursing_type_display(),
        'description': r.description,
        'status': r.status,
        'status_name': r.get_status_display(),
        'created_at': r.created_at.isoformat() if r.created_at else None
    } for r in records[:2]]
    
    print(f'Items: {len(items)}')
    for item in items:
        print(f'  {item}')