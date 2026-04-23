# -*- coding: utf-8 -*-
"""数据库迁移脚本 - 为notifications表添加order_id字段"""
from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app('default')


def migrate_notifications_table():
    """迁移通知表，添加order_id字段"""
    with app.app_context():
        conn = db.engine.connect()
        
        # 检查表是否存在
        result = conn.execute(text("PRAGMA table_info(notifications)"))
        columns = [row[1] for row in result.fetchall()]
        
        print("Current notifications table columns:", columns)
        
        # 检查并添加order_id字段
        if "order_id" not in columns:
            try:
                sql = "ALTER TABLE notifications ADD COLUMN order_id INTEGER"
                conn.execute(text(sql))
                conn.commit()
                print("Added field: order_id")
            except Exception as e:
                print(f"Failed to add field order_id: {e}")
        else:
            print("Field already exists: order_id")
        
        conn.close()
        print("\nDatabase migration completed!")


if __name__ == '__main__':
    migrate_notifications_table()
