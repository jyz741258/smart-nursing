"""检查数据库结构"""
import sqlite3

db_path = r'C:\Users\Jyz74\smart-nursing\backend\smart_nursing.db'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 列出所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"数据库中的表: {[t[0] for t in tables]}")
    
    if tables:
        for table in tables:
            table_name = table[0]
            print(f"\n=== {table_name} 表结构 ===")
            cursor.execute(f"PRAGMA table_info('{table_name}')")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  {col[1]}: {col[2]}")
    
    conn.close()
except Exception as e:
    print(f'查询失败: {e}')
    import traceback
    traceback.print_exc()