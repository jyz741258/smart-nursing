# -*- coding: utf-8 -*-
import sqlite3
import sys

# 设置输出编码
sys.stdout.reconfigure(encoding='utf-8')

db_path = r'c:\Users\Jyz74\smart-nursing\backend\instance\smart_nursing.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("=== 数据库订单统计 ===")
c.execute("SELECT COUNT(*) FROM orders")
total = c.fetchone()[0]
print(f"总订单数: {total}")

c.execute("SELECT status, COUNT(*) FROM orders GROUP BY status ORDER BY status")
print("\n按状态统计:")
status_names = {0: '已取消', 1: '待支付', 2: '待服务', 3: '服务中', 4: '已完成', 5: '已退款'}
for status, cnt in c.fetchall():
    name = status_names.get(status, '未知')
    print(f"  status={status}({name}): {cnt}条")

c.execute("SELECT id, status, actual_amount, total_amount FROM orders ORDER BY id DESC LIMIT 10")
print("\n最近10条订单:")
for row in c.fetchall():
    name = status_names.get(row[1], '未知')
    print(f"  ID={row[0]}, status={row[1]}({name}), actual={row[2]}, total={row[3]}")

conn.close()
input("\n按回车退出...")
