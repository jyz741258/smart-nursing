# -*- coding: utf-8 -*-
"""添加家属绑定老人字段"""
from app import create_app
from app.extensions import db

app = create_app('default')

def add_binding_elder_field():
    """为家属用户添加绑定老人字段"""
    with app.app_context():
        # 检查表结构
        from sqlalchemy import inspect, text

        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('users')]

        if 'binding_elder_id' not in columns:
            # 添加新列
            db.session.execute(text('ALTER TABLE users ADD COLUMN binding_elder_id INTEGER'))
            db.session.commit()
            print("成功添加 binding_elder_id 字段到 users 表")
        else:
            print("binding_elder_id 字段已存在")

if __name__ == '__main__':
    add_binding_elder_field()
