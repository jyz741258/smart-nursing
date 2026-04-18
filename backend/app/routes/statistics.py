from flask import request
from datetime import datetime, timedelta
from sqlalchemy import func
from . import statistics_bp
from ..extensions import db
from ..models import User, NursingRecord, HealthMetric, CareTask, CarePlan
from ..utils.response import api_response, page_response
from ..utils import require_token


@statistics_bp.route('/dashboard', methods=['GET'])
@require_token
def get_dashboard(current_user):
    """获取仪表盘统计"""
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    # 今日护理记录数
    today_nursing_count = NursingRecord.query.filter(
        NursingRecord.created_at >= today_start,
        NursingRecord.created_at <= today_end
    ).count()

    # 今日完成任务数
    today_completed_tasks = CareTask.query.filter(
        CareTask.completed_at >= today_start,
        CareTask.completed_at <= today_end
    ).count()

    # 老人总数
    elder_count = User.query.filter_by(user_type=1).count()

    # 护理人员数
    staff_count = User.query.filter_by(user_type=2).count()

    # 家属数量
    family_count = User.query.filter_by(user_type=4).count()

    # 待处理任务数
    pending_tasks = CareTask.query.filter_by(status=1).count()

    # 今日订单数（假设订单模型存在）
    today_orders = 0
    try:
        from ..models import Order
        today_orders = Order.query.filter(
            Order.created_at >= today_start,
            Order.created_at <= today_end
        ).count()
    except ImportError:
        pass

    return api_response({
        'today_nursing_count': today_nursing_count,
        'today_completed_tasks': today_completed_tasks,
        'elder_count': elder_count,
        'staff_count': staff_count,
        'family_count': family_count,
        'today_orders': today_orders,
        'pending_tasks': pending_tasks
    })


@statistics_bp.route('/nursing-summary', methods=['GET'])
@require_token
def get_nursing_summary(current_user):
    """获取护理统计摘要"""
    days = request.args.get('days', 7, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)

    # 按类型统计护理记录
    summary = db.session.query(
        NursingRecord.nursing_type,
        func.count(NursingRecord.id).label('count')
    ).filter(
        NursingRecord.created_at >= start_date
    ).group_by(NursingRecord.nursing_type).all()

    nursing_stats = [{
        'nursing_type': s[0],
        'count': s[1]
    } for s in summary]

    return api_response(nursing_stats)


@statistics_bp.route('/health-trend', methods=['GET'])
@require_token
def get_health_trend(current_user):
    """获取健康指标趋势"""
    elder_id = request.args.get('elder_id', type=int)
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)

    query = HealthMetric.query.filter(
        HealthMetric.recorded_at >= start_date
    )

    if elder_id:
        query = query.filter_by(elder_id=elder_id)

    metrics = query.order_by(HealthMetric.recorded_at.asc()).all()

    trend = {}
    for m in metrics:
        date_str = m.recorded_at.strftime('%Y-%m-%d')
        if date_str not in trend:
            trend[date_str] = {}
        type_name = m.get_metric_type_display()
        if type_name not in trend[date_str]:
            trend[date_str][type_name] = []
        trend[date_str][type_name].append({
            'value': m.metric_value,
            'unit': m.unit,
            'time': m.recorded_at.isoformat()
        })

    return api_response(trend)


@statistics_bp.route('/workload', methods=['GET'])
@require_token
def get_staff_workload(current_user):
    """获取护理人员工作量统计"""
    days = request.args.get('days', 7, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)

    workload = db.session.query(
        NursingRecord.staff_id,
        func.count(NursingRecord.id).label('record_count')
    ).filter(
        NursingRecord.created_at >= start_date,
        NursingRecord.staff_id.isnot(None)
    ).group_by(
        NursingRecord.staff_id
    ).all()
    
    # 为每个工作量添加护理人员姓名
    workload_with_names = []
    for w in workload:
        staff = User.query.get(w[0])
        workload_with_names.append({
            'staff_id': w[0],
            'staff_name': staff.name if staff else '未知',
            'record_count': w[1]
        })

    return api_response(workload_with_names)


@statistics_bp.route('/alerts', methods=['GET'])
@require_token
def get_health_alerts(current_user):
    """获取健康预警统计"""
    days = request.args.get('days', 7, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)

    # 获取异常指标
    alerts = HealthMetric.query.filter(
        HealthMetric.recorded_at >= start_date,
        HealthMetric.notes.like('%异常%')
    ).order_by(HealthMetric.recorded_at.desc()).limit(20).all()

    return api_response([{
        'elder_id': a.elder_id,
        'elder_name': a.elder.name if a.elder else None,
        'metric_type': a.metric_type,
        'metric_type_name': a.get_metric_type_display(),
        'metric_value': a.metric_value,
        'unit': a.unit,
        'recorded_at': a.recorded_at.isoformat(),
        'notes': a.notes
    } for a in alerts])


@statistics_bp.route('/care-plan-progress', methods=['GET'])
@require_token
def get_care_plan_progress(current_user):
    """获取护理计划执行进度"""
    plans = CarePlan.query.filter_by(status=1).all()

    progress = []
    for plan in plans:
        total_tasks = CareTask.query.filter_by(care_plan_id=plan.id).count()
        completed_tasks = CareTask.query.filter_by(
            care_plan_id=plan.id,
            status=2
        ).count()

        progress.append({
            'plan_id': plan.id,
            'title': plan.title,
            'elder_name': plan.elder.name if plan.elder else None,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'progress_rate': round(completed_tasks / total_tasks * 100, 2) if total_tasks > 0 else 0
        })

    return api_response(progress)


@statistics_bp.route('/weekly-nursing', methods=['GET'])
@require_token
def get_weekly_nursing(current_user):
    """获取护理记录统计（按日分组，支持本周或本月）"""
    period = request.args.get('period', 'week')  # 默认本周
    today = datetime.utcnow().date()

    if period == 'week':
        # 本周：周一至周日
        weekday = today.weekday()
        start_date = today - timedelta(days=weekday)
        end_date = start_date + timedelta(days=6)
        date_format = '%Y-%m-%d'
        day_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        days_to_generate = 7
    elif period == 'month':
        # 本月：1号至今日（或本月最后一天）
        start_date = today.replace(day=1)
        # 获取本月最后一天
        if today.month == 12:
            end_date = today.replace(month=1, day=1) - timedelta(days=1)
        else:
            end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        date_format = '%m-%d'
        days_to_generate = end_date.day  # 本月天数
        day_names = [str(d) for d in range(1, days_to_generate + 1)]  # 1, 2, 3...
    else:
        return api_error('Invalid period parameter', 400)

    print(f"[Debug] Nursing chart period={period}, start={start_date}, end={end_date}")

    # 查询指定时间范围内的护理记录，按日期分组统计
    query = db.session.query(
        db.func.date(NursingRecord.created_at).label('date'),
        func.count(NursingRecord.id).label('count')
    ).filter(
        NursingRecord.created_at >= datetime.combine(start_date, datetime.min.time()),
        NursingRecord.created_at <= datetime.combine(end_date, datetime.max.time())
    ).group_by(db.func.date(NursingRecord.created_at)).order_by(db.func.date(NursingRecord.created_at))

    results = query.all()
    print(f"[Debug] Raw query results: {results}")

    # 构建完整的数据数组（填充没有记录的日期为0）
    data_map = {str(r.date): r.count for r in results}

    chart_data = []
    for i in range(days_to_generate):
        if period == 'week':
            current_date = start_date + timedelta(days=i)
            label = day_names[i]  # 周一、周二...
            date_key = str(current_date)
        else:  # month
            current_date = start_date.replace(day=i + 1)
            label = f'{i + 1}日'  # 1日、2日...
            date_key = str(current_date)

        chart_data.append({
            'date': date_key,
            'day': label,  # 显示标签
            'count': data_map.get(date_key, 0)
        })

    print(f"[Debug] Chart data: {chart_data}")

    return api_response(chart_data)


@statistics_bp.route('/service-distribution', methods=['GET'])
@require_token
def get_service_distribution(current_user):
    """获取服务类型分布"""
    from ..models import Service

    distribution = db.session.query(
        Service.category,
        func.count(Service.id).label('count')
    ).group_by(Service.category).all()

    # 护理类型映射
    nursing_type_names = {
        1: '日常照护',
        2: '医疗护理',
        3: '康复训练',
        4: '心理疏导',
        5: '饮食护理',
        6: '清洁护理',
        7: '安全护理'
    }

    data = []
    for d in distribution:
        category = d[0] or '其他'
        count = d[1]
        data.append({
            'name': category,
            'value': count
        })

    return api_response(data)
