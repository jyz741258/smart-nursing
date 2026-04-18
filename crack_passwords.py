import sqlite3
from werkzeug.security import check_password_hash

# 连接数据库
conn = sqlite3.connect(r'C:\Users\Jyz74\smart-nursing\backend\instance\smart_nursing.db')
cursor = conn.cursor()

cursor.execute("SELECT id, username, password_hash, phone FROM users")
users = cursor.fetchall()

# 常见默认密码猜测
common_passwords = ['123456', '12345678', 'admin123', 'smartnursing', 'password', 'admin888', '111111']

print("=== 尝试破解密码 ===\n")

for user in users:
    user_id, username, password_hash, phone = user
    print(f"用户: {username} (ID: {user_id}, 手机: {phone})")
    
    # 尝试常见密码
    for pwd in common_passwords:
        try:
            if check_password_hash(password_hash, pwd):
                print(f"  ✅ 密码可能是: {pwd}")
                break
        except:
            pass
    else:
        print(f"  ❌ 密码未破解 (哈希: {password_hash[:30]}...)")
    print()

conn.close()

print("\n提示：如果常见密码都不对，可以注册新账号或通过API重置密码。")
