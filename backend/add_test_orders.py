# -*- coding: utf-8 -*-
"""添加测试订单数据"""
from app import create_app
from app.extensions import db
from app.models import Order, Service, User
from datetime import datetime, timedelta
import random

app = create_app('default')


def add_test_orders():
    """添加测试订单数据"""
    with app.app_context():
        # 获取现有的服务和用户
        services = Service.query.all()
        elders = User.query.filter_by(user_type=1).all()
        nurses = User.query.filter_by(user_type=2).all()
        users = User.query.filter(User.user_type.in_([1, 4])).all()  # 老人和家属

        if not services:
            print("没有找到服务数据，请先运行 add_test_services.py")
            return
        if not elders:
            print("没有找到老人用户数据，请先运行 init_test_data.py")
            return

        print(f"找到 {len(services)} 个服务")
        print(f"找到 {len(elders)} 个老人")
        print(f"找到 {len(nurses)} 个护理人员")
        print(f"找到 {len(users)} 个可下单用户")

        # 服务名称和定价对应
        service_prices = {
            '日常照护': 80.00,
            '医疗护理': 120.00,
            '康复训练': 150.00,
            '心理疏导': 100.00,
            '营养膳食': 60.00,
            '清洁护理': 50.00,
            '安全监护': 200.00,
            '陪同就医': 150.00
        }

        # 订单状态
        statuses = [1, 2, 4]  # 待支付, 待服务, 已完成
        status_names = {1: '待支付', 2: '待服务', 4: '已完成'}

        # 创建测试订单
        orders = []

        # 为每个老人创建订单
        for elder in elders:
            # 随机选择下单用户
            if users:
                order_user = random.choice(users)
            else:
                order_user = elder

            # 创建 3-5 个订单
            num_orders = random.randint(3, 5)
            for i in range(num_orders):
                service = random.choice(services)
                status = random.choice(statuses)

                # 生成下单时间（最近30天内）
                days_ago = random.randint(0, 30)
                hours_ago = random.randint(0, 23)
                order_time = datetime.now() - timedelta(days=days_ago, hours=hours_ago)

                # 预约时间
                appointment_date = (order_time + timedelta(days=random.randint(1, 7))).date()

                # 预约时间段
                time_slots = ['上午 9:00-12:00', '下午 14:00-17:00', '晚上 18:00-21:00']
                appointment_time = random.choice(time_slots)

                # 计算价格
                price = service_prices.get(service.name, service.price)

                # 创建订单
                order = Order(
                    order_no=f"ORD{datetime.now().strftime('%Y%m%d')}{str(len(orders)+1).zfill(4)}",
                    user_id=order_user.id,
                    service_id=service.id,
                    elder_id=elder.id,
                    nurse_id=nurses[0].id if nurses and status >= 2 else None,
                    total_amount=price,
                    actual_amount=price,
                    service_name=service.name,
                    service_price=price,
                    order_time=order_time,
                    appointment_date=appointment_date,
                    appointment_time=appointment_time,
                    status=status,
                    notes=f"为{elder.real_name or elder.username}预约的{service.name}服务",
                    created_by=order_user.id,
                    created_at=order_time
                )

                # 如果已完成，设置完成时间
                if status == 4:
                    # 时间段格式: "上午 9:00-12:00" 或 "下午 14:00-17:00"
                    time_part = appointment_time.split(' ')[1]  # "14:00-17:00"
                    end_time = time_part.split('-')[1]  # "17:00"
                    order.completion_time = datetime.strptime(
                        appointment_date.strftime('%Y-%m-%d') + ' ' + end_time,
                        '%Y-%m-%d %H:%M'
                    )

                orders.append(order)

        # 添加到数据库
        db.session.add_all(orders)
        db.session.commit()

        print(f"成功添加了 {len(orders)} 条测试订单数据！")

        # 打印订单统计
        print("\n订单统计：")
        for status, name in status_names.items():
            count = Order.query.filter_by(status=status).count()
            print(f"  {name}: {count} 条")


if __name__ == '__main__':
    add_test_orders()
