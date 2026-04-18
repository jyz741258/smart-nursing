import sqlite3

db = r'C:\Users\Jyz74\smart-nursing\backend\instance\smart_nursing.db'
conn = sqlite3.connect(db)
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM orders")
total = c.fetchone()[0]
print(f"总订单数: {total}")

c.execute("SELECT status, COUNT(*) FROM orders GROUP BY status ORDER BY status")
print("状态统计:")
for row in c.fetchall():
    print(f"  status={row[0]}: {row[1]}条")

c.execute("SELECT id, status FROM orders ORDER BY id DESC LIMIT 10")
print("最近10条订单ID和状态:")
for row in c.fetchall():
    print(f"  ID={row[0]}, status={row[1]}")

conn.close()
