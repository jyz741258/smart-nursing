from flask import request
from datetime import datetime, timedelta
from . import health_bp
from ..extensions import db
from ..models import HealthMetric
from ..utils.response import api_response, api_error, page_response
from ..utils import require_token


@health_bp.route('/metrics', methods=['POST'])
@require_token
def create_health_metric(current_user):
    """创建健康指标"""
    data = request.get_json()

    metric = HealthMetric(
        elder_id=data.get('elder_id'),
        metric_type=data.get('metric_type'),
        metric_value=float(data.get('metric_value')),
        unit=data.get('unit'),
        recorded_by=current_user.id,
        notes=data.get('notes')
    )

    if 'recorded_at' in data:
        metric.recorded_at = datetime.fromisoformat(data['recorded_at'])

    db.session.add(metric)
    db.session.commit()

    return api_response({'id': metric.id}, '健康指标记录成功')


@health_bp.route('/metrics', methods=['GET'])
@require_token
def get_health_metrics(current_user):
    """获取健康指标列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    elder_id = request.args.get('elder_id', type=int)
    metric_type = request.args.get('metric_type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = HealthMetric.query

    if elder_id:
        query = query.filter_by(elder_id=elder_id)
    if metric_type:
        query = query.filter_by(metric_type=metric_type)
    if start_date:
        query = query.filter(HealthMetric.recorded_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(HealthMetric.recorded_at <= datetime.fromisoformat(end_date))

    query = query.order_by(HealthMetric.recorded_at.desc())

    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    metrics = [{
        'id': m.id,
        'elder_id': m.elder_id,
        'elder_name': m.elder.name if m.elder else None,
        'metric_type': m.metric_type,
        'metric_type_name': m.get_metric_type_display(),
        'metric_value': m.metric_value,
        'unit': m.unit,
        'recorded_at': m.recorded_at.isoformat(),
        'notes': m.notes
    } for m in pagination.items]

    return page_response(metrics, pagination.total, page, page_size)


@health_bp.route('/metrics/<int:metric_id>', methods=['GET'])
@require_token
def get_health_metric_detail(current_user, metric_id):
    """获取健康指标详情"""
    metric = HealthMetric.query.get_or_404(metric_id)

    return api_response({
        'id': metric.id,
        'elder_id': metric.elder_id,
        'elder_name': metric.elder.name if metric.elder else None,
        'metric_type': metric.metric_type,
        'metric_type_name': metric.get_metric_type_display(),
        'metric_value': metric.metric_value,
        'unit': metric.unit,
        'recorded_at': metric.recorded_at.isoformat(),
        'recorded_by': metric.recorded_by,
        'recorded_by_name': metric.recorder.name if metric.recorder else None,
        'notes': metric.notes
    })


@health_bp.route('/metrics/latest/<int:elder_id>', methods=['GET'])
@require_token
def get_latest_metrics(current_user, elder_id):
    """获取老人最新健康指标"""
    metric_types = [1, 2, 3, 4, 5, 6]  # 各种指标类型
    latest_metrics = {}

    for metric_type in metric_types:
        metric = HealthMetric.query.filter_by(
            elder_id=elder_id,
            metric_type=metric_type
        ).order_by(HealthMetric.recorded_at.desc()).first()

        if metric:
            latest_metrics[metric.get_metric_type_display()] = {
                'value': metric.metric_value,
                'unit': metric.unit,
                'recorded_at': metric.recorded_at.isoformat()
            }

    return api_response(latest_metrics)


@health_bp.route('/metrics/history/<int:elder_id>/<int:metric_type>', methods=['GET'])
@require_token
def get_metric_history(current_user, elder_id, metric_type):
    """获取健康指标历史"""
    days = request.args.get('days', 7, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)

    metrics = HealthMetric.query.filter(
        HealthMetric.elder_id == elder_id,
        HealthMetric.metric_type == metric_type,
        HealthMetric.recorded_at >= start_date
    ).order_by(HealthMetric.recorded_at.asc()).all()

    return api_response([{
        'value': m.metric_value,
        'recorded_at': m.recorded_at.isoformat()
    } for m in metrics])


@health_bp.route('/metrics/types', methods=['GET'])
@require_token
def get_metric_types(current_user):
    """获取指标类型列表"""
    types = [
        {'value': 1, 'label': '体温', 'unit': '℃'},
        {'value': 2, 'label': '血压-收缩压', 'unit': 'mmHg'},
        {'value': 3, 'label': '血压-舒张压', 'unit': 'mmHg'},
        {'value': 4, 'label': '心率', 'unit': '次/分'},
        {'value': 5, 'label': '血氧', 'unit': '%'},
        {'value': 6, 'label': '血糖', 'unit': 'mmol/L'},
        {'value': 7, 'label': '体重', 'unit': 'kg'},
        {'value': 8, 'label': '身高', 'unit': 'cm'}
    ]
    return api_response(types)
