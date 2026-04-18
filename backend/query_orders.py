"""查询数据库并输出到控制台（使用ASCII避免编码问题）"""
import sqlite3

db = r'c:\Users\Jyz74\smart-nursing\backend\instance\smart_nursing.db'
conn = sqlite3.connect(db)
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM orders")
total = c.fetchone()[0]
print("TOTAL_ORDERS =", total)

c.execute("SELECT status, COUNT(*) FROM orders GROUP BY status ORDER BY status")
print("STATS =", c.fetchall())

c.execute("SELECT id, status, actual_amount FROM orders ORDER BY id DESC LIMIT 10")
print("RECENT_ORDERS =", c.fetchall())

conn.close()
