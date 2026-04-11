from app import create_app
from app.extensions import db
from app.models import User

# 创建应用实例
app = create_app('default')

# 在应用上下文中查询数据
with app.app_context():
    # 查询所有用户
    all_users = User.query.all()
    print(f"总共有 {len(all_users)} 个用户")
    
    # 按用户类型分组查询
    user_types = {1: '老人', 2: '护理人员', 3: '管理员', 4: '家属'}
    for user_type, type_name in user_types.items():
        users = User.query.filter_by(user_type=user_type).all()
        print(f"{type_name}用户: {len(users)} 个")
        for user in users:
            print(f"  ID: {user.id}, 姓名: {user.name}, 电话: {user.phone}")
