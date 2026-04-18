"""直接读取SQLite数据库"""
import sqlite3

db_file = r'c:\Users\Jyz74\smart-nursing\backend\instance\smart_nursing.db'
conn = sqlite3.connect(db_file)
c = conn.cursor()

print("=== 检查orders表数据 ===")
c.execute("SELECT * FROM orders")
rows = c.fetchall()
print(f"orders表列数: {len(rows[0]) if rows else 0}")
print(f"orders表记录数: {len(rows)}")
if rows:
    print("\n每条订单的字段:")
    for row in rows[:3]:
        print(row)

# 查看表结构
print("\n=== 表结构 ===")
c.execute("PRAGMA table_info(orders)")
for col in c.fetchall():
    print(f"  {col[1]}: {col[2]}")

conn.close()
