import sqlite3
import sys

# 使用绝对路径
db_path = r'C:\Users\Jyz74\smart-nursing\backend\instance\smart_nursing.db'

try:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # 查询
    c.execute("SELECT COUNT(*) as total FROM orders")
    total_row = c.fetchone()
    total = total_row[0] if total_row else 0
    
    c.execute("SELECT status, COUNT(*) as cnt FROM orders GROUP BY status ORDER BY status")
    stats = c.fetchall()
    
    c.execute("SELECT id, status, actual_amount, total_amount FROM orders ORDER BY id DESC LIMIT 10")
    orders = c.fetchall()
    
    conn.close()
    
    # 输出到文件（避免编码问题）
    with open('C:/Users/Jyz74/smart-nursing/backend/db_stats.txt', 'w', encoding='utf-8') as f:
        f.write(f"总订单数: {total}\n")
        f.write(f"状态统计: {stats}\n")
        f.write("最近10条订单:\n")
        for o in orders:
            f.write(f"  ID={o[0]}, status={o[1]}, actual={o[2]}, total={o[3]}\n")
    
    print(f"总订单数: {total}")
    print(f"状态统计: {stats}")
    print("详情已写入 db_stats.txt")
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
