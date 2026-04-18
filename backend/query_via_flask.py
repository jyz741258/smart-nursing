"""使用Flask应用上下文查询数据库"""
import sys
sys.path.insert(0, r'c:\Users\Jyz74\smart-nursing\backend')

from app import create_app, db
from app.models import Order

app = create_app()
with app.app_context():
    total = Order.query.count()
    print(f"总订单数: {total}")
    
    # 按状态统计
    from sqlalchemy import func
    stats = db.session.query(Order.status, func.count()).group_by(Order.status).order_by(Order.status).all()
    print("状态统计:", stats)
    
    # 最近订单
    recent = Order.query.order_by(Order.id.desc()).limit(5).all()
    print("最近5条订单ID:", [o.id for o in recent])
    print("最近5条订单状态:", [o.status for o in recent])
