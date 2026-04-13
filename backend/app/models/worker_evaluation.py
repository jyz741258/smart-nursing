from datetime import datetime
from ..extensions import db


class WorkerEvaluation(db.Model):
    """护工评价模型 - 老人/家属对护工的评价"""
    __tablename__ = 'worker_evaluations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='评价ID')
    elder_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='老人ID')
    worker_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='护工ID')
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), comment='关联订单ID')

    # 评分 1-5 星
    overall_rating = db.Column(db.Numeric(2, 1), nullable=False, comment='总体评分 1-5')

    # 维度评分 1-5
    professionalism_rating = db.Column(db.Integer, default=5, comment='专业程度评分')
    attitude_rating = db.Column(db.Integer, default=5, comment='服务态度评分')
    punctuality_rating = db.Column(db.Integer, default=5, comment='准时性评分')
    skill_rating = db.Column(db.Integer, default=5, comment='技能水平评分')

    # 评价内容
    content = db.Column(db.Text, comment='评价内容')
    tags = db.Column(db.Text, comment='评价标签JSON数组，如["专业","耐心","细心"]')

    # 是否匿名评价
    is_anonymous = db.Column(db.SmallInteger, default=0, comment='是否匿名: 0-否, 1-是')

    # 护工回复
    reply_content = db.Column(db.Text, comment='护工回复内容')
    reply_time = db.Column(db.DateTime, comment='回复时间')

    # 状态
    status = db.Column(db.SmallInteger, default=1, comment='状态: 0-隐藏, 1-显示')

    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系
    elder = db.relationship('User', primaryjoin='WorkerEvaluation.elder_id == User.id', foreign_keys=[elder_id], viewonly=True)
    worker = db.relationship('User', primaryjoin='WorkerEvaluation.worker_id == User.id', foreign_keys=[worker_id], viewonly=True)
    order = db.relationship('Order', backref='worker_evaluation')

    def to_dict(self, include_user_info=True):
        """转换为字典"""
        data = {
            'id': self.id,
            'elder_id': self.elder_id,
            'worker_id': self.worker_id,
            'order_id': self.order_id,
            'overall_rating': float(self.overall_rating) if self.overall_rating else 0,
            'professionalism_rating': self.professionalism_rating,
            'attitude_rating': self.attitude_rating,
            'punctuality_rating': self.punctuality_rating,
            'skill_rating': self.skill_rating,
            'content': self.content,
            'tags': self.tags,
            'is_anonymous': self.is_anonymous,
            'reply_content': self.reply_content,
            'reply_time': self.reply_time.strftime('%Y-%m-%d %H:%M:%S') if self.reply_time else None,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
        }

        if include_user_info:
            data.update({
                'elder_name': self.elder.name if self.elder else None,
                'elder_avatar': self.elder.avatar if self.elder else None,
                'worker_name': self.worker.name if self.worker else None,
                'worker_avatar': self.worker.avatar if self.worker else None,
            })

        return data
