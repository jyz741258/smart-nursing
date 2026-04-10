# -*- coding: utf-8 -*-
"""添加address字段到users表"""
from app import create_app
from app.extensions import db
import sqlite3

app = create_app('default')

def add_address_column():
    """添加address列"""
    db_path = 'smart_nursing.db'
    
    with app.app_context():
        # 获取数据库路径
        with app.app_context():
            engine = db.engine
            db_url = str(engine.url)
            
            # 连接到数据库
            conn = sqlite3.connect(db_path.split('/')[-1] if '/' not in db_path else db_path)
            cursor = conn.cursor()
            
            # 检查列是否存在
            cursor.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'address' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN address VARCHAR(255)")
                conn.commit()
                print('已添加 address 列到 users 表')
            else:
                print('address 列已存在')
            
            conn.close()

if __name__ == '__main__':
    add_address_column()
