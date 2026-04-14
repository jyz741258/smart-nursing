# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

from app import create_app
from app.models import Service

app = create_app('default')

with app.app_context():
    services = Service.query.all()
    print(f'服务总数: {len(services)}')
    for s in services:
        req = s.requirements
        req_preview = req[:50] if req else '空'
        print(f'  {s.name}: requirements={req_preview}...')
    
    # 检查第一个服务的完整数据
    if services:
        print('\n第一个服务的完整数据:')
        s = services[0]
        print(f'  name: {s.name}')
        print(f'  price: {s.price}')
        print(f'  requirements: {s.requirements}')