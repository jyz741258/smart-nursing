# -*- coding: utf-8 -*-
"""初始化完整的测试数据"""
from app import create_app
from app.extensions import db
from app.models import (
    User, Service, CarePlan, CareTask, HealthMetric,
    NursingRecord, Notification, Order, Complaint
)
from datetime import datetime, timedelta
import random

app = create_app('default')


def init_all_test_data():
    """初始化完整的测试数据"""
    with app.app_context():
        # ========== 1. 创建用户 ==========
        users_data = [
            {'username': 'admin', 'phone': '13800138000', 'real_name': '系统管理员', 'user_type': 3, 'status': 1},
            {'username': 'nurse1', 'phone': '13700137000', 'real_name': '张护士', 'user_type': 2, 'status': 1},
            {'username': 'nurse2', 'phone': '13700137001', 'real_name': '李护士', 'user_type': 2, 'status': 1},
            {'username': 'nurse3', 'phone': '13700137002', 'real_name': '王护士', 'user_type': 2, 'status': 1},
            {'username': 'elder1', 'phone': '13900139000', 'real_name': '王大爷', 'gender': 1, 'age': 78, 'user_type': 1, 'status': 1},
            {'username': 'elder2', 'phone': '13900139001', 'real_name': '李奶奶', 'gender': 2, 'age': 82, 'user_type': 1, 'status': 1},
            {'username': 'elder3', 'phone': '13900139002', 'real_name': '张爷爷', 'gender': 1, 'age': 75, 'user_type': 1, 'status': 1},
            {'username': 'elder4', 'phone': '13900139003', 'real_name': '刘奶奶', 'gender': 2, 'age': 80, 'user_type': 1, 'status': 1},
            {'username': 'family1', 'phone': '13900001004', 'real_name': '王家人', 'gender': 1, 'user_type': 4, 'status': 1},
        ]

        users = {}
        for data in users_data:
            phone = data['phone']
            existing = User.query.filter_by(phone=phone).first()
            if not existing:
                user = User(
                    username=data['username'],
                    phone=data['phone'],
                    real_name=data['real_name'],
                    gender=data.get('gender', 1),
                    age=data.get('age', 70),
                    user_type=data['user_type'],
                    status=data['status']
                )
                user.set_password('123456')
                db.session.add(user)
            else:
                users[data['real_name']] = existing
            db.session.commit()
        
        # 重新获取所有用户
        for data in users_data:
            users[data['real_name']] = User.query.filter_by(phone=data['phone']).first()

        print('用户创建完成')

        # ========== 2. 创建护理记录 ==========
        descriptions = {
            1: '协助老人进行日常洗漱、更换衣物',
            2: '测量血压血糖，指导用药',
            3: '进行肢体康复训练30分钟',
            4: '与老人谈心，进行心理疏导',
            5: '协助准备营养餐食',
            6: '帮助老人清洁身体，更换床单',
            7: '检查房间安全设施'
        }

        elders = ['王大爷', '李奶奶', '张爷爷', '刘奶奶']
        nurses = ['张护士', '李护士', '王护士']

        # 检查是否已有护理记录，如果没有则创建
        existing_records = NursingRecord.query.count()
        if existing_records < 20:
            for i in range(20 - existing_records):
                elder_name = random.choice(elders)
                nurse_name = random.choice(nurses)
                nursing_type = random.randint(1, 7)

                record = NursingRecord(
                    elder_id=users[elder_name].id,
                    nursing_type=nursing_type,
                    description=descriptions[nursing_type],
                    staff_id=users[nurse_name].id,
                    status=random.choice([1, 2]),
                    start_time=datetime.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 12)),
                    end_time=datetime.now() - timedelta(days=random.randint(0, 30)) if random.random() > 0.3 else None,
                    notes='护理过程正常' if random.random() > 0.5 else None,
                    created_at=datetime.now() - timedelta(days=random.randint(0, 30))
                )
                db.session.add(record)
            
            db.session.commit()
            print(f'已创建 {20 - existing_records} 条护理记录')
        else:
            print(f'护理记录已存在 ({existing_records} 条)')

        # ========== 3. 创建通知 ==========
        notification_titles = [
            '系统更新通知',
            '护理计划变更提醒',
            '健康数据异常提醒',
            '定期体检通知',
            '服务续费提醒',
        ]

        existing_notifications = Notification.query.count()
        if existing_notifications < 5:
            for i, title in enumerate(notification_titles):
                notification = Notification(
                    user_id=users['王大爷'].id if i < 3 else users['李奶奶'].id,
                    title=title,
                    content=f'亲爱的用户，您有一条新的通知：{title}',
                    notification_type=random.randint(1, 4),
                    priority=random.randint(0, 2),
                    is_read=random.choice([True, False]),
                    created_at=datetime.now() - timedelta(days=i)
                )
                db.session.add(notification)
            
            db.session.commit()
            print('已创建通知')
        else:
            print('通知已存在')

        # ========== 4. 创建健康数据 ==========
        existing_metrics = HealthMetric.query.count()
        if existing_metrics < 50:
            # metric_type: 1-体温, 2-血压-收缩压, 3-血压-舒张压, 4-心率, 5-血氧, 6-血糖, 7-体重, 8-身高
            metric_configs = [
                (1, '℃'), (2, 'mmHg'), (3, 'mmHg'), (4, '次/分'), (5, '%'), (6, 'mmol/L'), (7, 'kg'), (8, 'cm')
            ]
            for elder_name in elders:
                for day in range(3):
                    for metric_type, unit in metric_configs:
                        if metric_type == 1:
                            value = random.uniform(36.0, 37.5)
                        elif metric_type in [2, 3]:
                            value = random.uniform(60, 140)
                        elif metric_type == 4:
                            value = random.uniform(60, 100)
                        elif metric_type == 5:
                            value = random.uniform(95, 100)
                        elif metric_type == 6:
                            value = random.uniform(4.0, 8.0)
                        elif metric_type == 7:
                            value = random.uniform(40, 90)
                        else:
                            value = random.uniform(120, 180)
                        
                        health_data = HealthMetric(
                            elder_id=users[elder_name].id,
                            metric_type=metric_type,
                            metric_value=value,
                            unit=unit,
                            recorded_at=datetime.now() - timedelta(days=day)
                        )
                        db.session.add(health_data)
            
            db.session.commit()
            print('已创建健康数据')
        else:
            print('健康数据已存在')

        print('\n========== 测试数据初始化完成！ ==========')
        print('测试账号:')
        print('  管理员: 13800138000 / 123456')
        print('  护理人员: 13700137000 / 123456')
        print('  老人: 13900139000 / 123456')
        print('  家属: 13900001004 / 123456')


if __name__ == '__main__':
    init_all_test_data()
