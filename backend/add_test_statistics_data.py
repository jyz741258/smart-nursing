from app import create_app
from app.extensions import db
from app.models import NursingRecord, CarePlan, CareTask, HealthMetric
from datetime import datetime, timedelta

# 创建应用实例
app = create_app('default')

# 在应用上下文中添加测试数据
with app.app_context():
    # 添加护理记录
    nursing_records = [
        NursingRecord(
            elder_id=2,
            nursing_type=1,  # 日常照护
            description='协助老人进行日常清洁和起居照料',
            start_time=datetime.now() - timedelta(days=1, hours=2),
            end_time=datetime.now() - timedelta(days=1, hours=1),
            status=2,  # 已完成
            staff_id=3,
            notes='老人状态良好'
        ),
        NursingRecord(
            elder_id=4,
            nursing_type=2,  # 医疗护理
            description='测量血压和心率，协助服药',
            start_time=datetime.now() - timedelta(days=2, hours=3),
            end_time=datetime.now() - timedelta(days=2, hours=2),
            status=2,  # 已完成
            staff_id=6,
            notes='血压偏高，已提醒按时服药'
        ),
        NursingRecord(
            elder_id=5,
            nursing_type=3,  # 康复训练
            description='协助进行肢体康复训练',
            start_time=datetime.now() - timedelta(days=3, hours=1),
            end_time=datetime.now() - timedelta(days=3),
            status=2,  # 已完成
            staff_id=3,
            notes='训练效果良好'
        ),
        NursingRecord(
            elder_id=2,
            nursing_type=4,  # 心理疏导
            description='与老人聊天，进行心理疏导',
            start_time=datetime.now() - timedelta(days=4, hours=2),
            end_time=datetime.now() - timedelta(days=4, hours=1),
            status=2,  # 已完成
            staff_id=6,
            notes='老人情绪稳定'
        ),
        NursingRecord(
            elder_id=4,
            nursing_type=1,  # 日常照护
            description='协助老人进食和饮水',
            start_time=datetime.now() - timedelta(days=5, hours=1),
            end_time=datetime.now() - timedelta(days=5),
            status=2,  # 已完成
            staff_id=3,
            notes='老人食欲良好'
        )
    ]
    db.session.add_all(nursing_records)
    
    # 添加护理计划
    care_plan = CarePlan(
        elder_id=2,
        title='日常护理计划',
        description='为老人制定的日常护理计划',
        start_date=datetime.now() - timedelta(days=7),
        end_date=datetime.now() + timedelta(days=7),
        status=1,  # 进行中
        created_by=1
    )
    db.session.add(care_plan)
    db.session.flush()  # 获取care_plan.id
    
    # 添加护理任务
    care_tasks = [
        CareTask(
            care_plan_id=care_plan.id,
            task_name='测量血压',
            task_type=1,
            description='每天上午9点测量老人血压',
            frequency='每天',
            scheduled_time=datetime.now().replace(hour=9, minute=0, second=0, microsecond=0),
            status=2,  # 已完成
            completed_at=datetime.now() - timedelta(hours=1),
            completed_by=3,
            notes='血压正常'
        ),
        CareTask(
            care_plan_id=care_plan.id,
            task_name='协助康复训练',
            task_type=2,
            description='每天下午3点协助老人进行康复训练',
            frequency='每天',
            scheduled_time=datetime.now().replace(hour=15, minute=0, second=0, microsecond=0),
            status=1,  # 待执行
            notes='需要护理人员协助'
        ),
        CareTask(
            care_plan_id=care_plan.id,
            task_name='更换床单',
            task_type=3,
            description='每周一更换老人床单',
            frequency='每周',
            scheduled_time=datetime.now().replace(hour=10, minute=0, second=0, microsecond=0),
            status=2,  # 已完成
            completed_at=datetime.now() - timedelta(days=2),
            completed_by=6,
            notes='床单已更换'
        )
    ]
    db.session.add_all(care_tasks)
    
    # 添加带有异常标记的健康指标记录
    health_alert = HealthMetric(
        elder_id=4,
        metric_type=2,  # 血压-收缩压
        metric_value=160,
        unit='mmHg',
        recorded_by=6,
        recorded_at=datetime.now() - timedelta(hours=2),
        notes='血压异常偏高，需要关注'
    )
    db.session.add(health_alert)
    
    # 提交所有更改
    db.session.commit()
    
    print("测试统计数据添加成功！")
    print(f"添加了 {len(nursing_records)} 条护理记录")
    print(f"添加了 1 个护理计划")
    print(f"添加了 {len(care_tasks)} 个护理任务")
    print(f"添加了 1 条异常健康指标记录")
