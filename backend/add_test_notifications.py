from app import create_app
from app.extensions import db
from app.models import Notification
from datetime import datetime, timedelta

# 创建应用实例
app = create_app('default')

# 在应用上下文中添加测试数据
with app.app_context():
    # 添加测试通知数据
    notifications = [
        # 系统通知
        Notification(
            user_id=1,  # 管理员
            title='系统升级通知',
            content='系统将于今晚23:00进行升级维护，预计持续2小时，期间系统可能会暂时无法访问。',
            notification_type=1,  # 系统通知
            priority=1,  # 重要
            created_by=1
        ),
        # 护理提醒
        Notification(
            user_id=3,  # 护理人员
            title='护理任务提醒',
            content='您有一项护理任务需要执行：为李奶奶测量血压和心率。',
            notification_type=2,  # 护理提醒
            priority=1,  # 重要
            created_by=1
        ),
        # 健康预警
        Notification(
            user_id=1,  # 管理员
            title='健康预警',
            content='李奶奶的血压异常偏高，收缩压为160mmHg，请及时关注。',
            notification_type=3,  # 健康预警
            priority=2,  # 紧急
            created_by=1
        ),
        # 任务通知
        Notification(
            user_id=6,  # 护理人员
            title='新任务分配',
            content='您被分配了新的护理任务：协助张三进行康复训练。',
            notification_type=4,  # 任务通知
            priority=1,  # 重要
            created_by=1
        ),
        # 紧急通知
        Notification(
            user_id=1,  # 管理员
            title='紧急通知',
            content='张三老人突然感到不适，需要紧急处理，请立即安排护理人员前往查看。',
            notification_type=5,  # 紧急通知
            priority=2,  # 紧急
            created_by=1
        ),
        # 已完成的通知
        Notification(
            user_id=1,  # 管理员
            title='护理任务完成通知',
            content='李护理已完成对李奶奶的护理任务。',
            notification_type=4,  # 任务通知
            priority=0,  # 普通
            is_read=True,
            read_at=datetime.now() - timedelta(hours=1),
            created_by=1
        ),
        # 待完成的通知
        Notification(
            user_id=1,  # 管理员
            title='待完成任务提醒',
            content='有3项护理任务尚未完成，请及时跟进。',
            notification_type=4,  # 任务通知
            priority=1,  # 重要
            created_by=1
        )
    ]
    
    # 添加到数据库
    db.session.add_all(notifications)
    db.session.commit()
    
    print(f"成功添加了 {len(notifications)} 条测试通知数据！")
