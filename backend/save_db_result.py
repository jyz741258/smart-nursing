import sqlite3

db_path = r'c:\Users\Jyz74\smart-nursing\backend\instance\smart_nursing.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 查询
c.execute("SELECT COUNT(*) FROM orders")
total = c.fetchone()[0]

c.execute("SELECT status, COUNT(*) FROM orders GROUP BY status")
stats = c.fetchall()

c.execute("SELECT id, status, actual_amount FROM orders ORDER BY id DESC LIMIT 5")
recent = c.fetchall()

conn.close()

# 写入文件（用json避免编码问题）
import json
data = {
    'total': total,
    'stats': stats,
    'recent': recent
}
with open('db_result.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("OK")
