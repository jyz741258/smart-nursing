from flask import request
from datetime import datetime
import uuid
from . import order_bp
from ..extensions import db
from ..models import Order, Service, User, Notification
from ..utils.response import api_response, api_error, page_response
from ..utils import require_token


@order_bp.route('/summary', methods=['GET'])
@require_token
def get_orders_summary(current_user):
    """获取订单汇总统计"""
    from datetime import datetime

    # 获取日期范围参数
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    status = request.args.get('status', type=int)
    elder_id = request.args.get('elder_id', type=int)
    service_id = request.args.get('service_id', type=int)

    # 构建基础查询
    query = Order.query

    # 应用权限过滤（与 get_orders 保持一致）
    if current_user.user_type != 3:
        if current_user.user_type == 1:
            # 老人只能看到自己的订单
            query = query.filter_by(elder_id=current_user.id)
        elif current_user.user_type == 2:
            # 护理人员只能看到自己的订单
            query = query.filter_by(nurse_id=current_user.id)
        elif current_user.user_type == 4:
            # 家属只能看到自己绑定的老人的订单
            if current_user.binding_elder_id:
                query = query.filter_by(elder_id=current_user.binding_elder_id)
            else:
                # 家属未绑定老人，返回空结果
                query = query.filter_by(id=0)

    # 应用筛选条件（与 get_orders 完全一致）
    if status is not None:
        query = query.filter_by(status=status)
    if elder_id:
        query = query.filter_by(elder_id=elder_id)
    if service_id:
        query = query.filter_by(service_id=service_id)
    if start_date:
        query = query.filter(Order.created_at >= start_date)
    if end_date:
        query = query.filter(Order.created_at <= end_date)

    # 调试日志 - 查看筛选后的订单
    all_orders = query.all()
    print(f"[Order Summary Debug] 筛选后订单数量: {len(all_orders)}")
    for o in all_orders[:5]:
        print(f"  Order ID={o.id}, status={o.status}, actual_amount={o.actual_amount}, total_amount={o.total_amount}")

    # 获取总订单数
    total_orders = len(all_orders)

    # 获取总销售额（已完成/待支付的订单）
    sales_query = query.filter(Order.status.in_([2, 4])).all()
    total_sales = sum(o.actual_amount for o in sales_query if o.actual_amount) if sales_query else 0
    print(f"[Order Summary Debug] 销售额计算: 订单数={len(sales_query)}, total_sales={total_sales}")

    # 获取已完成订单数（状态为4）
    completed_orders = query.filter_by(status=4).count()

    # 获取待处理订单数（状态为1）
    pending_orders = query.filter_by(status=1).count()

    # 调试日志
    print(f"[Order Summary] user_type={current_user.user_type}, filters: status={status}")
    print(f"[Order Summary] total_orders={total_orders}, total_sales={total_sales}, completed={completed_orders}, pending={pending_orders}")

    return api_response({
        'total_orders': total_orders,
        'total_sales': float(total_sales),
        'completed_orders': completed_orders,
        'pending_orders': pending_orders
    })


@order_bp.route('/', methods=['GET'])
@require_token
def get_orders(current_user):
    """获取订单列表"""
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        status = request.args.get('status', type=int)
        elder_id = request.args.get('elder_id', type=int)
        service_id = request.args.get('service_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = Order.query

        # 管理员可以看到所有订单
        if current_user.user_type != 3:
            if current_user.user_type == 1:
                # 老人只能看到自己的订单
                query = query.filter_by(elder_id=current_user.id)
            elif current_user.user_type == 2:
                # 护理人员只能看到自己的订单
                query = query.filter_by(nurse_id=current_user.id)
            elif current_user.user_type == 4:
                # 家属只能看到自己绑定的老人的订单
                # 通过 current_user.binding_elder_id 过滤
                if current_user.binding_elder_id:
                    query = query.filter_by(elder_id=current_user.binding_elder_id)
                else:
                    # 家属未绑定老人，返回空结果
                    query = query.filter_by(id=0)  # 永远不匹配的条件

        if status is not None:
            query = query.filter_by(status=status)
        if elder_id:
            query = query.filter_by(elder_id=elder_id)
        if service_id:
            query = query.filter_by(service_id=service_id)
        if start_date:
            query = query.filter(Order.created_at >= start_date)
        if end_date:
            query = query.filter(Order.created_at <= end_date)

        # 调试日志
        total_before_paginate = query.count()
        print(f"[Get Orders] user_type={current_user.user_type}, filters: status={status}, total_before_paginate={total_before_paginate}")

        query = query.order_by(Order.created_at.desc())

        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        orders = []
        for order in pagination.items:
            order_dict = order.to_dict()
            # 添加上下文信息
            service = Service.query.get(order.service_id)
            if service:
                order_dict['service_name'] = service.name
                order_dict['price'] = service.price
            elder = User.query.get(order.elder_id)
            if elder:
                order_dict['elder_name'] = elder.name
            nurse = User.query.get(order.nurse_id)
            if nurse:
                order_dict['nurse_name'] = nurse.name
            # 添加状态名称
            status_names = {0: '已取消', 1: '待支付', 2: '待服务', 3: '服务中', 4: '已完成', 5: '已退款'}
            order_dict['status_name'] = status_names.get(order.status, '未知')
            orders.append(order_dict)

        print(f"[Get Orders] returned {len(orders)} items, pagination.total={pagination.total}")

        return page_response(orders, pagination.total, page, page_size)
    except Exception as e:
        print(f"[Get Orders ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return api_error(f'获取订单列表失败: {str(e)}', 500)


@order_bp.route('/<int:order_id>', methods=['GET'])
@require_token
def get_order_detail(current_user, order_id):
    """获取订单详情"""
    order = Order.query.get_or_404(order_id)
    # 检查权限
    if current_user.user_type != 3:
        if current_user.user_type == 1 and order.elder_id != current_user.id:
            return api_error('无权限', 403)
        elif current_user.user_type == 2 and order.nurse_id != current_user.id:
            return api_error('无权限', 403)
        elif current_user.user_type == 4:
            elder = User.query.get(order.elder_id)
            if elder and elder.family_id != current_user.id:
                return api_error('无权限', 403)
    order_dict = order.to_dict()
    # 添加上下文信息
    service = Service.query.get(order.service_id)
    if service:
        order_dict['service_name'] = service.name
        order_dict['price'] = service.price
    elder = User.query.get(order.elder_id)
    if elder:
        order_dict['elder_name'] = elder.name
    nurse = User.query.get(order.nurse_id)
    if nurse:
        order_dict['nurse_name'] = nurse.name
    # 添加状态名称
    status_names = {0: '已取消', 1: '待支付', 2: '待服务', 3: '服务中', 4: '已完成', 5: '已退款'}
    order_dict['status_name'] = status_names.get(order.status, '未知')
    return api_response(order_dict)


@order_bp.route('/', methods=['POST'])
@require_token
def create_order(current_user):
    """创建订单"""
    from datetime import datetime
    import uuid
    import traceback

    try:
        data = request.get_json()
        service_id = data.get('service_id')
        elder_id = data.get('elder_id')
        service_time = data.get('service_time')
        notes = data.get('notes')
        appointment_date = data.get('appointment_date')
        appointment_time = data.get('appointment_time')

        # 验证参数
        if not service_id:
            return api_error('缺少必要参数：service_id', 400)

        # 验证服务是否存在
        service = Service.query.get(service_id)
        if not service:
            return api_error('服务不存在', 404)

        # 确定老人ID
        if not elder_id:
            if current_user.user_type == 1:
                # 老人自己下单
                elder_id = current_user.id
            elif current_user.user_type == 4:
                # 家属为老人下单，从userInfo中自动获取绑定的老人ID
                family_user = User.query.get(current_user.id)
                if family_user and family_user.binding_elder_id:
                    elder_id = family_user.binding_elder_id
                else:
                    return api_error('请先绑定老人', 400)
            else:
                elder_id = None

        # 验证老人是否存在（如果指定了老人ID）
        elder = None
        if elder_id:
            elder = User.query.get(elder_id)
            if not elder or elder.user_type != 1:
                return api_error('老人不存在', 404)

        # 生成订单号
        order_no = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"

        # 创建订单
        order = Order(
            order_no=order_no,
            user_id=current_user.id,
            service_id=service_id,
            elder_id=elder_id,
            order_time=datetime.now(),
            remark=notes,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            total_amount=service.price,
            actual_amount=service.price,
            service_name=service.name,
            service_price=service.price,
            status=1,  # 待支付
            created_by=current_user.id
        )

        db.session.add(order)
        db.session.commit()

        # 订单创建成功后，发送通知给管理员和护理人员
        try:
            # 获取管理员（user_type=3）
            admins = User.query.filter_by(user_type=3, status=1).all()
            # 获取负责该老人的护理人员（通过nurse_id，如果有的话）
            # 这里先发送给管理员，管理员再分配给护理人员
            # 或者根据服务类型查找对应区域的护理人员

            # 构建通知内容
            notification_title = "新订单预约"
            notification_content = f"用户 {current_user.real_name or current_user.username} 预约了服务「{service.name}」，服务时间：{appointment_date or '待定'} {appointment_time or ''}，服务对象：{elder.real_name if elder else '未知'}"

            # 发送给所有在线管理员
            for admin in admins:
                notification = Notification(
                    user_id=admin.id,
                    title=notification_title,
                    content=notification_content,
                    notification_type=4,  # 任务通知
                    priority=1,  # 重要
                    created_by=current_user.id
                )
                db.session.add(notification)

            # 如果有指定的护理人员（nurse_id字段），也发送通知
            # 但当前订单刚创建，nurse_id为空，需要管理员分配
            # 所以暂时只通知管理员

            db.session.commit()
        except Exception as e:
            # 通知发送失败不影响订单创建
            print(f"发送订单通知失败: {e}")

        return api_response(order.to_dict(), '订单创建成功')
    except Exception as e:
        db.session.rollback()
        error_trace = traceback.format_exc()
        print(f"创建订单失败: {e}")
        print(error_trace)
        return api_error(f'创建订单失败: {str(e)}', 500)


@order_bp.route('/<int:order_id>', methods=['PUT'])
@require_token
def update_order(current_user, order_id):
    """更新订单"""
    order = Order.query.get_or_404(order_id)
    # 检查权限
    if current_user.user_type != 3:
        if current_user.user_type == 1 and order.elder_id != current_user.id:
            return api_error('无权限', 403)
        elif current_user.user_type == 2 and order.nurse_id != current_user.id:
            return api_error('无权限', 403)
        elif current_user.user_type == 4:
            elder = User.query.get(order.elder_id)
            if elder and elder.family_id != current_user.id:
                return api_error('无权限', 403)
    data = request.get_json()

    # 记录变更用于通知
    changes = []
    
    if 'status' in data:
        old_status = order.status
        order.status = data['status']
        if old_status != data['status']:
            status_map = {0: '已取消', 1: '待支付', 2: '待服务', 3: '服务中', 4: '已完成', 5: '已退款'}
            changes.append(f"订单状态变更为：{status_map.get(data['status'], '未知')}")
    
    if 'nurse_id' in data:
        old_nurse = order.nurse_id
        new_nurse = data['nurse_id']
        order.nurse_id = new_nurse
        if old_nurse != new_nurse:
            nurse = User.query.get(new_nurse)
            nurse_name = nurse.name if nurse else "未知"
            changes.append(f"护理人员已分配：{nurse_name}")
    
    if 'notes' in data:
        order.notes = data['notes']
    if 'appointment_date' in data:
        order.appointment_date = data['appointment_date']
    if 'appointment_time' in data:
        order.appointment_time = data['appointment_time']
    if 'remark' in data:
        order.remark = data['remark']

    db.session.commit()

    # 发送通知（如果发生了重要变更）
    try:
        if changes:
            # 通知护理人员（如果已分配）
            if order.nurse_id:
                nurse = User.query.get(order.nurse_id)
                if nurse:
                    notification = Notification(
                        user_id=nurse.id,
                        title="订单更新通知",
                        content=f"订单「{order.service_name}」已更新：{'; '.join(changes)}",
                        notification_type=4,  # 任务通知
                        priority=1 if 'nurse_id' in data else 0,
                        created_by=current_user.id
                    )
                    db.session.add(notification)
            
            # 通知老人（状态变更）
            if 'status' in data and order.elder_id:
                elder = User.query.get(order.elder_id)
                if elder:
                    notification = Notification(
                        user_id=elder.id,
                        title="订单状态更新",
                        content=f"您的订单「{order.service_name}」状态已更新为：{status_map.get(data['status'], '未知')}",
                        notification_type=2,  # 护理提醒
                        priority=1,
                        created_by=current_user.id
                    )
                    db.session.add(notification)
            
            db.session.commit()
    except Exception as e:
        print(f"发送订单更新通知失败: {e}")

    return api_response(order.to_dict(), '订单更新成功')


@order_bp.route('/<int:order_id>', methods=['DELETE'])
@require_token
def delete_order(current_user, order_id):
    """删除订单"""
    # 只有管理员可以删除订单
    if current_user.user_type != 3:
        return api_error('无权限', 403)

    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()

    return api_response(message='订单删除成功')
