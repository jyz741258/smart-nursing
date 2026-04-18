"""读取SQLite数据库中的orders表数据"""
import sqlite3
import json

db_path = r'c:\Users\Jyz74\smart-nursing\backend\instance\smart_nursing.db'

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 查询orders表
cursor.execute("SELECT * FROM orders LIMIT 5")
rows = cursor.fetchall()

print(f"查询到 {len(rows)} 条订单记录:")
for row in rows:
    print(dict(row))

conn.close()
