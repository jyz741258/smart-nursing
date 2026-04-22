from ..extensions import db
import datetime


class LocationRecord(db.Model):
    """位置记录模型"""
    __tablename__ = 'location_records'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    longitude = db.Column(db.Float, nullable=False)  # 经度
    latitude = db.Column(db.Float, nullable=False)   # 纬度
    accuracy = db.Column(db.Float, nullable=False, default=10)  # 精度（米）
    altitude = db.Column(db.Float, nullable=False, default=0)  # 海拔高度
    speed = db.Column(db.Float, nullable=False, default=0)  # 速度（米/秒）
    direction = db.Column(db.Float, nullable=False, default=0)  # 方向（度）
    location_name = db.Column(db.String(200), nullable=True, default='未知位置')  # 位置名称
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)  # 时间戳
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())  # 创建时间
    
    # 关联关系
    user = db.relationship('User', backref=db.backref('location_records', lazy='dynamic'))
