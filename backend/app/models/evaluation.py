from datetime import datetime
from ..extensions import db


class Evaluation(db.Model):
    """评价模型"""
    __tablename__ = 'evaluations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, comment='订单ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), comment='服务ID')

    rating = db.Column(db.Numeric(3, 2), nullable=False, comment='评分 1-5')
    content = db.Column(db.Text, comment='评价内容')
    images = db.Column(db.Text, comment='评价图片JSON数组')

    # 标签评价
    is_punctual = db.Column(db.SmallInteger, default=1, comment='是否准时: 0-否, 1-是')
    is_professional = db.Column(db.SmallInteger, default=1, comment='是否专业: 0-否, 1-是')
    is_friendly = db.Column(db.SmallInteger, default=1, comment='是否友好: 0-否, 1-是')

    # 回复
    reply_content = db.Column(db.Text, comment='回复内容')
    reply_time = db.Column(db.DateTime, comment='回复时间')

    # 状态
    status = db.Column(db.SmallInteger, default=1, comment='状态: 0-隐藏, 1-显示')
    is_anonymous = db.Column(db.SmallInteger, default=0, comment='是否匿名: 0-否, 1-是')

    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系
    order = db.relationship('Order', backref='evaluation')
    service = db.relationship('Service', backref='evaluations')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'orderId': self.order_id,
            'userId': self.user_id,
            'serviceId': self.service_id,
            'rating': float(self.rating) if self.rating else 0,
            'content': self.content,
            'images': self.images,
            'isPunctual': self.is_punctual,
            'isProfessional': self.is_professional,
            'isFriendly': self.is_friendly,
            'replyContent': self.reply_content,
            'replyTime': self.reply_time.strftime('%Y-%m-%d %H:%M:%S') if self.reply_time else None,
            'status': self.status,
            'isAnonymous': self.is_anonymous,
            'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
