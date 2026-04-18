"""使用Flask CLI方式查询"""
import sys
import os

# 设置环境变量
os.environ['FLASK_APP'] = 'run.py'
os.chdir(r'C:\Users\Jyz74\smart-nursing\backend')

# 导入Flask应用
sys.path.insert(0, '.')
from app import create_app, db
from app.models import Order

app = create_app()
with app.app_context():
    print("=== 通过SQLAlchemy查询 ===")
    total = Order.query.count()
    print(f"总订单数: {total}")
    
    from sqlalchemy import func
    stats = db.session.query(Order.status, func.count(Order.id)).group_by(Order.status).order_by(Order.status).all()
    print("状态统计:")
    status_names = {0: '已取消', 1: '待支付', 2: '待服务', 3: '服务中', 4: '已完成', 5: '已退款'}
    for status, cnt in stats:
        print(f"  {status}({status_names.get(status, '未知')}): {cnt}条")
    
    # 样本订单
    sample = Order.query.order_by(Order.id.desc()).limit(5).all()
    print("\n最近5条订单:")
    for o in sample:
        print(f"  ID={o.id}, status={o.status}, order_no={o.order_no}")
