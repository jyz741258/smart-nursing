from ..extensions import db
import datetime


class CheckinRecord(db.Model):
    """打卡记录模型"""
    __tablename__ = 'checkin_records'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.date.today())
    time = db.Column(db.Time, nullable=False, default=datetime.datetime.now().time())
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    
    # 关联关系
    user = db.relationship('User', backref=db.backref('checkin_records', lazy='dynamic'))
