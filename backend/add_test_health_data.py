from app import create_app
from app.extensions import db
from app.models import HealthMetric
from datetime import datetime

# 创建应用实例
app = create_app('default')

# 在应用上下文中添加测试数据
with app.app_context():
    # 为老人ID=1添加测试健康数据
    elder_id = 1
    
    # 血压数据（收缩压和舒张压）
    blood_pressure_high = HealthMetric(
        elder_id=elder_id,
        metric_type=2,  # 血压-收缩压
        metric_value=145,
        unit='mmHg',
        recorded_by=1,
        recorded_at=datetime.now()
    )
    
    blood_pressure_low = HealthMetric(
        elder_id=elder_id,
        metric_type=3,  # 血压-舒张压
        metric_value=92,
        unit='mmHg',
        recorded_by=1,
        recorded_at=datetime.now()
    )
    
    # 心率数据
    heart_rate = HealthMetric(
        elder_id=elder_id,
        metric_type=4,  # 心率
        metric_value=72,
        unit='次/分',
        recorded_by=1,
        recorded_at=datetime.now()
    )
    
    # 睡眠时长数据
    sleep_hours = HealthMetric(
        elder_id=elder_id,
        metric_type=9,  # 睡眠时长
        metric_value=7.5,
        unit='h',
        recorded_by=1,
        recorded_at=datetime.now()
    )
    
    # 今日步数数据
    steps = HealthMetric(
        elder_id=elder_id,
        metric_type=10,  # 今日步数
        metric_value=3200,
        unit='步',
        recorded_by=1,
        recorded_at=datetime.now()
    )
    
    # 添加到数据库
    db.session.add_all([blood_pressure_high, blood_pressure_low, heart_rate, sleep_hours, steps])
    db.session.commit()
    
    print("测试健康数据添加成功！")
    print(f"为老人ID={elder_id}添加了以下健康数据：")
    print(f"  血压-收缩压: 145 mmHg")
    print(f"  血压-舒张压: 92 mmHg")
    print(f"  心率: 72 次/分")
    print(f"  睡眠时长: 7.5 h")
    print(f"  今日步数: 3200 步")
