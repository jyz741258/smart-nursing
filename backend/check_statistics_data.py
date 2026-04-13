from app import create_app
from app.extensions import db
from app.models import NursingRecord, CarePlan, CareTask, HealthMetric

# 创建应用实例
app = create_app('default')

# 在应用上下文中查询数据
with app.app_context():
    # 查询护理记录
    nursing_records = NursingRecord.query.all()
    print(f"总共有 {len(nursing_records)} 条护理记录")
    
    # 查询护理计划
    care_plans = CarePlan.query.all()
    print(f"总共有 {len(care_plans)} 个护理计划")
    
    # 查询护理任务
    care_tasks = CareTask.query.all()
    print(f"总共有 {len(care_tasks)} 个护理任务")
    
    # 查询健康指标
    health_metrics = HealthMetric.query.all()
    print(f"总共有 {len(health_metrics)} 条健康指标记录")
    
    # 查询有异常标记的健康指标
    health_alerts = HealthMetric.query.filter(HealthMetric.notes.like('%异常%')).all()
    print(f"总共有 {len(health_alerts)} 条异常健康指标记录")
