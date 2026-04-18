"""直接读取数据库二进制并解析（简化版）"""
import sqlite3
import struct

def read_db():
    db_path = r'C:\Users\Jyz74\smart-nursing\backend\instance\smart_nursing.db'
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # 查询关键信息
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='orders'")
    table = c.fetchone()
    print("orders表存在:", table is not None)
    
    c.execute("SELECT COUNT(*) FROM orders")
    total = c.fetchone()[0]
    print(f"总订单数: {total}")
    
    c.execute("SELECT id, status, order_no, actual_amount FROM orders ORDER BY id DESC LIMIT 5")
    print("\n最近5条订单:")
    for row in c.fetchall():
        print(f"  ID={row[0]}, status={row[1]}, order_no={row[2]}, actual={row[3]}")
    
    conn.close()

if __name__ == '__main__':
    read_db()
