import sqlite3

db_path = r'c:\Users\Jyz74\smart-nursing\backend\instance\smart_nursing.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 查询所有订单
c.execute("SELECT id, status, actual_amount, total_amount, order_no FROM orders ORDER BY id DESC")
rows = c.fetchall()

# 写入结果文件
with open(r'c:\Users\Jyz74\smart-nursing\backend\orders_data.txt', 'w', encoding='utf-8') as f:
    f.write(f"总订单数: {len(rows)}\n\n")
    f.write("=== 订单详情 ===\n")
    status_map = {0: '已取消', 1: '待支付', 2: '待服务', 3: '服务中', 4: '已完成', 5: '已退款'}
    for row in rows:
        status_name = status_map.get(row[1], '未知')
        f.write(f"ID={row[0]}, status={row[1]}({status_name}), actual={row[2]}, total={row[3]}, order_no={row[4]}\n")
    
    f.write("\n=== 按状态统计 ===\n")
    c.execute("SELECT status, COUNT(*), SUM(actual_amount) FROM orders GROUP BY status ORDER BY status")
    for status, cnt, total_amt in c.fetchall():
        name = status_map.get(status, '未知')
        f.write(f"status={status}({name}): {cnt}条, 总金额={total_amt}\n")

conn.close()
print("数据已写入 orders_data.txt")
