from datetime import datetime
from ..extensions import db


class CarePlan(db.Model):
    """护理计划模型"""
    __tablename__ = 'care_plans'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    elder_id = db.Column(db.Integer, nullable=False, comment='老人ID')
    title = db.Column(db.String(100), nullable=False, comment='计划标题')
    description = db.Column(db.Text, comment='计划描述')
    start_date = db.Column(db.Date, comment='开始日期')
    end_date = db.Column(db.Date, comment='结束日期')
    
    # 状态: 1-执行中, 2-已完成, 3-已暂停
    status = db.Column(db.SmallInteger, default=1, comment='状态')
    
    created_by = db.Column(db.Integer, comment='创建人ID')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系（使用 primaryjoin 指定连接条件，因为没有外键）
    elder = db.relationship('User', primaryjoin='CarePlan.elder_id == User.id', foreign_keys=[elder_id], backref='care_plans', viewonly=True)
    tasks = db.relationship('CareTask', backref='care_plan', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'elder_id': self.elder_id,
            'elder_name': self.elder.name if self.elder else None,
            'title': self.title,
            'description': self.description,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
            'status': self.status,
            'status_name': self.get_status_display(),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def get_status_display(self):
        status_map = {1: '执行中', 2: '已完成', 3: '已暂停'}
        return status_map.get(self.status, '未知')


class CareTask(db.Model):
    """护理任务模型"""
    __tablename__ = 'care_tasks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    care_plan_id = db.Column(db.Integer, db.ForeignKey('care_plans.id'), nullable=False, comment='护理计划ID')
    task_name = db.Column(db.String(100), nullable=False, comment='任务名称')
    task_type = db.Column(db.String(50), comment='任务类型')
    description = db.Column(db.Text, comment='任务描述')
    frequency = db.Column(db.String(50), comment='执行频率')
    scheduled_time = db.Column(db.DateTime, comment='计划时间')
    
    # 状态: 1-待执行, 2-已完成, 3-已取消
    status = db.Column(db.SmallInteger, default=1, comment='状态')
    
    completed_at = db.Column(db.DateTime, comment='完成时间')
    completed_by = db.Column(db.Integer, comment='完成人ID')
    notes = db.Column(db.Text, comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def to_dict(self):
        return {
            'id': self.id,
            'care_plan_id': self.care_plan_id,
            'task_name': self.task_name,
            'task_type': self.task_type,
            'description': self.description,
            'frequency': self.frequency,
            'scheduled_time': self.scheduled_time.strftime('%Y-%m-%d %H:%M:%S') if self.scheduled_time else None,
            'status': self.status,
            'status_name': self.get_status_display(),
            'completed_at': self.completed_at.strftime('%Y-%m-%d %H:%M:%S') if self.completed_at else None,
            'notes': self.notes
        }

    def get_status_display(self):
        status_map = {1: '待执行', 2: '已完成', 3: '已取消'}
        return status_map.get(self.status, '未知')
