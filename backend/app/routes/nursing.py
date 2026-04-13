from flask import request
from datetime import datetime
from . import nursing_bp
from ..extensions import db
from ..models import NursingRecord
from ..utils.response import api_response, api_error, page_response
from ..utils import require_token


@nursing_bp.route('/records', methods=['POST'])
@require_token
def create_nursing_record(current_user):
    """创建护理记录"""
    # 只有护理人员(2)和管理员(3)可以创建护理记录
    if current_user.user_type not in [2, 3]:
        return api_error('无权限创建护理记录', 403)

    data = request.get_json()

    record = NursingRecord(
        elder_id=data.get('elder_id'),
        nursing_type=data.get('nursing_type'),
        description=data.get('description'),
        staff_id=current_user.id,
        status=1
    )

    if 'start_time' in data:
        record.start_time = datetime.fromisoformat(data['start_time'])
    if 'end_time' in data:
        record.end_time = datetime.fromisoformat(data['end_time'])

    db.session.add(record)
    db.session.commit()

    return api_response({'id': record.id}, '护理记录创建成功')


@nursing_bp.route('/records', methods=['GET'])
@require_token
def get_nursing_records(current_user):
    """获取护理记录列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    elder_id = request.args.get('elder_id', type=int)
    nursing_type = request.args.get('nursing_type')

    query = NursingRecord.query

    if elder_id:
        query = query.filter_by(elder_id=elder_id)
    if nursing_type:
        query = query.filter_by(nursing_type=nursing_type)

    query = query.order_by(NursingRecord.created_at.desc())

    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    records = [{
        'id': r.id,
        'elder_id': r.elder_id,
        'elder_name': r.elder.name if r.elder else None,
        'nursing_type': r.nursing_type,
        'nursing_type_name': r.get_nursing_type_display(),
        'description': r.description,
        'start_time': r.start_time.isoformat() if r.start_time else None,
        'end_time': r.end_time.isoformat() if r.end_time else None,
        'status': r.status,
        'status_name': r.get_status_display(),
        'created_at': r.created_at.isoformat()
    } for r in pagination.items]

    return page_response(records, pagination.total, page, page_size)


@nursing_bp.route('/records/<int:record_id>', methods=['GET'])
@require_token
def get_nursing_record_detail(current_user, record_id):
    """获取护理记录详情"""
    record = NursingRecord.query.get_or_404(record_id)

    return api_response({
        'id': record.id,
        'elder_id': record.elder_id,
        'elder_name': record.elder.name if record.elder else None,
        'nursing_type': record.nursing_type,
        'nursing_type_name': record.get_nursing_type_display(),
        'description': record.description,
        'start_time': record.start_time.isoformat() if record.start_time else None,
        'end_time': record.end_time.isoformat() if record.end_time else None,
        'status': record.status,
        'status_name': record.get_status_display(),
        'staff_id': record.staff_id,
        'staff_name': record.staff.name if record.staff else None,
        'notes': record.notes,
        'created_at': record.created_at.isoformat(),
        'updated_at': record.updated_at.isoformat() if record.updated_at else None
    })


@nursing_bp.route('/records/<int:record_id>', methods=['PUT'])
@require_token
def update_nursing_record(current_user, record_id):
    """更新护理记录"""
    record = NursingRecord.query.get_or_404(record_id)
    data = request.get_json()

    if 'nursing_type' in data:
        record.nursing_type = data['nursing_type']
    if 'description' in data:
        record.description = data['description']
    if 'start_time' in data:
        record.start_time = datetime.fromisoformat(data['start_time'])
    if 'end_time' in data:
        record.end_time = datetime.fromisoformat(data['end_time'])
    if 'status' in data:
        record.status = data['status']
    if 'notes' in data:
        record.notes = data['notes']

    db.session.commit()
    return api_response(message='护理记录更新成功')


@nursing_bp.route('/records/<int:record_id>/complete', methods=['POST'])
@require_token
def complete_nursing_record(current_user, record_id):
    """完成护理记录"""
    record = NursingRecord.query.get_or_404(record_id)
    data = request.get_json()

    record.status = 2  # 已完成
    record.end_time = datetime.utcnow()
    if 'notes' in data:
        record.notes = data['notes']

    db.session.commit()
    return api_response(message='护理记录已完成')


@nursing_bp.route('/types', methods=['GET'])
@require_token
def get_nursing_types(current_user):
    """获取护理类型列表"""
    types = [
        {'value': 1, 'label': '日常照护'},
        {'value': 2, 'label': '医疗护理'},
        {'value': 3, 'label': '康复训练'},
        {'value': 4, 'label': '心理疏导'},
        {'value': 5, 'label': '饮食护理'},
        {'value': 6, 'label': '清洁护理'},
        {'value': 7, 'label': '安全护理'}
    ]
    return api_response(types)
