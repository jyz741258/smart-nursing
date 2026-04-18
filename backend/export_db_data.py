import sqlite3
import json

db = r'c:\Users\Jyz74\smart-nursing\backend\instance\smart_nursing.db'
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT COUNT(*) as total FROM orders")
total = c.fetchone()['total']

c.execute("SELECT status, COUNT(*) as cnt FROM orders GROUP BY status ORDER BY status")
stats = [dict(row) for row in c.fetchall()]

c.execute("SELECT id, order_no, status, actual_amount, total_amount, created_at FROM orders ORDER BY id DESC LIMIT 20")
orders = [dict(row) for row in c.fetchall()]

result = {
    'total_orders': total,
    'status_stats': stats,
    'recent_orders': orders
}

print(json.dumps(result, ensure_ascii=False, indent=2))
conn.close()
