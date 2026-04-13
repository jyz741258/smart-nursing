# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

from app import create_app
from app.extensions import db
from app.models import User

app = create_app('default')

with app.app_context():
    # 重置管理员密码
    admin = User.query.filter_by(phone='13800138000').first()
    if admin:
        admin.set_password('123456')
        db.session.commit()
        print('管理员密码已重置为: 123456')
        print(f'管理员信息: ID={admin.id}, Phone={admin.phone}, Type={admin.user_type}')
    else:
        print('管理员不存在')
    
    # 验证
    admin = User.query.filter_by(phone='13800138000').first()
    print(f'验证密码: {admin.check_password("123456")}')