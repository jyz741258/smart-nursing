from flask import request
from . import checkin_bp
from ..models import User, CheckinRecord
from ..extensions import db
from ..utils.auth import require_token
from ..utils.response import api_response, api_error
import datetime


@checkin_bp.route('/', methods=['POST'])
@require_token
def checkin(current_user):
    """执行打卡"""
    # 检查今天是否已经打卡
    today = datetime.date.today()
    existing_checkin = CheckinRecord.query.filter_by(
        user_id=current_user.id,
        date=today
    ).first()
    
    if existing_checkin:
        return api_error('今日已打卡')
    
    # 创建新的打卡记录
    checkin_record = CheckinRecord(
        user_id=current_user.id,
        date=today,
        time=datetime.datetime.now().time()
    )
    
    db.session.add(checkin_record)
    db.session.commit()
    
    return api_response({
        'date': today.strftime('%Y-%m-%d'),
        'time': checkin_record.time.strftime('%H:%M:%S')
    }, '打卡成功')


@checkin_bp.route('/history', methods=['GET'])
@require_token
def get_checkin_history(current_user):
    """获取打卡历史"""
    records = CheckinRecord.query.filter_by(
        user_id=current_user.id
    ).order_by(CheckinRecord.date.desc(), CheckinRecord.time.desc()).all()
    
    history = []
    for record in records:
        history.append({
            'date': record.date.strftime('%Y-%m-%d'),
            'time': record.time.strftime('%H:%M:%S')
        })
    
    return api_response(history)


@checkin_bp.route('/stats', methods=['GET'])
@require_token
def get_checkin_stats(current_user):
    """获取打卡统计"""
    records = CheckinRecord.query.filter_by(user_id=current_user.id).order_by(CheckinRecord.date).all()
    
    # 计算总打卡次数
    total_checkins = len(records)
    
    # 计算连续打卡天数
    consecutive_days = 0
    if records:
        today = datetime.date.today()
        check_date = today
        
        while True:
            if any(record.date == check_date for record in records):
                consecutive_days += 1
                check_date = check_date - datetime.timedelta(days=1)
            else:
                break
    
    # 计算本月打卡次数
    now = datetime.datetime.now()
    monthly_checkins = len([r for r in records if r.date.month == now.month and r.date.year == now.year])
    
    # 计算本周打卡次数
    week_start = now - datetime.timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    weekly_checkins = len([r for r in records if r.date >= week_start.date()])
    
    # 计算最长连续打卡天数
    max_consecutive = 0
    current_consecutive = 1
    
    for i in range(1, len(records)):
        prev_date = records[i-1].date
        curr_date = records[i].date
        
        if (prev_date - curr_date).days == 1:
            current_consecutive += 1
            max_consecutive = max(max_consecutive, current_consecutive)
        else:
            current_consecutive = 1
    
    max_consecutive = max(max_consecutive, 1) if records else 0
    
    return api_response({
        'total_checkins': total_checkins,
        'consecutive_days': consecutive_days,
        'monthly_checkins': monthly_checkins,
        'weekly_checkins': weekly_checkins,
        'max_consecutive_days': max_consecutive
    })
