from app import create_app
from app.extensions import db
from app.models import HealthMetric
from datetime import datetime, timedelta
import random

# 创建应用实例
app = create_app('default')

# 在应用上下文中添加测试数据
with app.app_context():
    elder_id = 5

    # 先删除旧数据（如果存在）
    HealthMetric.query.filter_by(elder_id=elder_id).delete()

    # 生成近30天的历史数据
    today = datetime.now()

    # 1. 体温数据（每天2次，早晚）
    for days_ago in range(30):
        for time_offset in [8, 20]:  # 早上8点和晚上8点
            recorded_at = today - timedelta(days=days_ago, hours=time_offset - datetime.now().hour)
            temp = round(random.uniform(36.2, 37.0), 1)
            metric = HealthMetric(
                elder_id=elder_id,
                metric_type=1,  # 体温
                metric_value=temp,
                unit='℃',
                recorded_by=2,
                recorded_at=recorded_at
            )
            db.session.add(metric)

    # 2. 血压数据（每天3次）
    for days_ago in range(30):
        for hour in [8, 12, 18]:
            recorded_at = today - timedelta(days=days_ago, hours=hour)
            systolic = random.randint(120, 145)
            diastolic = random.randint(75, 95)

            metric_high = HealthMetric(
                elder_id=elder_id,
                metric_type=2,  # 血压-收缩压
                metric_value=systolic,
                unit='mmHg',
                recorded_by=2,
                recorded_at=recorded_at
            )
            metric_low = HealthMetric(
                elder_id=elder_id,
                metric_type=3,  # 血压-舒张压
                metric_value=diastolic,
                unit='mmHg',
                recorded_by=2,
                recorded_at=recorded_at
            )
            db.session.add(metric_high)
            db.session.add(metric_low)

    # 3. 心率数据（每天3次）
    for days_ago in range(30):
        for hour in [8, 12, 18]:
            recorded_at = today - timedelta(days=days_ago, hours=hour)
            heart_rate = random.randint(65, 85)
            metric = HealthMetric(
                elder_id=elder_id,
                metric_type=4,  # 心率
                metric_value=heart_rate,
                unit='次/分',
                recorded_by=2,
                recorded_at=recorded_at
            )
            db.session.add(metric)

    # 4. 血氧数据（每天2次）
    for days_ago in range(30):
        for hour in [9, 19]:
            recorded_at = today - timedelta(days=days_ago, hours=hour)
            oxygen = random.randint(95, 99)
            metric = HealthMetric(
                elder_id=elder_id,
                metric_type=5,  # 血氧
                metric_value=oxygen,
                unit='%',
                recorded_by=2,
                recorded_at=recorded_at
            )
            db.session.add(metric)

    # 5. 血糖数据（每天2次，空腹和餐后）
    for days_ago in range(30):
        for hour, base_val in [(7, 5.0), (9, 7.5), (12, 8.5), (18, 8.0)]:
            recorded_at = today - timedelta(days=days_ago, hours=hour)
            blood_sugar = round(base_val + random.uniform(-0.5, 0.5), 1)
            metric = HealthMetric(
                elder_id=elder_id,
                metric_type=6,  # 血糖
                metric_value=blood_sugar,
                unit='mmol/L',
                recorded_by=2,
                recorded_at=recorded_at
            )
            db.session.add(metric)

    # 6. 体重数据（每周2次）
    base_weight = 62.5
    for weeks_ago in range(10):
        for day_offset in [1, 4]:
            recorded_at = today - timedelta(weeks=weeks_ago, days=day_offset)
            weight = round(base_weight + random.uniform(-0.5, 0.5), 1)
            metric = HealthMetric(
                elder_id=elder_id,
                metric_type=7,  # 体重
                metric_value=weight,
                unit='kg',
                recorded_by=2,
                recorded_at=recorded_at
            )
            db.session.add(metric)

    # 7. 身高数据（每月1次，基本不变）
    metric_height = HealthMetric(
        elder_id=elder_id,
        metric_type=8,  # 身高
        metric_value=168.0,
        unit='cm',
        recorded_by=2,
        recorded_at=today
    )
    db.session.add(metric_height)

    # 8. 睡眠时长数据（每天1次）
    for days_ago in range(30):
        recorded_at = today - timedelta(days=days_ago, hours=8)  # 记录次日早上
        sleep_hours = round(random.uniform(6.5, 8.5), 1)
        metric = HealthMetric(
            elder_id=elder_id,
            metric_type=9,  # 睡眠时长
            metric_value=sleep_hours,
            unit='h',
            recorded_by=2,
            recorded_at=recorded_at
        )
        db.session.add(metric)

    # 9. 今日步数数据（每天1次）
    for days_ago in range(30):
        recorded_at = today - timedelta(days=days_ago)
        steps = random.randint(3000, 8500)
        metric = HealthMetric(
            elder_id=elder_id,
            metric_type=10,  # 今日步数
            metric_value=steps,
            unit='步',
            recorded_by=2,
            recorded_at=recorded_at
        )
        db.session.add(metric)

    # 提交所有数据
    db.session.commit()

    print("=" * 50)
    print("老人ID=5 的测试健康数据添加成功！")
    print("=" * 50)
    print(f"数据生成时间范围：近30天")
    print()
    print("包含以下数据：")
    print("  - 体温：60条（每天2次）")
    print("  - 血压：180条（每天3次收缩压+舒张压）")
    print("  - 心率：90条（每天3次）")
    print("  - 血氧：60条（每天2次）")
    print("  - 血糖：120条（每天4次）")
    print("  - 体重：20条（每周2次）")
    print("  - 身高：1条")
    print("  - 睡眠时长：30条（每天1次）")
    print("  - 今日步数：30条（每天1次）")
    print()
    print(f"总计：约591条健康数据记录")
    print("=" * 50)
