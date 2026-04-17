from datetime import datetime
from ..extensions import db


class Order(db.Model):
    """订单模型"""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_no = db.Column(db.String(32), unique=True, nullable=False, index=True, comment='订单编号')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID(下单者)')
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False, comment='服务ID')
    elder_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='老人ID(服务对象)')
    nurse_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='护理人员ID')
    address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'), comment='地址ID')

    # 订单金额信息
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, comment='订单总金额')
    discount_amount = db.Column(db.Numeric(10, 2), default=0, comment='优惠金额')
    actual_amount = db.Column(db.Numeric(10, 2), nullable=False, comment='实际支付金额')

    # 服务信息快照
    service_name = db.Column(db.String(100), comment='服务名称快照')
    service_price = db.Column(db.Numeric(10, 2), comment='服务价格快照')
    service_image = db.Column(db.String(255), comment='服务图片快照')

    # 地址信息快照
    address_snapshot = db.Column(db.Text, comment='地址信息JSON快照')

    # 预约信息
    appointment_date = db.Column(db.Date, comment='预约日期')
    appointment_time = db.Column(db.String(20), comment='预约时间段')
    order_time = db.Column(db.DateTime, comment='下单时间')
    remark = db.Column(db.String(500), comment='备注')
    notes = db.Column(db.String(500), comment='订单备注')
    created_by = db.Column(db.Integer, comment='创建人ID')

    # 订单状态: 0-已取消, 1-待支付, 2-已支付/待服务, 3-服务中, 4-已完成, 5-已退款
    status = db.Column(db.SmallInteger, default=1, comment='订单状态')

    # 支付信息
    payment_method = db.Column(db.String(20), comment='支付方式')
    payment_time = db.Column(db.DateTime, comment='支付时间')
    pay_transaction_id = db.Column(db.String(64), comment='支付流水号')

    # 完成信息
    service_start_time = db.Column(db.DateTime, comment='服务开始时间')
    service_end_time = db.Column(db.DateTime, comment='服务结束时间')
    completion_time = db.Column(db.DateTime, comment='完成时间')

    # 取消信息
    cancel_reason = db.Column(db.String(255), comment='取消原因')
    cancel_time = db.Column(db.DateTime, comment='取消时间')

    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系
    service = db.relationship('Service', backref='orders')
    address = db.relationship('Address', backref='orders')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'orderNo': self.order_no,
            'userId': self.user_id,
            'serviceId': self.service_id,
            'elderId': self.elder_id,
            'nurseId': self.nurse_id,
            'addressId': self.address_id,
            'orderTime': self.order_time.strftime('%Y-%m-%d %H:%M:%S') if self.order_time else None,
            'notes': self.notes,
            'createdBy': self.created_by,
            'totalAmount': float(self.total_amount) if self.total_amount else 0,
            'discountAmount': float(self.discount_amount) if self.discount_amount else 0,
            'actualAmount': float(self.actual_amount) if self.actual_amount else 0,
            'serviceName': self.service_name,
            'servicePrice': float(self.service_price) if self.service_price else 0,
            'serviceImage': self.service_image,
            'addressSnapshot': self.address_snapshot,
            'appointmentDate': self.appointment_date.strftime('%Y-%m-%d') if self.appointment_date else None,
            'appointmentTime': self.appointment_time,
            'remark': self.remark,
            'status': self.status,
            'statusText': self.get_status_text(),
            'paymentMethod': self.payment_method,
            'paymentTime': self.payment_time.strftime('%Y-%m-%d %H:%M:%S') if self.payment_time else None,
            'payTransactionId': self.pay_transaction_id,
            'serviceStartTime': self.service_start_time.strftime('%Y-%m-%d %H:%M:%S') if self.service_start_time else None,
            'serviceEndTime': self.service_end_time.strftime('%Y-%m-%d %H:%M:%S') if self.service_end_time else None,
            'completionTime': self.completion_time.strftime('%Y-%m-%d %H:%M:%S') if self.completion_time else None,
            'cancelReason': self.cancel_reason,
            'cancelTime': self.cancel_time.strftime('%Y-%m-%d %H:%M:%S') if self.cancel_time else None,
            'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def get_status_text(self):
        """获取状态文本"""
        status_map = {
            0: '已取消',
            1: '待支付',
            2: '待服务',
            3: '服务中',
            4: '已完成',
            5: '已退款'
        }
        return status_map.get(self.status, '未知')
