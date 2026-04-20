from flask import request
from datetime import datetime
from . import notification_bp
from ..extensions import db
from ..models import Notification, User
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

    # 管理员可以看到所有通知，普通用户只能看到自己的通知
    if current_user.user_type == 3:  # 管理员
        query = Notification.query
    else:
        query = Notification.query.filter_by(user_id=current_user.id)

    if is_read is not None:
        query = query.filter_by(is_read=is_read.lower() == 'true')

    query = query.order_by(Notification.created_at.desc())

    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    notifications = []
    for n in pagination.items:
        # 获取发送者信息
        creator = User.query.get(n.created_by)
        creator_name = creator.name if creator else '系统'

        # 获取接收者信息
        recipient = User.query.get(n.user_id)
        recipient_name = recipient.name if recipient else '未知'

        notifications.append({
            'id': n.id,
            'title': n.title,
            'content': n.content,
            'notification_type': n.notification_type,
            'notification_type_name': n.get_notification_type_display(),
            'priority': n.priority,
            'priority_name': n.get_priority_display(),
            'is_read': n.is_read,
            'created_at': n.created_at.isoformat(),
            'created_by_name': creator_name,
            'recipient_name': recipient_name,
            'user_name': recipient_name  # 兼容前端字段
        })

    return page_response(notifications, pagination.total, page, page_size)


@notification_bp.route('/<int:notification_id>/read', methods=['POST'])
@require_token
def mark_as_read(current_user, notification_id):
    """标记通知已读"""
    notification = Notification.query.get_or_404(notification_id)

    # 管理员可以标记任何通知为已读，普通用户只能标记自己的通知为已读
    if current_user.user_type != 3 and notification.user_id != current_user.id:
        return api_error('无权限', 403)

    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.session.commit()

    return api_response(message='已标记为已读')


@notification_bp.route('/read-all', methods=['POST'])
@require_token
def mark_all_as_read(current_user):
    """标记所有通知已读"""
    # 管理员可以标记所有通知为已读，普通用户只能标记自己的通知为已读
    if current_user.user_type == 3:  # 管理员
        query = Notification.query.filter_by(is_read=False)
    else:
        query = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        )
    
    query.update({
        'is_read': True,
        'read_at': datetime.utcnow()
    })
    db.session.commit()

    return api_response(message='所有通知已标记为已读')


@notification_bp.route('/unread-count', methods=['GET'])
@require_token
def get_unread_count(current_user):
    """获取未读通知数量"""
    # 管理员可以看到所有未读通知的数量，普通用户只能看到自己的未读通知数量
    if current_user.user_type == 3:  # 管理员
        count = Notification.query.filter_by(is_read=False).count()
    else:
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


@notification_bp.route('/users', methods=['GET'])
@require_token
def get_notification_users(current_user):
    """获取可发送通知的用户列表（供管理员选择）"""
    user_type = request.args.get('user_type', type=int)

    query = User.query.filter(User.user_type.in_([1, 2, 4]))  # 老人、护理人员、家属

    if user_type:
        query = query.filter_by(user_type=user_type)

    users = query.order_by(User.user_type.asc(), User.id.asc()).all()

    user_type_names = {1: '老人', 2: '护理人员', 4: '家属', 3: '管理员'}

    return api_response([{
        'id': u.id,
        'name': u.name,
        'phone': u.phone,
        'user_type': u.user_type,
        'user_type_name': user_type_names.get(u.user_type, '未知')
    } for u in users])


@notification_bp.route('/create', methods=['POST'])
@require_token
def create_notification_v2(current_user):
    """创建通知（支持发送给多人）"""
    data = request.get_json()

    user_ids = data.get('user_ids', [])  # 支持发送给多个用户
    title = data.get('title', '')
    content = data.get('content', '')
    notification_type = data.get('notification_type', 1)
    priority = data.get('priority', 0)

    if not title:
        return api_error('通知标题不能为空')
    if not user_ids:
        return api_error('请选择至少一个接收人')

    created_count = 0
    for user_id in user_ids:
        notification = Notification(
            user_id=user_id,
            title=title,
            content=content,
            notification_type=notification_type,
            priority=priority,
            created_by=current_user.id
        )
        db.session.add(notification)
        created_count += 1

    db.session.commit()
    return api_response({'count': created_count}, f'通知已发送给 {created_count} 个用户')
