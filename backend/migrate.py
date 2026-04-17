"""数据库迁移脚本 - 添加缺失的列"""
import sqlite3

# 数据库实际路径
db_path = r'C:\Users\Jyz74\smart-nursing\backend\instance\smart_nursing.db'

print(f"数据库路径: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查 orders 表结构
    cursor.execute("PRAGMA table_info('orders')")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"当前 orders 表的列: {columns}")
    
    # 需要添加的列
    columns_to_add = [
        ('pay_transaction_id', 'VARCHAR(64)'),
        ('service_start_time', 'DATETIME'),
        ('service_end_time', 'DATETIME'),
        ('completion_time', 'DATETIME'),
        ('cancel_reason', 'VARCHAR(255)'),
        ('cancel_time', 'DATETIME')
    ]
    
    for col_name, col_type in columns_to_add:
        if col_name not in columns:
            sql = f"ALTER TABLE orders ADD COLUMN {col_name} {col_type}"
            cursor.execute(sql)
            print(f"已添加列: {col_name}")
        else:
            print(f"列已存在: {col_name}")
    
    conn.commit()
    conn.close()
    print('数据库表已更新完成')
except Exception as e:
    print(f'更新失败: {e}')
    import traceback
    traceback.print_exc()