from flask import request
from datetime import datetime
from . import care_bp
from ..extensions import db
from ..models import CarePlan, CareTask
from ..utils.response import api_response, api_error, page_response
from ..utils import require_token


@care_bp.route('/plans', methods=['POST'])
@require_token
def create_care_plan(current_user):
    """创建护理计划"""
    data = request.get_json()

    plan = CarePlan(
        elder_id=data.get('elder_id'),
        title=data.get('title'),
        description=data.get('description'),
        start_date=datetime.fromisoformat(data['start_date']) if data.get('start_date') else None,
        end_date=datetime.fromisoformat(data['end_date']) if data.get('end_date') else None,
        status=1,
        created_by=current_user.id
    )

    db.session.add(plan)
    db.session.commit()

    return api_response({'id': plan.id}, '护理计划创建成功')


@care_bp.route('/plans', methods=['GET'])
@require_token
def get_care_plans(current_user):
    """获取护理计划列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    elder_id = request.args.get('elder_id', type=int)
    status = request.args.get('status', type=int)

    query = CarePlan.query

    if elder_id:
        query = query.filter_by(elder_id=elder_id)
    if status:
        query = query.filter_by(status=status)

    query = query.order_by(CarePlan.created_at.desc())

    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    plans = [{
        'id': p.id,
        'elder_id': p.elder_id,
        'elder_name': p.elder.name if p.elder else None,
        'title': p.title,
        'description': p.description,
        'start_date': p.start_date.isoformat() if p.start_date else None,
        'end_date': p.end_date.isoformat() if p.end_date else None,
        'status': p.status,
        'status_name': p.get_status_display(),
        'created_at': p.created_at.isoformat()
    } for p in pagination.items]

    return page_response(plans, pagination.total, page, page_size)


@care_bp.route('/plans/<int:plan_id>', methods=['GET'])
@require_token
def get_care_plan_detail(current_user, plan_id):
    """获取护理计划详情"""
    plan = CarePlan.query.get_or_404(plan_id)
    tasks = CareTask.query.filter_by(care_plan_id=plan_id).all()

    return api_response({
        'id': plan.id,
        'elder_id': plan.elder_id,
        'elder_name': plan.elder.name if plan.elder else None,
        'title': plan.title,
        'description': plan.description,
        'start_date': plan.start_date.isoformat() if plan.start_date else None,
        'end_date': plan.end_date.isoformat() if plan.end_date else None,
        'status': plan.status,
        'status_name': plan.get_status_display(),
        'tasks': [{
            'id': t.id,
            'task_name': t.task_name,
            'task_type': t.task_type,
            'frequency': t.frequency,
            'status': t.status,
            'status_name': t.get_status_display()
        } for t in tasks]
    })


@care_bp.route('/plans/<int:plan_id>', methods=['PUT'])
@require_token
def update_care_plan(current_user, plan_id):
    """更新护理计划"""
    plan = CarePlan.query.get_or_404(plan_id)
    data = request.get_json()

    if 'title' in data:
        plan.title = data['title']
    if 'description' in data:
        plan.description = data['description']
    if 'start_date' in data:
        plan.start_date = datetime.fromisoformat(data['start_date'])
    if 'end_date' in data:
        plan.end_date = datetime.fromisoformat(data['end_date'])
    if 'status' in data:
        plan.status = data['status']

    db.session.commit()
    return api_response(message='护理计划更新成功')


@care_bp.route('/tasks', methods=['POST'])
@require_token
def create_care_task(current_user):
    """创建护理任务"""
    data = request.get_json()

    task = CareTask(
        care_plan_id=data.get('care_plan_id'),
        task_name=data.get('task_name'),
        task_type=data.get('task_type'),
        description=data.get('description'),
        frequency=data.get('frequency'),
        status=1
    )

    if 'scheduled_time' in data:
        task.scheduled_time = datetime.fromisoformat(data['scheduled_time'])

    db.session.add(task)
    db.session.commit()

    return api_response({'id': task.id}, '护理任务创建成功')


@care_bp.route('/tasks/<int:task_id>/complete', methods=['POST'])
@require_token
def complete_care_task(current_user, task_id):
    """完成任务"""
    task = CareTask.query.get_or_404(task_id)
    data = request.get_json()

    task.status = 2
    task.completed_at = datetime.utcnow()
    task.completed_by = current_user.id
    if 'notes' in data:
        task.notes = data['notes']

    db.session.commit()
    return api_response(message='任务已完成')


@care_bp.route('/tasks/today', methods=['GET'])
@require_token
def get_today_tasks(current_user):
    """获取今日任务"""
    today = datetime.utcnow().date()
    tasks = CareTask.query.join(CarePlan).filter(
        CarePlan.status == 1,
        CareTask.status.in_([1, 2])
    ).order_by(CareTask.scheduled_time.asc()).all()

    return api_response([{
        'id': t.id,
        'task_name': t.task_name,
        'task_type': t.task_type,
        'elder_id': t.care_plan.elder_id,
        'elder_name': t.care_plan.elder.name if t.care_plan.elder else None,
        'scheduled_time': t.scheduled_time.isoformat() if t.scheduled_time else None,
        'status': t.status,
        'status_name': t.get_status_display()
    } for t in tasks])


@care_bp.route('/plans/<int:plan_id>/tasks', methods=['POST'])
@require_token
def create_care_task_for_plan(current_user, plan_id):
    """为护理计划添加任务"""
    # 验证护理计划是否存在
    plan = CarePlan.query.get_or_404(plan_id)
    
    data = request.get_json()

    task = CareTask(
        care_plan_id=plan_id,
        task_name=data.get('task_name'),
        task_type=data.get('task_type'),
        description=data.get('description'),
        frequency=data.get('frequency'),
        scheduled_time=datetime.fromisoformat(data['scheduled_time']) if data.get('scheduled_time') else None,
        status=1,
        notes=data.get('notes')
    )

    db.session.add(task)
    db.session.commit()

    return api_response({'id': task.id}, '护理任务添加成功')
