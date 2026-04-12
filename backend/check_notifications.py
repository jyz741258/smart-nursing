from app import create_app
from app.extensions import db
from app.models import Notification, User
from datetime import datetime

# 创建应用实例
app = create_app('default')

# 在应用上下文中查询数据
with app.app_context():
    # 查询所有通知
    notifications = Notification.query.all()
    print(f"总共有 {len(notifications)} 条通知")
    
    # 打印每条通知的信息
    for i, notification in enumerate(notifications):
        print(f"\n通知 {i+1}:")
        print(f"ID: {notification.id}")
        print(f"用户ID: {notification.user_id}")
        print(f"标题: {notification.title}")
        print(f"内容: {notification.content}")
        print(f"类型: {notification.notification_type}")
        print(f"优先级: {notification.priority}")
        print(f"是否已读: {notification.is_read}")
        print(f"创建时间: {notification.created_at}")
    
    # 查询所有用户
    users = User.query.all()
    print(f"\n总共有 {len(users)} 个用户")
    for user in users:
        print(f"用户ID: {user.id}, 姓名: {user.name}, 类型: {user.user_type}")
