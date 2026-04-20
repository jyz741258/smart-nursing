from flask import request
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from collections import defaultdict
from . import bigdata_bp
from ..extensions import db
from ..models import User, NursingRecord, HealthMetric, CareTask, CarePlan
from ..utils.response import api_response, api_error
from ..utils import require_token
import statistics


# 健康指标标准范围
HEALTH_RANGES = {
    1: {'name': '体温', 'min': 36.0, 'max': 37.3, 'unit': '°C'},
    4: {'name': '心率', 'min': 60, 'max': 100, 'unit': 'BPM'},
    5: {'name': '血氧', 'min': 95, 'max': 100, 'unit': '%'},
    6: {'name': '血糖', 'min': 3.9, 'max': 6.1, 'unit': 'mmol/L'},
}


def is_abnormal(metric_type, value):
    """判断指标是否异常"""
    if metric_type in HEALTH_RANGES:
        range_info = HEALTH_RANGES[metric_type]
        return value < range_info['min'] or value > range_info['max']
    return False


def calculate_statistics(values):
    """计算统计数据"""
    if not values:
        return {
            'min': 0, 'max': 0, 'avg': 0, 'median': 0,
            'std': 0, 'count': 0, 'variance': 0
        }
    
    return {
        'min': round(min(values), 2),
        'max': round(max(values), 2),
        'avg': round(statistics.mean(values), 2),
        'median': round(statistics.median(values), 2),
        'std': round(statistics.stdev(values), 2) if len(values) > 1 else 0,
        'count': len(values),
        'variance': round(statistics.variance(values), 2) if len(values) > 1 else 0
    }


@bigdata_bp.route('/health-analysis', methods=['GET'])
@require_token
def get_health_analysis(current_user):
    """获取综合健康分析"""
    elder_id = request.args.get('elder_id', type=int)
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = HealthMetric.query.filter(
        HealthMetric.recorded_at >= start_date
    )
    
    if elder_id:
        query = query.filter_by(elder_id=elder_id)
    
    metrics = query.order_by(HealthMetric.recorded_at.asc()).all()
    
    # 按类型分组
    by_type = defaultdict(list)
    for m in metrics:
        by_type[m.metric_type].append({
            'value': float(m.metric_value),
            'recorded_at': m.recorded_at,
            'elder_id': m.elder_id,
            'notes': m.notes
        })
    
    # 计算每个类型的统计数据
    analysis = {}
    for metric_type, records in by_type.items():
        values = [r['value'] for r in records]
        stats = calculate_statistics(values)
        
        # 计算异常率
        abnormal_count = sum(1 for r in records if is_abnormal(metric_type, r['value']))
        stats['abnormal_rate'] = round(abnormal_count / len(records) * 100, 2) if records else 0
        
        # 获取趋势（最近7天 vs 之前）
        recent = [r for r in records if r['recorded_at'] >= datetime.utcnow() - timedelta(days=7)]
        older = [r for r in records if r['recorded_at'] < datetime.utcnow() - timedelta(days=7)]
        
        if recent and older:
            recent_avg = statistics.mean([r['value'] for r in recent])
            older_avg = statistics.mean([r['value'] for r in older])
            stats['trend'] = 'up' if recent_avg > older_avg else 'down' if recent_avg < older_avg else 'stable'
            stats['trend_percent'] = round((recent_avg - older_avg) / older_avg * 100, 2) if older_avg else 0
        else:
            stats['trend'] = 'stable'
            stats['trend_percent'] = 0
        
        # 获取类型名称
        temp_metric = HealthMetric(metric_type=metric_type, metric_value=0)
        type_name = temp_metric.get_metric_type_display()
        
        # 添加历史数据（最近30条）
        historical = [
            {'date': r['recorded_at'].strftime('%Y-%m-%d'), 'value': r['value']}
            for r in records[-30:]  # 只取最近30条
        ]
        
        analysis[type_name] = {
            'metric_type': metric_type,
            'historical': historical,
            **stats
        }
    
    return api_response(analysis)


@bigdata_bp.route('/elder-health-report', methods=['GET'])
@require_token
def get_elder_health_report(current_user):
    """获取老人健康报告"""
    elder_id = request.args.get('elder_id', type=int)
    if not elder_id:
        return api_error("缺少elder_id参数")
    
    # 获取老人信息
    elder = User.query.get(elder_id)
    if not elder or elder.user_type != 1:
        return api_error("未找到该老人")
    
    # 分析最近30天的数据
    days = 30
    start_date = datetime.utcnow() - timedelta(days=days)
    
    metrics = HealthMetric.query.filter(
        HealthMetric.elder_id == elder_id,
        HealthMetric.recorded_at >= start_date
    ).all()
    
    # 生成报告
    report = {
        'elder_id': elder_id,
        'elder_name': elder.name,
        'elder_age': elder.age,
        'report_date': datetime.utcnow().strftime('%Y-%m-%d'),
        'analysis_period': f'{days}天',
        'summary': {
            'total_records': len(metrics),
            'abnormal_count': 0,
            'health_score': 100
        },
        'metrics': {},
        'recommendations': []
    }
    
    # 按类型统计
    by_type = defaultdict(list)
    for m in metrics:
        by_type[m.metric_type].append(float(m.metric_value))
    
    for metric_type, values in by_type.items():
        temp_metric = HealthMetric(metric_type=metric_type, metric_value=0)
        type_name = temp_metric.get_metric_type_display()
        
        stats = calculate_statistics(values)
        abnormal = sum(1 for v in values if is_abnormal(metric_type, v))
        abnormal_rate = abnormal / len(values) * 100 if values else 0
        
        report['metrics'][type_name] = {
            'stats': stats,
            'abnormal_rate': round(abnormal_rate, 2),
            'latest_value': values[-1] if values else None
        }
        
        report['summary']['abnormal_count'] += abnormal
    
    # 计算健康评分
    if metrics:
        report['summary']['health_score'] = max(0, 100 - report['summary']['abnormal_count'])
    
    # 生成建议
    for metric_name, metric_data in report['metrics'].items():
        if metric_data['abnormal_rate'] > 20:
            report['recommendations'].append({
                'type': 'warning',
                'metric': metric_name,
                'message': f'{metric_name}指标异常率较高({metric_data["abnormal_rate"]}%)，建议密切关注'
            })
    
    return api_response(report)


@bigdata_bp.route('/health-prediction', methods=['GET'])
@require_token
def get_health_prediction(current_user):
    """健康趋势预测（简单线性回归）"""
    elder_id = request.args.get('elder_id', type=int)
    metric_type = request.args.get('metric_type', type=int)
    days = request.args.get('days', 14, type=int)
    predict_days = request.args.get('predict_days', 7, type=int)
    
    if not elder_id or not metric_type:
        return api_error("缺少必要参数")
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    metrics = HealthMetric.query.filter(
        HealthMetric.elder_id == elder_id,
        HealthMetric.metric_type == metric_type,
        HealthMetric.recorded_at >= start_date
    ).order_by(HealthMetric.recorded_at.asc()).all()
    
    if len(metrics) < 3:
        return api_error("数据不足，无法进行预测")
    
    # 准备数据
    values = [float(m.metric_value) for m in metrics]
    times = list(range(len(values)))
    
    # 简单线性回归
    n = len(times)
    sum_x = sum(times)
    sum_y = sum(values)
    sum_xy = sum(x * y for x, y in zip(times, values))
    sum_x2 = sum(x * x for x in times)
    
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x) if (n * sum_x2 - sum_x * sum_x) != 0 else 0
    intercept = (sum_y - slope * sum_x) / n
    
    # 预测未来数据
    predictions = []
    last_date = metrics[-1].recorded_at
    
    for i in range(1, predict_days + 1):
        pred_time = len(values) + i - 1
        pred_value = slope * pred_time + intercept
        pred_date = last_date + timedelta(days=i)
        
        predictions.append({
            'date': pred_date.strftime('%Y-%m-%d'),
            'predicted_value': round(pred_value, 2),
            'confidence': max(0, min(100, 100 - i * 10 - abs(slope) * 10))
        })
    
    temp_metric = HealthMetric(metric_type=metric_type, metric_value=0)
    
    return api_response({
        'metric_type': metric_type,
        'metric_name': temp_metric.get_metric_type_display(),
        'trend': 'rising' if slope > 0 else 'falling' if slope < 0 else 'stable',
        'slope': round(slope, 4),
        'historical': [{'date': m.recorded_at.strftime('%Y-%m-%d'), 'value': float(m.metric_value)} for m in metrics[-7:]],
        'predictions': predictions
    })


@bigdata_bp.route('/nursing-efficiency', methods=['GET'])
@require_token
def get_nursing_efficiency(current_user):
    """护理效率分析"""
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # 统计护理记录
    records = NursingRecord.query.filter(
        NursingRecord.created_at >= start_date
    ).all()
    
    # 按类型统计
    by_type = defaultdict(list)
    for r in records:
        by_type[r.nursing_type].append(r)
    
    efficiency = {}
    type_names = {
        1: '日常照护', 2: '医疗护理', 3: '康复训练',
        4: '健康监测', 5: '心理疏导', 6: '饮食护理'
    }
    
    for nursing_type, recs in by_type.items():
        total = len(recs)
        # 计算平均时长（如果有duration字段）
        durations = [r.duration for r in recs if hasattr(r, 'duration') and r.duration]
        avg_duration = statistics.mean(durations) if durations else 0
        
        efficiency[type_names.get(nursing_type, '其他')] = {
            'count': total,
            'avg_duration': round(avg_duration, 1),
            'percentage': round(total / len(records) * 100, 2) if records else 0
        }
    
    return api_response(efficiency)


@bigdata_bp.route('/care-plan-analysis', methods=['GET'])
@require_token
def get_care_plan_analysis(current_user):
    """护理计划完成度分析"""
    plans = CarePlan.query.filter_by(status=1).all()
    
    analysis = []
    for plan in plans:
        total_tasks = CareTask.query.filter_by(care_plan_id=plan.id).count()
        completed = CareTask.query.filter_by(care_plan_id=plan.id, status=2).count()
        pending = CareTask.query.filter_by(care_plan_id=plan.id, status=1).count()
        overdue = 0
        
        # 检查逾期任务
        pending_tasks = CareTask.query.filter_by(
            care_plan_id=plan.id,
            status=1,
            scheduled_date=datetime.utcnow().date()
        ).all()
        
        for task in pending_tasks:
            if task.scheduled_date < datetime.utcnow().date():
                overdue += 1
        
        completion_rate = completed / total_tasks * 100 if total_tasks > 0 else 0
        
        analysis.append({
            'plan_id': plan.id,
            'plan_title': plan.title,
            'elder_name': plan.elder.name if plan.elder else None,
            'total_tasks': total_tasks,
            'completed': completed,
            'pending': pending,
            'overdue': overdue,
            'completion_rate': round(completion_rate, 2),
            'status': 'excellent' if completion_rate >= 90 else 'good' if completion_rate >= 70 else 'needs_improvement'
        })
    
    return api_response(analysis)


@bigdata_bp.route('/risk-assessment', methods=['GET'])
@require_token
def get_risk_assessment(current_user):
    """老人健康风险评估"""
    elder_id = request.args.get('elder_id', type=int)
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = HealthMetric.query.filter(
        HealthMetric.recorded_at >= start_date
    )
    
    if elder_id:
        query = query.filter_by(elder_id=elder_id)
        elder = User.query.get(elder_id)
        elders = [elder] if elder else []
    else:
        # 获取所有老人
        elders = User.query.filter_by(user_type=1).all()
    
    risk_assessments = []
    
    for elder in elders:
        metrics = query.filter_by(elder_id=elder.id).all()
        
        # 按类型分组
        by_type = defaultdict(list)
        for m in metrics:
            by_type[m.metric_type].append(float(m.metric_value))
        
        risk_score = 0
        risk_factors = []
        
        for metric_type, values in by_type.items():
            if len(values) < 2:
                continue
            
            abnormal_count = sum(1 for v in values if is_abnormal(metric_type, v))
            abnormal_rate = abnormal_count / len(values)
            
            # 根据异常率计算风险分数
            if abnormal_rate > 0.5:
                risk_score += 30
                temp_metric = HealthMetric(metric_type=metric_type, metric_value=0)
                risk_factors.append({
                    'factor': temp_metric.get_metric_type_display(),
                    'risk_level': 'high',
                    'abnormal_rate': round(abnormal_rate * 100, 2)
                })
            elif abnormal_rate > 0.2:
                risk_score += 15
                temp_metric = HealthMetric(metric_type=metric_type, metric_value=0)
                risk_factors.append({
                    'factor': temp_metric.get_metric_type_display(),
                    'risk_level': 'medium',
                    'abnormal_rate': round(abnormal_rate * 100, 2)
                })
        
        # 根据风险分数确定风险等级
        if risk_score >= 60:
            risk_level = 'high'
        elif risk_score >= 30:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        risk_assessments.append({
            'elder_id': elder.id,
            'elder_name': elder.name,
            'elder_age': elder.age,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'assessment_date': datetime.utcnow().strftime('%Y-%m-%d')
        })
    
    return api_response(risk_assessments)


@bigdata_bp.route('/activity-patterns', methods=['GET'])
@require_token
def get_activity_patterns(current_user):
    """获取活动模式分析"""
    elder_id = request.args.get('elder_id', type=int)
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = HealthMetric.query.filter(
        HealthMetric.recorded_at >= start_date,
        HealthMetric.metric_type.in_([9, 10])  # 睡眠时长和步数
    )
    
    if elder_id:
        query = query.filter_by(elder_id=elder_id)
    
    metrics = query.order_by(HealthMetric.recorded_at.asc()).all()
    
    # 按日期统计
    by_date = defaultdict(lambda: {'sleep': [], 'steps': []})
    for m in metrics:
        date_str = m.recorded_at.strftime('%Y-%m-%d')
        if m.metric_type == 9:  # 睡眠
            by_date[date_str]['sleep'].append(float(m.metric_value))
        elif m.metric_type == 10:  # 步数
            by_date[date_str]['steps'].append(float(m.metric_value))
    
    patterns = []
    for date_str, data in sorted(by_date.items()):
        patterns.append({
            'date': date_str,
            'avg_sleep': round(statistics.mean(data['sleep']), 1) if data['sleep'] else None,
            'avg_steps': round(statistics.mean(data['steps']), 0) if data['steps'] else None,
            'activity_level': 'high' if (data['steps'] and sum(data['steps']) / len(data['steps']) > 8000) 
                          else 'medium' if (data['steps'] and sum(data['steps']) / len(data['steps']) > 4000)
                          else 'low'
        })
    
    # 计算周模式
    weekly_pattern = defaultdict(lambda: {'sleep': [], 'steps': []})
    for p in patterns:
        date_obj = datetime.strptime(p['date'], '%Y-%m-%d')
        weekday = date_obj.strftime('%A')
        if p['avg_sleep']:
            weekly_pattern[weekday]['sleep'].append(p['avg_sleep'])
        if p['avg_steps']:
            weekly_pattern[weekday]['steps'].append(p['avg_steps'])
    
    weekly_summary = {}
    for weekday, data in weekly_pattern.items():
        weekly_summary[weekday] = {
            'avg_sleep': round(statistics.mean(data['sleep']), 1) if data['sleep'] else None,
            'avg_steps': round(statistics.mean(data['steps']), 0) if data['steps'] else None
        }
    
    return api_response({
        'daily_patterns': patterns,
        'weekly_summary': weekly_summary
    })


@bigdata_bp.route('/comparison', methods=['GET'])
@require_token
def get_comparison_analysis(current_user):
    """老人健康数据对比分析"""
    elder_ids = request.args.get('elder_ids', type=str)  # 逗号分隔
    metric_type = request.args.get('metric_type', type=int)
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    if not elder_ids:
        return api_error("缺少elder_ids参数")
    
    elder_id_list = [int(eid) for eid in elder_ids.split(',')]
    
    comparison = []
    for elder_id in elder_id_list:
        elder = User.query.get(elder_id)
        if not elder or elder.user_type != 1:
            continue
        
        metrics = HealthMetric.query.filter(
            HealthMetric.elder_id == elder_id,
            HealthMetric.metric_type == metric_type,
            HealthMetric.recorded_at >= start_date
        ).all()
        
        values = [float(m.metric_value) for m in metrics]
        stats = calculate_statistics(values)
        
        temp_metric = HealthMetric(metric_type=metric_type, metric_value=0)
        
        comparison.append({
            'elder_id': elder_id,
            'elder_name': elder.name,
            'elder_age': elder.age,
            'metric_name': temp_metric.get_metric_type_display(),
            'stats': stats,
            'latest_value': values[-1] if values else None,
            'record_count': len(values)
        })
    
    return api_response(comparison)


@bigdata_bp.route('/anomaly-alerts', methods=['GET'])
@require_token
def get_anomaly_alerts(current_user):
    """异常告警列表"""
    elder_id = request.args.get('elder_id', type=int)
    days = request.args.get('days', 7, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = HealthMetric.query.filter(
        HealthMetric.recorded_at >= start_date
    )
    
    if elder_id:
        query = query.filter_by(elder_id=elder_id)
    
    metrics = query.order_by(HealthMetric.recorded_at.desc()).all()
    
    alerts = []
    for m in metrics:
        value = float(m.metric_value)
        if is_abnormal(m.metric_type, value):
            temp_metric = HealthMetric(metric_type=m.metric_type, metric_value=value)
            
            alerts.append({
                'id': m.id,
                'elder_id': m.elder_id,
                'elder_name': m.elder.name if m.elder else None,
                'metric_type': m.metric_type,
                'metric_name': temp_metric.get_metric_type_display(),
                'value': value,
                'unit': m.unit,
                'recorded_at': m.recorded_at.strftime('%Y-%m-%d %H:%M'),
                'severity': 'critical' if m.metric_type in [4, 5] and (value < 50 or value > 120 or value < 90) else 'warning',
                'recommendation': f'建议{m.get_metric_type_display()}异常，请密切关注或就医'
            })
    
    return api_response(alerts)


@bigdata_bp.route('/health-insights', methods=['GET'])
@require_token
def get_health_insights(current_user):
    """健康数据洞察"""
    elder_id = request.args.get('elder_id', type=int)
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)

    query = HealthMetric.query.filter(
        HealthMetric.recorded_at >= start_date
    )

    if elder_id:
        query = query.filter_by(elder_id=elder_id)

    metrics = query.all()

    insights = []

    # 1. 数据完整度分析（按老人计算）
    elder_ids = set(m.elder_id for m in metrics)
    total_expected_records = len(elder_ids) * days  # 每个老人每天应有1条记录

    # 统计实际记录
    days_with_data = len(set(m.recorded_at.strftime('%Y-%m-%d') for m in metrics))

    # 完整度 = 有数据的天数 / 总天数，最大100%
    completeness = min(100, days_with_data / days * 100) if days > 0 else 0

    insights.append({
        'type': 'data_quality',
        'title': '数据完整度',
        'description': f'最近{days}天中，有{days_with_data}天有健康数据记录',
        'value': round(completeness, 1),
        'status': 'excellent' if completeness >= 80 else 'good' if completeness >= 50 else 'poor'
    })
    
    # 2. 测量频率分析
    by_type = defaultdict(int)
    for m in metrics:
        by_type[m.metric_type] += 1
    
    avg_frequency = statistics.mean(by_type.values()) if by_type else 0
    
    insights.append({
        'type': 'measurement_frequency',
        'title': '测量频率',
        'description': f'平均每天每项指标测量{avg_frequency:.1f}次',
        'value': round(avg_frequency, 1),
        'status': 'excellent' if avg_frequency >= 2 else 'good' if avg_frequency >= 1 else 'needs_improvement'
    })
    
    # 3. 健康趋势洞察
    for metric_type, count in by_type.items():
        recent_metrics = [m for m in metrics if m.metric_type == metric_type and 
                         m.recorded_at >= datetime.utcnow() - timedelta(days=7)]
        older_metrics = [m for m in metrics if m.metric_type == metric_type and
                        m.recorded_at < datetime.utcnow() - timedelta(days=7)]
        
        if len(recent_metrics) >= 2 and len(older_metrics) >= 2:
            recent_avg = statistics.mean([float(m.metric_value) for m in recent_metrics])
            older_avg = statistics.mean([float(m.metric_value) for m in older_metrics])
            
            if recent_avg > older_avg * 1.1:
                temp_metric = HealthMetric(metric_type=metric_type, metric_value=0)
                insights.append({
                    'type': 'trend',
                    'title': f'{temp_metric.get_metric_type_display()}上升趋势',
                    'description': f'近期平均值较之前上升{((recent_avg-older_avg)/older_avg*100):.1f}%',
                    'status': 'warning'
                })
            elif recent_avg < older_avg * 0.9:
                temp_metric = HealthMetric(metric_type=metric_type, metric_value=0)
                insights.append({
                    'type': 'trend',
                    'title': f'{temp_metric.get_metric_type_display()}下降趋势',
                    'description': f'近期平均值较之前下降{((older_avg-recent_avg)/older_avg*100):.1f}%',
                    'status': 'warning'
                })
    
    # 4. 异常检测洞察
    anomalies = [m for m in metrics if is_abnormal(m.metric_type, float(m.metric_value))]
    anomaly_rate = len(anomalies) / len(metrics) * 100 if metrics else 0
    
    insights.append({
        'type': 'anomaly_detection',
        'title': '异常检测',
        'description': f'发现{len(anomalies)}条异常记录，占比{anomaly_rate:.1f}%',
        'value': len(anomalies),
        'status': 'excellent' if anomaly_rate < 10 else 'good' if anomaly_rate < 20 else 'warning'
    })
    
    return api_response(insights)
