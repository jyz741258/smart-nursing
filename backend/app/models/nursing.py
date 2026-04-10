from datetime import datetime
from ..extensions import db


class NursingRecord(db.Model):
    """护理记录模型"""
    __tablename__ = 'nursing_records'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    elder_id = db.Column(db.Integer, nullable=False, comment='老人ID')
    
    # 护理类型: 1-日常照护, 2-医疗护理, 3-康复训练, 4-心理疏导, 5-饮食护理, 6-清洁护理, 7-安全护理
    nursing_type = db.Column(db.SmallInteger, nullable=False, comment='护理类型')
    
    description = db.Column(db.Text, comment='护理描述')
    start_time = db.Column(db.DateTime, comment='开始时间')
    end_time = db.Column(db.DateTime, comment='结束时间')
    
    # 状态: 1-进行中, 2-已完成
    status = db.Column(db.SmallInteger, default=1, comment='状态')
    
    staff_id = db.Column(db.Integer, comment='护理人员ID')
    notes = db.Column(db.Text, comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系（使用 primaryjoin 指定连接条件，因为没有外键）
    elder = db.relationship('User', primaryjoin='NursingRecord.elder_id == User.id', foreign_keys=[elder_id], backref='nursing_records', viewonly=True)
    staff = db.relationship('User', primaryjoin='NursingRecord.staff_id == User.id', foreign_keys=[staff_id], viewonly=True)

    def to_dict(self):
        return {
            'id': self.id,
            'elder_id': self.elder_id,
            'elder_name': self.elder.name if self.elder else None,
            'nursing_type': self.nursing_type,
            'description': self.description,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else None,
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else None,
            'status': self.status,
            'status_name': self.get_status_display(),
            'staff_id': self.staff_id,
            'staff_name': self.staff.name if self.staff else None,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def get_nursing_type_display(self):
        type_map = {
            1: '日常照护', 2: '医疗护理', 3: '康复训练',
            4: '心理疏导', 5: '饮食护理', 6: '清洁护理', 7: '安全护理'
        }
        return type_map.get(self.nursing_type, '未知')

    def get_status_display(self):
        status_map = {1: '进行中', 2: '已完成'}
        return status_map.get(self.status, '未知')
