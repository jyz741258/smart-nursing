"""使用简单编码查询数据库"""
import sys
import sqlite3

# 数据库路径
db_path = r'c:\Users\Jyz74\smart-nursing\backend\instance\smart_nursing.db'

try:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    print("=== 数据库订单统计 ===")
    
    # 总订单数
    c.execute("SELECT COUNT(*) as cnt FROM orders")
    total = c.fetchone()['cnt']
    print(f"总订单数: {total}")
    
    # 按状态统计
    c.execute("SELECT status, COUNT(*) as cnt FROM orders GROUP BY status ORDER BY status")
    print("\n按状态分布:")
    status_names = {0: '已取消', 1: '待支付', 2: '待服务', 3: '服务中', 4: '已完成', 5: '已退款'}
    for row in c.fetchall():
        name = status_names.get(row['status'], '未知')
        print(f"  status={row['status']}({name}): {row['cnt']}条")
    
    # 订单详情
    c.execute("SELECT id, order_no, status, actual_amount, total_amount, created_at FROM orders ORDER BY id DESC LIMIT 20")
    print("\n最近20条订单:")
    for row in c.fetchall():
        name = status_names.get(row['status'], '未知')
        print(f"  ID={row['id']}, status={row['status']}({name}), actual={row['actual_amount']}, total={row['total_amount']}, time={row['created_at']}")
    
    conn.close()
    
except Exception as e:
    print(f"错误: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()

input("\n按回车退出...")
