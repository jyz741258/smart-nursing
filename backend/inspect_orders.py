"""查询订单数据库中的实际数据"""
import sqlite3

db_path = r'c:\Users\Jyz74\smart-nursing\backend\instance\smart_nursing.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=== 1. 订单总数 ===")
cursor.execute("SELECT COUNT(*) as cnt FROM orders")
total = cursor.fetchone()['cnt']
print(f"总订单数: {total}")

print("\n=== 2. 订单状态分布 ===")
cursor.execute("SELECT status, COUNT(*) as cnt FROM orders GROUP BY status ORDER BY status")
for row in cursor.fetchall():
    status_name = {0:'已取消', 1:'待支付', 2:'待服务', 3:'服务中', 4:'已完成', 5:'已退款'}.get(row['status'], '未知')
    print(f"  状态 {row['status']} ({status_name}): {row['cnt']} 条")

print("\n=== 3. 订单金额统计（按状态） ===")
cursor.execute("SELECT status, SUM(actual_amount) as total, COUNT(*) as cnt FROM orders GROUP BY status ORDER BY status")
for row in cursor.fetchall():
    status_name = {0:'已取消', 1:'待支付', 2:'待服务', 3:'服务中', 4:'已完成', 5:'已退款'}.get(row['status'], '未知')
    print(f"  状态 {row['status']} ({status_name}): 共{row['cnt']}条, 金额总和={row['total']}")

print("\n=== 4. 销售额统计（状态2和4）===")
cursor.execute("SELECT SUM(actual_amount) as sales FROM orders WHERE status IN (2, 4)")
sales = cursor.fetchone()['sales']
print(f"待服务+已完成订单总金额: {sales}")

print("\n=== 5. 前5条订单详情 ===")
cursor.execute("SELECT id, order_no, status, actual_amount, total_amount, created_at FROM orders ORDER BY id DESC LIMIT 5")
rows = cursor.fetchall()
for row in rows:
    status_name = {0:'已取消', 1:'待支付', 2:'待服务', 3:'服务中', 4:'已完成', 5:'已退款'}.get(row['status'], '未知')
    print(f"  ID:{row['id']}, 状态:{row['status']}({status_name}), actual_amount={row['actual_amount']}, total_amount={row['total_amount']}, 时间:{row['created_at']}")

conn.close()
