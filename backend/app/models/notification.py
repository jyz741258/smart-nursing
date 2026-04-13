from datetime import datetime
from ..extensions import db


class Notification(db.Model):
    """通知模型"""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False, comment='用户ID')
    title = db.Column(db.String(100), nullable=False, comment='通知标题')
    content = db.Column(db.Text, comment='通知内容')

    # 通知类型: 1-系统通知, 2-护理提醒, 3-健康预警, 4-任务通知, 5-紧急通知
    notification_type = db.Column(db.SmallInteger, default=1, comment='通知类型')
    
    # 优先级: 0-普通, 1-重要, 2-紧急
    priority = db.Column(db.SmallInteger, default=0, comment='优先级')
    
    is_read = db.Column(db.Boolean, default=False, comment='是否已读')
    read_at = db.Column(db.DateTime, comment='阅读时间')
    created_by = db.Column(db.Integer, comment='创建者ID')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'title': self.title,
            'content': self.content,
            'notificationType': self.notification_type,
            'priority': self.priority,
            'isRead': self.is_read,
            'readAt': self.read_at.strftime('%Y-%m-%d %H:%M:%S') if self.read_at else None,
            'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def get_notification_type_display(self):
        type_map = {1: '系统通知', 2: '护理提醒', 3: '健康预警', 4: '任务通知', 5: '紧急通知'}
        return type_map.get(self.notification_type, '未知')

    def get_priority_display(self):
        priority_map = {0: '普通', 1: '重要', 2: '紧急'}
        return priority_map.get(self.priority, '普通')
