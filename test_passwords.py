import sqlite3
from werkzeug.security import check_password_hash

# 连接数据库
conn = sqlite3.connect(r'C:\Users\Jyz74\smart-nursing\backend\instance\smart_nursing.db')
cursor = conn.cursor()

cursor.execute("SELECT id, username, password_hash, phone, real_name FROM users")
users = cursor.fetchall()

# 常见默认密码猜测（用于测试）
test_passwords = ['123456', '12345678', 'admin123', 'smartnursing', 'password', 'admin888', '111111', '000000']

print("=== Test Default Passwords ===\n")

for user in users:
    user_id, username, password_hash, phone, real_name = user
    print(f"User: {username} ({real_name}) - Phone: {phone}")
    
    # 尝试常见密码
    found = False
    for pwd in test_passwords:
        try:
            if check_password_hash(password_hash, pwd):
                print(f"  [OK] Password found: {pwd}")
                found = True
                break
        except:
            pass
    
    if not found:
        print(f"  [!] Password unknown (need reset)")
    print()

conn.close()

print("\nSuggestions:")
print("1. If no password matches, register a new account for testing")
print("2. Or reset password via API if that feature is implemented")
print("3. In development, you can directly modify password hash in database")
