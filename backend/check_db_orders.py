"""统计数据库中的所有订单"""
import sqlite3

db_path = r'c:\Users\Jyz74\smart-nursing\backend\instance\smart_nursing.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 总订单数
cursor.execute("SELECT COUNT(*) FROM orders")
total = cursor.fetchone()[0]
print(f"【数据库】orders表总记录数: {total}")

# 按状态统计
cursor.execute("SELECT status, COUNT(*) FROM orders GROUP BY status ORDER BY status")
print("\n【数据库】按状态统计:")
status_map = {0: '已取消', 1: '待支付', 2: '待服务', 3: '服务中', 4: '已完成', 5: '已退款'}
for status, cnt in cursor.fetchall():
    name = status_map.get(status, '未知')
    print(f"  status={status}({name}): {cnt} 条")

# 查看所有订单的ID和状态
cursor.execute("SELECT id, status, order_no FROM orders ORDER BY id DESC")
rows = cursor.fetchall()
print(f"\n【数据库】所有订单详情（共{len(rows)}条）:")
for row in rows:
    status_name = status_map.get(row[1], '未知')
    print(f"  ID={row[0]}, status={row[1]}({status_name}), order_no={row[2]}")

conn.close()
input("\n按回车键退出...")
