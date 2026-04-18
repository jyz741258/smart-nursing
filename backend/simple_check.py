"""读取数据库并输出纯文本"""
import sqlite3

db = r'c:\Users\Jyz74\smart-nursing\backend\instance\smart_nursing.db'
conn = sqlite3.connect(db)
c = conn.cursor()

# 统计总数
c.execute("SELECT COUNT(*) FROM orders")
total = c.fetchone()[0]

# 按状态统计
c.execute("SELECT status, COUNT(*) FROM orders GROUP BY status")
stats = c.fetchall()

# 订单详情
c.execute("SELECT id, status, actual_amount, total_amount FROM orders ORDER BY id DESC LIMIT 10")
orders = c.fetchall()

conn.close()

# 输出纯文本（无中文编码问题）
print("TOTAL:", total)
print("STATS:", stats)
print("ORDERS:")
for o in orders:
    print(o)
