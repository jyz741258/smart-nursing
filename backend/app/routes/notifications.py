from flask import request
from datetime import datetime
from . import notification_bp
from ..extensions import db
from ..models import Notification
from ..utils.response import api_response, api_error, page_response
from ..utils import require_token


@notification_bp.route('/', methods=['POST'])
@require_token
def create_notification(current_user):
    """创建通知"""
    data = request.get_json()

    notification = Notification(
        user_id=data.get('user_id'),
        title=data.get('title'),
        content=data.get('content'),
        notification_type=data.get('notification_type', 1),
        priority=data.get('priority', 0),
        created_by=current_user.id
    )

    db.session.add(notification)
    db.session.commit()

    return api_response({'id': notification.id}, '通知创建成功')


@notification_bp.route('/', methods=['GET'])
@require_token
def get_notifications(current_user):
    """获取通知列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    is_read = request.args.get('is_read')

    query = Notification.query.filter_by(user_id=current_user.id)

    if is_read is not None:
        query = query.filter_by(is_read=is_read.lower() == 'true')

    query = query.order_by(Notification.created_at.desc())

    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    notifications = [{
        'id': n.id,
        'title': n.title,
        'content': n.content,
        'notification_type': n.notification_type,
        'notification_type_name': n.get_notification_type_display(),
        'priority': n.priority,
        'priority_name': n.get_priority_display(),
        'is_read': n.is_read,
        'created_at': n.created_at.isoformat()
    } for n in pagination.items]

    return page_response(notifications, pagination.total, page, page_size)


@notification_bp.route('/<int:notification_id>/read', methods=['POST'])
@require_token
def mark_as_read(current_user, notification_id):
    """标记通知已读"""
    notification = Notification.query.get_or_404(notification_id)

    if notification.user_id != current_user.id:
        return api_error('无权限', 403)

    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.session.commit()

    return api_response(message='已标记为已读')


@notification_bp.route('/read-all', methods=['POST'])
@require_token
def mark_all_as_read(current_user):
    """标记所有通知已读"""
    Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).update({
        'is_read': True,
        'read_at': datetime.utcnow()
    })
    db.session.commit()

    return api_response(message='所有通知已标记为已读')


@notification_bp.route('/unread-count', methods=['GET'])
@require_token
def get_unread_count(current_user):
    """获取未读通知数量"""
    count = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).count()

    return api_response({'count': count})


@notification_bp.route('/broadcast', methods=['POST'])
@require_token
def broadcast_notification(current_user):
    """广播通知给所有用户"""
    data = request.get_json()
    user_ids = data.get('user_ids', [])

    for user_id in user_ids:
        notification = Notification(
            user_id=user_id,
            title=data.get('title'),
            content=data.get('content'),
            notification_type=data.get('notification_type', 1),
            priority=data.get('priority', 1),
            created_by=current_user.id
        )
        db.session.add(notification)

    db.session.commit()
    return api_response(message=f'通知已发送给 {len(user_ids)} 个用户')


@notification_bp.route('/types', methods=['GET'])
@require_token
def get_notification_types(current_user):
    """获取通知类型列表"""
    types = [
        {'value': 1, 'label': '系统通知'},
        {'value': 2, 'label': '护理提醒'},
        {'value': 3, 'label': '健康预警'},
        {'value': 4, 'label': '任务通知'},
        {'value': 5, 'label': '紧急通知'}
    ]
    return api_response(types)
