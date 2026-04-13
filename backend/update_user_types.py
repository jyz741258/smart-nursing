# -*- coding: utf-8 -*-
"""更新用户类型"""
from app import create_app
from app.extensions import db

app = create_app('default')

def update_user_types():
    """更新用户类型"""
    with app.app_context():
        # 更新管理员类型 (从0改为3)
        result = db.session.execute(
            db.text("UPDATE users SET user_type = 3 WHERE user_type = 0 AND phone = '13800138000'")
        )
        db.session.commit()
        print(f'已更新 {result.rowcount} 个管理员账号')

        # 添加两个老人测试数据
        from app.models import User
        
        if not User.query.filter_by(phone='13900139001').first():
            user2 = User(
                username='testuser2',
                phone='13900139001',
                real_name='李奶奶',
                gender=2,
                age=82,
                user_type=1,
                status=1
            )
            user2.set_password('123456')
            db.session.add(user2)
            db.session.commit()
            print('已创建老人账号: 13900139001 / 123456 (李奶奶)')

        # 验证结果
        print('\n当前用户列表:')
        users = User.query.all()
        for u in users:
            type_names = {1: '老人', 2: '护理人员', 3: '管理员'}
            print(f"  {u.phone} - {u.real_name or u.username} ({type_names.get(u.user_type, '未知')})")

if __name__ == '__main__':
    update_user_types()
