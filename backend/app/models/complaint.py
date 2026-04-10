from datetime import datetime
from ..extensions import db


class Complaint(db.Model):
    """投诉模型"""
    __tablename__ = 'complaints'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    complaint_no = db.Column(db.String(32), unique=True, nullable=False, index=True, comment='投诉编号')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), comment='关联订单ID')

    # 投诉类型: 1-服务态度, 2-服务质量, 3-服务超时, 4-乱收费, 5-其他
    complaint_type = db.Column(db.SmallInteger, nullable=False, comment='投诉类型')
    title = db.Column(db.String(100), nullable=False, comment='投诉标题')
    content = db.Column(db.Text, nullable=False, comment='投诉内容')
    images = db.Column(db.Text, comment='投诉图片JSON数组')

    # 处理状态: 0-已提交, 1-处理中, 2-已回复, 3-已解决, 4-已关闭
    status = db.Column(db.SmallInteger, default=0, comment='处理状态')
    handle_content = db.Column(db.Text, comment='处理回复')
    handle_time = db.Column(db.DateTime, comment='处理时间')

    # 评价
    user_rating = db.Column(db.SmallInteger, comment='用户满意度评分 1-5')

    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系
    order = db.relationship('Order', backref='complaints')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'complaintNo': self.complaint_no,
            'userId': self.user_id,
            'orderId': self.order_id,
            'complaintType': self.complaint_type,
            'complaintTypeText': self.get_type_text(),
            'title': self.title,
            'content': self.content,
            'images': self.images,
            'status': self.status,
            'statusText': self.get_status_text(),
            'handleContent': self.handle_content,
            'handleTime': self.handle_time.strftime('%Y-%m-%d %H:%M:%S') if self.handle_time else None,
            'userRating': self.user_rating,
            'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def get_type_text(self):
        """获取类型文本"""
        type_map = {
            1: '服务态度',
            2: '服务质量',
            3: '服务超时',
            4: '乱收费',
            5: '其他'
        }
        return type_map.get(self.complaint_type, '未知')

    def get_status_text(self):
        """获取状态文本"""
        status_map = {
            0: '已提交',
            1: '处理中',
            2: '已回复',
            3: '已解决',
            4: '已关闭'
        }
        return status_map.get(self.status, '未知')
