from ..extensions import db
import datetime


class EmergencyCall(db.Model):
    """紧急呼叫记录模型"""
    __tablename__ = 'emergency_calls'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    elder_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False, default='sos')  # 呼叫类型：sos, help, etc.
    location = db.Column(db.String(200), nullable=False, default='未知位置')
    status = db.Column(db.String(50), nullable=False, default='pending')  # pending, assigned, responding, completed
    assigned_worker_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    response_time = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    
    # 关联关系
    elder = db.relationship('User', foreign_keys=[elder_id], backref=db.backref('emergency_calls', lazy='dynamic'))
    assigned_worker = db.relationship('User', foreign_keys=[assigned_worker_id], backref=db.backref('assigned_emergency_calls', lazy='dynamic'))
