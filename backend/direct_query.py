"""查询数据库 - 使用subprocess避免编码问题"""
import subprocess
import sys

code = """
import sqlite3
conn = sqlite3.connect(r'C:\\Users\\Jyz74\\smart-nursing\\backend\\instance\\smart_nursing.db')
c = conn.cursor()
c.execute("SELECT COUNT(*) FROM orders")
print("TOTAL:", c.fetchone()[0])
c.execute("SELECT status, COUNT(*) FROM orders GROUP BY status ORDER BY status")
print("STATS:", c.fetchall())
c.execute("SELECT id, status FROM orders ORDER BY id DESC LIMIT 10")
print("RECENT:", c.fetchall())
conn.close()
"""

result = subprocess.run(
    [sys.executable, '-c', code],
    capture_output=True, text=True,
    cwd=r'C:\Users\Jyz74\smart-nursing\backend'
)

print("STDOUT:", result.stdout)
print("STDERR:", result.stderr[:300] if result.stderr else "无")
print("RC:", result.returncode)
