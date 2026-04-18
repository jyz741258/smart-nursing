import sqlite3

db = r'c:\Users\Jyz74\smart-nursing\backend\instance\smart_nursing.db'
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute("SELECT COUNT(*) FROM orders")
print("Orders count:", c.fetchone()[0])
c.execute("SELECT id, status, actual_amount FROM orders LIMIT 3")
for row in c.fetchall():
    print(row)
conn.close()
