# -*- coding: utf-8 -*-
"""数据库迁移脚本 - 添加缺失的订单字段"""
from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app('default')


def migrate_orders_table():
    """迁移订单表，添加缺失的字段"""
    with app.app_context():
        conn = db.engine.connect()
        
        # 检查表是否存在
        result = conn.execute(text("PRAGMA table_info(orders)"))
        columns = [row[1] for row in result.fetchall()]
        
        print("Current orders table columns:", columns)
        
        # 需要添加的字段
        migrations = [
            ("nurse_id", "INTEGER"),
            ("order_time", "DATETIME"),
            ("notes", "VARCHAR(500)"),
            ("created_by", "INTEGER")
        ]
        
        for field_name, field_type in migrations:
            if field_name not in columns:
                try:
                    sql = f"ALTER TABLE orders ADD COLUMN {field_name} {field_type}"
                    conn.execute(text(sql))
                    conn.commit()
                    print(f"Added field: {field_name}")
                except Exception as e:
                    print(f"Failed to add field {field_name}: {e}")
            else:
                print(f"Field already exists: {field_name}")
        
        conn.close()
        print("\nDatabase migration completed!")


if __name__ == '__main__':
    migrate_orders_table()
