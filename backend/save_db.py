"""查询数据库并写入文件（避免编码问题）"""
import sqlite3

db = r'C:\Users\Jyz74\smart-nursing\backend\instance\smart_nursing.db'
conn = sqlite3.connect(db)
c = conn.cursor()

# 查询
c.execute("SELECT COUNT(*) FROM orders")
total = c.fetchone()[0]

c.execute("SELECT status, COUNT(*) FROM orders GROUP BY status ORDER BY status")
stats = c.fetchall()

c.execute("SELECT id, status, order_no, actual_amount FROM orders ORDER BY id DESC LIMIT 20")
orders = c.fetchall()

conn.close()

# 写入纯文本文件
with open(r'C:\Users\Jyz74\smart-nursing\backend\db_result.txt', 'w', encoding='utf-8') as f:
    f.write(f"总订单数: {total}\n\n")
    f.write("=== 状态统计 ===\n")
    status_names = {0:'已取消', 1:'待支付', 2:'待服务', 3:'服务中', 4:'已完成', 5:'已退款'}
    for status, cnt in stats:
        name = status_names.get(status, '未知')
        f.write(f"  status={status}({name}): {cnt}条\n")
    f.write("\n=== 最近20条订单 ===\n")
    for row in orders:
        f.write(f"  ID={row[0]}, status={row[1]}, order_no={row[2]}, actual={row[3]}\n")

print("数据已写入 db_result.txt")
