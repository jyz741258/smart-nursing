# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

from app import create_app
from app.extensions import db
from app.models import User

app = create_app('default')

with app.app_context():
    print('=== 用户列表 ===')
    users = User.query.all()
    for u in users:
        print(f'ID:{u.id}, Phone:{u.phone}, Username:{u.username}, RealName:{u.real_name}, Type:{u.user_type}')
        # 测试密码
        if u.check_password('123456'):
            print(f'  -> 密码 123456 正确')
        else:
            print(f'  -> 密码 123456 错误')