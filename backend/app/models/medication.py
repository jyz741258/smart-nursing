from ..extensions import db


class MedicationReminder(db.Model):
    """用药提醒模型"""
    __tablename__ = 'medication_reminders'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    medication_name = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(10), nullable=False)  # 格式：HH:MM
    dosage = db.Column(db.String(50), nullable=False)
    days = db.Column(db.String(100), nullable=False)  # 格式：周一,周二,周三
    notes = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # 关联关系
    user = db.relationship('User', backref=db.backref('medication_reminders', lazy='dynamic'))
