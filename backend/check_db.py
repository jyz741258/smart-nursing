# -*- coding: utf-8 -*-
"""检查数据库表结构"""
from app import create_app
from app.extensions import db

app = create_app('default')

def check_db():
    with app.app_context():
        # 查看数据库路径
        print('数据库路径:', db.engine.url)
        
        # 查看所有表
        result = db.session.execute(db.text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result]
        print('所有表:', tables)
        
        # 查看users表结构
        if 'users' in tables:
            result = db.session.execute(db.text("PRAGMA table_info(users)"))
            columns = [(row[1], row[2]) for row in result]
            print('users表列:', columns)

if __name__ == '__main__':
    check_db()