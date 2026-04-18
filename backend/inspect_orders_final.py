"""查询所有订单的详细信息"""
import sqlite3

db_path = r'c:\Users\Jyz74\smart-nursing\backend\instance\smart_nursing.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=== 1. 订单总数 ===")
cursor.execute("SELECT COUNT(*) as cnt FROM orders")
total = cursor.fetchone()['cnt']
print(f"数据库中总订单数: {total}")

print("\n=== 2. 按状态统计 ===")
cursor.execute("SELECT status, COUNT(*) as cnt FROM orders GROUP BY status ORDER BY status")
status_map = {0: '已取消', 1: '待支付', 2: '待服务', 3: '服务中', 4: '已完成', 5: '已退款'}
for row in cursor.fetchall():
    name = status_map.get(row['status'], '未知')
    print(f"  status={row['status']}({name}): {row['cnt']} 条")

print("\n=== 3. 所有订单详情（ID, 状态, 金额, 创建时间）===")
cursor.execute("SELECT id, order_no, status, actual_amount, total_amount, created_at FROM orders ORDER BY id DESC")
rows = cursor.fetchall()
print(f"总订单数: {len(rows)}")
for row in rows:
    status_name = status_map.get(row['status'], '未知')
    print(f"  ID={row['id']}, 状态={row['status']}({status_name}), actual_amount={row['actual_amount']}, total_amount={row['total_amount']}, 时间={row['created_at']}")

conn.close()
input("\n按回车键退出...")
