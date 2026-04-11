from datetime import datetime
from ..extensions import db


class HealthMetric(db.Model):
    """健康指标模型"""
    __tablename__ = 'health_metrics'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    elder_id = db.Column(db.Integer, nullable=False, comment='老人ID')
    
    # 指标类型: 1-体温, 2-血压-收缩压, 3-血压-舒张压, 4-心率, 5-血氧, 6-血糖, 7-体重, 8-身高
    metric_type = db.Column(db.SmallInteger, nullable=False, comment='指标类型')
    metric_value = db.Column(db.Numeric(10, 2), nullable=False, comment='指标值')
    unit = db.Column(db.String(20), comment='单位')
    recorded_by = db.Column(db.Integer, comment='记录人ID')
    recorded_at = db.Column(db.DateTime, default=datetime.now, comment='记录时间')
    notes = db.Column(db.Text, comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

    # 关系（使用 primaryjoin 指定连接条件，因为没有外键）
    recorder = db.relationship('User', primaryjoin='HealthMetric.recorded_by == User.id', foreign_keys=[recorded_by], viewonly=True)

    def to_dict(self):
        return {
            'id': self.id,
            'elder_id': self.elder_id,
            'elder_name': self.elder.name if self.elder else None,
            'metric_type': self.metric_type,
            'metric_value': float(self.metric_value) if self.metric_value else 0,
            'unit': self.unit,
            'recorded_by': self.recorded_by,
            'recorded_at': self.recorded_at.strftime('%Y-%m-%d %H:%M:%S') if self.recorded_at else None,
            'notes': self.notes
        }

    def get_metric_type_display(self):
        type_map = {
            1: '体温', 2: '血压-收缩压', 3: '血压-舒张压',
            4: '心率', 5: '血氧', 6: '血糖', 7: '体重', 8: '身高',
            9: '睡眠时长', 10: '今日步数'
        }
        return type_map.get(self.metric_type, '未知')
