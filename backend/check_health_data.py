from app import create_app
from app.extensions import db
from app.models import HealthMetric

# 创建应用实例
app = create_app('default')

# 在应用上下文中查询数据
with app.app_context():
    # 查询所有健康数据记录
    all_metrics = HealthMetric.query.all()
    print(f"总共有 {len(all_metrics)} 条健康数据记录")
    
    # 按老人ID分组查询
    elder_ids = set()
    for metric in all_metrics:
        elder_ids.add(metric.elder_id)
    
    print(f"涉及的老人ID: {elder_ids}")
    
    # 查询每个老人的最新健康数据
    for elder_id in elder_ids:
        print(f"\n老人ID {elder_id} 的最新健康数据:")
        metric_types = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        for metric_type in metric_types:
            metric = HealthMetric.query.filter_by(
                elder_id=elder_id,
                metric_type=metric_type
            ).order_by(HealthMetric.recorded_at.desc()).first()
            if metric:
                print(f"  {metric.get_metric_type_display()}: {metric.metric_value} {metric.unit}")
            else:
                print(f"  {metric.get_metric_type_display()}: 无记录")
