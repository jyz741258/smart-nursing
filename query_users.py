import sqlite3
import os

# 数据库路径
db_path = r'C:\Users\Jyz74\smart-nursing\backend\instance\smart_nursing.db'

# 连接数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查询用户表结构
print("=== 用户表结构 ===")
cursor.execute("PRAGMA table_info(users)")
for row in cursor.fetchall():
    print(row)

print("\n=== 用户数据 ===")
cursor.execute("SELECT id, username, password_hash, phone, real_name, user_type, status, created_at FROM users")
rows = cursor.fetchall()

print(f"总计 {len(rows)} 条记录")
print("-" * 100)
print(f"{'ID':<5} {'用户名':<15} {'密码哈希(前20位)':<25} {'手机号':<15} {'真实姓名':<10} {'类型':<5} {'状态':<5} {'创建时间'}")
print("-" * 100)

for row in rows:
    user_id, username, password_hash, phone, real_name, user_type, status, created_at = row
    print(f"{user_id:<5} {username:<15} {password_hash[:20]:<25} {phone:<15} {str(real_name):<10} {user_type:<5} {status:<5} {created_at}")

conn.close()

# 用户类型说明
print("\n=== 用户类型说明 ===")
print("1 - 老人")
print("2 - 护理人员")
print("3 - 管理员")
print("4 - 家属")

# 状态说明
print("\n=== 状态说明 ===")
print("0 - 禁用")
print("1 - 正常")
