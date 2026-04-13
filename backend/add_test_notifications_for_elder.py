# -*- coding: utf-8 -*-
"""为老人和护理人员添加测试通知数据"""
from app import create_app
from app.extensions import db
from app.models import Notification

app = create_app('default')

def add_notifications_for_elder():
    """为老人账号添加测试通知数据"""
    with app.app_context():
        # 获取老人用户ID
        from app.models import User

        # 获取张三老人
        zhangsan = User.query.filter_by(phone='13900001001').first()
        if zhangsan:
            # 检查是否已有通知
            existing = Notification.query.filter_by(user_id=zhangsan.id).first()
            if existing:
                print(f"老人 {zhangsan.real_name} 已有通知数据，跳过创建")
            else:
                notifications = [
                    # 系统通知
                    Notification(
                        user_id=zhangsan.id,
                        title='欢迎使用智慧养老系统',
                        content='您好！欢迎使用智慧养老系统，您可以通过系统查看护理记录、健康数据和接收通知。',
                        notification_type=1,
                        priority=0,
                        created_by=1
                    ),
                    # 护理提醒
                    Notification(
                        user_id=zhangsan.id,
                        title='明日护理安排',
                        content='明日上午9点，护理人员将为您进行日常健康检查。',
                        notification_type=2,
                        priority=1,
                        created_by=1
                    ),
                    # 健康预警
                    Notification(
                        user_id=zhangsan.id,
                        title='健康提醒',
                        content='您的近期血压略有波动，建议注意饮食和休息，并按时服药。',
                        notification_type=3,
                        priority=1,
                        created_by=1
                    ),
                    # 任务通知
                    Notification(
                        user_id=zhangsan.id,
                        title='康复训练计划',
                        content='您被安排参加每周三下午的康复训练课程，请准时参加。',
                        notification_type=4,
                        priority=0,
                        created_by=1
                    ),
                    # 紧急通知
                    Notification(
                        user_id=zhangsan.id,
                        title='紧急联系',
                        content='如有任何不适，请立即按下紧急呼叫按钮，我们将第一时间为您提供帮助。',
                        notification_type=5,
                        priority=2,
                        created_by=1
                    )
                ]

                db.session.add_all(notifications)
                db.session.commit()
                print(f"为老人 {zhangsan.real_name} 添加了 {len(notifications)} 条通知数据")
        else:
            print("未找到张三老人用户")

        # 获取李奶奶
        limama = User.query.filter_by(phone='13900139001').first()
        if limama:
            existing = Notification.query.filter_by(user_id=limama.id).first()
            if existing:
                print(f"老人 {limama.real_name} 已有通知数据，跳过创建")
            else:
                notifications = [
                    Notification(
                        user_id=limama.id,
                        title='系统升级通知',
                        content='智慧养老系统��完成升级，功能更加完善，欢迎使用！',
                        notification_type=1,
                        priority=0,
                        created_by=1
                    ),
                    Notification(
                        user_id=limama.id,
                        title='健康数据更新',
                        content='您的最新健康数据已上传，请及时查看。',
                        notification_type=3,
                        priority=1,
                        created_by=1
                    ),
                    Notification(
                        user_id=limama.id,
                        title='护理计划提醒',
                        content='您明天下午2点有一项康复训练计划，请做好准备。',
                        notification_type=2,
                        priority=1,
                        created_by=1
                    )
                ]

                db.session.add_all(notifications)
                db.session.commit()
                print(f"为老人 {limama.real_name} 添加了 {len(notifications)} 条通知数据")

if __name__ == '__main__':
    add_notifications_for_elder()
