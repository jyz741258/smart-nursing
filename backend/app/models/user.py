from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db


class User(db.Model):
    """用户模型"""

    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    @property
    def name(self):
        """返回真实姓名或用户名"""
        return self.real_name or self.username

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True, comment='用户名')
    password_hash = db.Column(db.String(255), nullable=False, comment='密码哈希')
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True, comment='手机号')
    real_name = db.Column(db.String(50), comment='真实姓名')
    id_card = db.Column(db.String(20), comment='身份证号')
    gender = db.Column(db.SmallInteger, default=0, comment='性别: 0-未知, 1-男, 2-女')
    age = db.Column(db.Integer, comment='年龄')
    avatar = db.Column(db.String(255), comment='头像URL')
    address = db.Column(db.String(255), comment='地址')
    email = db.Column(db.String(100), comment='邮箱')
    emergency_contact = db.Column(db.String(50), comment='紧急联系人')
    emergency_phone = db.Column(db.String(20), comment='紧急联系电话')
    status = db.Column(db.SmallInteger, default=1, comment='状态: 0-禁用, 1-正常')
    user_type = db.Column(db.SmallInteger, default=1, comment='用户类型: 1-老人, 2-护理人员, 3-管理员, 4-家属')
    binding_elder_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='绑定的老人ID(家属用)')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    last_login = db.Column(db.DateTime, comment='最后登录时间')

    # 关系
    addresses = db.relationship('Address', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    orders = db.relationship('Order', foreign_keys='Order.user_id', backref='order_user', lazy='dynamic', cascade='all, delete-orphan')
    elder_orders = db.relationship('Order', foreign_keys='Order.elder_id', backref='elder', lazy='dynamic')
    nurse_orders = db.relationship('Order', foreign_keys='Order.nurse_id', backref='nurse', lazy='dynamic')
    evaluations = db.relationship('Evaluation', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    complaints = db.relationship('Complaint', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    # 家属绑定的老人
    binding_elder = db.relationship('User', remote_side=[id], foreign_keys=[binding_elder_id], backref='binded_families')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'phone': self.phone,
            'realName': self.real_name,
            'gender': self.gender,
            'age': self.age,
            'avatar': self.avatar,
            'email': self.email,
            'emergencyContact': self.emergency_contact,
            'emergencyPhone': self.emergency_phone,
            'status': self.status,
            'userType': self.user_type,
            'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'lastLogin': self.last_login.strftime('%Y-%m-%d %H:%M:%S') if self.last_login else None
        }
