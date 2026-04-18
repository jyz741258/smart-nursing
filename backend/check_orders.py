#!/usr/bin/env python
"""查询订单数据"""
from app import create_app, db
from app.models import Order

app = create_app()
with app.app_context():
    total = Order.query.count()
    print(f"数据库中的总订单数: {total}")

    orders = Order.query.limit(10).all()
    print(f"\n前10个订单:")
    for o in orders:
        print(f"  ID:{o.id}, 状态:{o.status}, 金额:{o.actual_amount}, 时间:{o.created_at}")
