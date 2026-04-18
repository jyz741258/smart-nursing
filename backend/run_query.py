import subprocess
result = subprocess.run(
    ['python', '-c', '''
import sqlite3
conn = sqlite3.connect(r"c:\\Users\\Jyz74\\smart-nursing\\backend\\instance\\smart_nursing.db")
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute("SELECT COUNT(*) as total FROM orders")
print("总订单数:", c.fetchone()["total"])
c.execute("SELECT status, COUNT(*) as cnt FROM orders GROUP BY status ORDER BY status")
print("按状态统计:")
for row in c.fetchall():
    print(f"  status={row['status']}: {row['cnt']}条")
c.execute("SELECT id, status, actual_amount FROM orders ORDER BY id DESC LIMIT 10")
print("\\n最近10条订单:")
for row in c.fetchall():
    print(f"  ID={row['id']}, status={row['status']}, actual_amount={row['actual_amount']}")
conn.close()
'''],
    capture_output=True, text=True,
    cwd=r'c:\Users\Jyz74\smart-nursing\backend'
)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
