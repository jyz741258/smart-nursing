from app import create_app
from app.extensions import db
from app.models import Service

# 创建应用实例
app = create_app('default')

# 在应用上下文中查询数据
with app.app_context():
    # 查询所有服务
    services = Service.query.all()
    print(f"总共有 {len(services)} 条服务数据")
    
    # 打印每条服务的信息
    for i, service in enumerate(services):
        print(f"\n服务 {i+1}:")
        print(f"ID: {service.id}")
        print(f"名称: {service.name}")
        print(f"类别: {service.category}")
        print(f"价格: ¥{service.price}")
        print(f"单位: {service.unit}")
        print(f"时长: {service.duration}分钟")
        print(f"状态: {'上架' if service.status == 1 else '下架'}")
        print(f"是否推荐: {'是' if service.is_recommended == 1 else '否'}")
