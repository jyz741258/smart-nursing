import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models import CheckinRecord, User

app = create_app()

with app.app_context():
    # 获取所有用户
    users = User.query.all()
    
    if not users:
        print("没有用户数据，请先运行init_test_data.py")
        sys.exit(1)
    
    # 为每个用户添加一些打卡记录
    for user in users:
        # 为每个用户添加最近7天的打卡记录
        for i in range(7):
            date = datetime.now().date() - timedelta(days=i)
            # 检查是否已经存在该日期的打卡记录
            existing = CheckinRecord.query.filter_by(user_id=user.id, date=date).first()
            if not existing:
                # 为每个用户在不同时间打卡
                hour = 8 + (user.id % 3)  # 不同用户不同时间
                minute = user.id * 10 % 60
                time = datetime.now().time().replace(hour=hour, minute=minute, second=0)
                
                checkin = CheckinRecord(
                    user_id=user.id,
                    date=date,
                    time=time
                )
                db.session.add(checkin)
    
    # 提交所有更改
    db.session.commit()
    print("测试打卡记录添加成功！")
