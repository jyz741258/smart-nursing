"""检查SQLite数据库"""
import sqlite3

db_file = r'c:\Users\Jyz74\smart-nursing\backend\instance\smart_nursing.db'

try:
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # 查看所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("数据库中的表:")
    for table in tables:
        print(f"  - {table[0]}")

    # 查询orders表记录数
    cursor.execute("SELECT COUNT(*) FROM orders;")
    count = cursor.fetchone()[0]
    print(f"\norders表总记录数: {count}")

    if count > 0:
        # 查看订单详情
        cursor.execute("SELECT id, order_no, status, actual_amount, created_at FROM orders LIMIT 5;")
        rows = cursor.fetchall()
        print("\n前5条订单:")
        for row in rows:
            print(f"  ID:{row[0]}, 订单号:{row[1]}, 状态:{row[2]}, 金额:{row[3]}, 时间:{row[4]}")

        # 按状态统计
        cursor.execute("SELECT status, COUNT(*) FROM orders GROUP BY status;")
        status_counts = cursor.fetchall()
        print("\n订单状态统计:")
        for status, cnt in status_counts:
            print(f"  状态 {status}: {cnt} 条")
    else:
        print("订单表为空！")

    conn.close()

except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
