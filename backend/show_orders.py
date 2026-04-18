import sqlite3

db = r'c:\Users\Jyz74\smart-nursing\backend\instance\smart_nursing.db'
conn = sqlite3.connect(db)
c = conn.cursor()

print("=== 订单总数 ===")
c.execute("SELECT COUNT(*) FROM orders")
print(c.fetchone()[0])

print("\n=== 订单状态统计 ===")
c.execute("SELECT status, COUNT(*) FROM orders GROUP BY status ORDER BY status")
for row in c.fetchall():
    print(row)

print("\n=== 最近5条订单（ID,状态,actual_amount）===")
c.execute("SELECT id, status, actual_amount FROM orders ORDER BY id DESC LIMIT 5")
for row in c.fetchall():
    print(row)

conn.close()
