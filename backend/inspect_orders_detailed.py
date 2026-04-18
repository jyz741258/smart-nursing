"""检查数据库中订单的状态和金额"""
import sqlite3

db_path = r'c:\Users\Jyz74\smart-nursing\backend\instance\smart_nursing.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=== 所有订单的状态和金额 ===")
cursor.execute("SELECT id, order_no, status, actual_amount, total_amount, created_at FROM orders ORDER BY id DESC")
rows = cursor.fetchall()
print(f"总订单数: {len(rows)}")
for row in rows:
    status_name = {0:'已取消', 1:'待支付', 2:'待服务', 3:'服务中', 4:'已完成', 5:'已退款'}.get(row['status'], '未知')
    print(f"  ID={row['id']}, 状态={row['status']}({status_name}), actual_amount={row['actual_amount']}, total_amount={row['total_amount']}")

print("\n=== 按状态统计订单数和金额 ===")
cursor.execute("SELECT status, COUNT(*) as cnt, SUM(actual_amount) as total FROM orders GROUP BY status ORDER BY status")
for row in cursor.fetchall():
    status_name = {0:'已取消', 1:'待支付', 2:'待服务', 3:'服务中', 4:'已完成', 5:'已退款'}.get(row['status'], '未知')
    print(f"  状态 {row['status']}({status_name}): {row['cnt']}条, 总金额={row['total']}")

conn.close()
