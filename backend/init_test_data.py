# -*- coding: utf-8 -*-
"""初始化测试数据"""
from app import create_app
from app.extensions import db
from app.models import User, Service, CarePlan, CareTask, HealthMetric, NursingRecord, Notification

app = create_app('default')

def init_test_data():
    """初始化测试数据"""
    with app.app_context():
        # 创建管理员账号
        if not User.query.filter_by(phone='13800138000').first():
            admin = User(
                username='admin',
                phone='13800138000',
                real_name='系统管理员',
                user_type=3,  # 管理员
                status=1
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print('已创建管理员账号: 13800138000 / admin123')

        # 创建老人账号
        if not User.query.filter_by(phone='13900139000').first():
            user = User(
                username='testuser',
                phone='13900139000',
                real_name='王大爷',
                gender=1,
                age=78,
                user_type=1,  # 老人
                status=1
            )
            user.set_password('123456')
            db.session.add(user)
            print('已创建老人账号: 13900139000 / 123456')

        # 创建第二位老人
        if not User.query.filter_by(phone='13900139001').first():
            user2 = User(
                username='testuser2',
                phone='13900139001',
                real_name='李奶奶',
                gender=2,
                age=82,
                user_type=1,  # 老人
                status=1
            )
            user2.set_password('123456')
            db.session.add(user2)
            print('已创建老人账号: 13900139001 / 123456')

        # 创建护理人员账号
        if not User.query.filter_by(phone='13700137000').first():
            nurse = User(
                username='nurse',
                phone='13700137000',
                real_name='张护士',
                user_type=2,  # 护理人员
                status=1
            )
            nurse.set_password('123456')
            db.session.add(nurse)
            print('已创建护理人员账号: 13700137000 / 123456')

        db.session.commit()
        print('测试数据初始化完成！')

if __name__ == '__main__':
    init_test_data()
