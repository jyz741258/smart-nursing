"""查询数据库中订单的实际金额"""
import sqlite3

db_path = r'c:\Users\Jyz74\smart-nursing\backend\instance\smart_nursing.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=== 所有订单的ID、状态、actual_amount、total_amount ===")
cursor.execute("SELECT id, status, actual_amount, total_amount, order_no FROM orders ORDER BY id DESC")
rows = cursor.fetchall()
print(f"总订单数: {len(rows)}")
for row in rows:
    print(f"  ID={row['id']}, status={row['status']}, actual_amount={row['actual_amount']}, total_amount={row['total_amount']}, order_no={row['order_no']}")

conn.close()
