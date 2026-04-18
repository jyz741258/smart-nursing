"""
支付相关路由
支持支付宝和微信支付
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from ..extensions import db
from ..models import Order, User, Notification
from ..utils.response import api_response, api_error
from ..utils import require_token
from ..utils.payment import payment_service
import logging

logger = logging.getLogger(__name__)

payment_bp = Blueprint('payment', __name__, url_prefix='/api/payment')


@payment_bp.route('/create', methods=['POST'])
@require_token
def create_payment(current_user):
    """
    创建支付订单
    
    请求参数:
        order_id: 订单ID
        platform: 支付平台 ('alipay' 或 'wechat')
        openid: 微信支付用户openid (可选，用于JSAPI支付)
    """
    data = request.get_json()
    order_id = data.get('order_id')
    platform = data.get('platform', 'alipay')  # 默认支付宝
    openid = data.get('openid')  # 微信JSAPI支付需要
    
    if not order_id:
        return api_error('缺少订单ID', 400)
    
    # 获取订单
    order = Order.query.get(order_id)
    if not order:
        return api_error('订单不存在', 404)
    
    # 检查订单状态
    if order.status != 1:  # 非待支付状态
        return api_error(f'订单状态不正确，当前状态: {order.get_status_text()}', 400)
    
    # 验证金额
    if order.actual_amount <= 0:
        return api_error('订单金额不正确', 400)
    
    try:
        # 调用支付服务创建支付
        result = payment_service.create_payment(
            order_no=order.order_no,
            amount=float(order.actual_amount),
            subject=order.service_name or '护理服务',
            platform=platform
        )
        
        if result.get('success'):
            return api_response({
                'order_id': order.id,
                'order_no': order.order_no,
                'platform': platform,
                'payment_data': result,  # 包含支付参数
                'amount': float(order.actual_amount)
            }, '支付订单创建成功')
        else:
            return api_error(result.get('error', '支付创建失败'), 500)
            
    except Exception as e:
        logger.error(f"创建支付失败: {e}")
        return api_error(f'支付创建失败: {str(e)}', 500)


@payment_bp.route('/query/<order_no>', methods=['GET'])
@require_token
def query_payment(current_user, order_no):
    """
    查询支付状态
    
    参数:
        order_no: 订单编号
    """
    # 获取订单
    order = Order.query.filter_by(order_no=order_no).first()
    if not order:
        return api_error('订单不存在', 404)
    
    platform = request.args.get('platform', 'alipay')
    
    try:
        result = payment_service.query_payment(order_no, platform)
        
        # 更新本地订单状态（如果支付成功）
        if result.get('success') and result.get('trade_status') == 'TRADE_SUCCESS':
            if order.status == 1:  # 待支付 -> 已支付
                order.status = 2  # 待服务
                order.payment_method = platform
                order.payment_time = datetime.now()
                db.session.commit()
                
                # 支付成功，发送通知
                try:
                    _send_payment_success_notifications(order)
                except Exception as e:
                    logger.error(f"发送支付成功通知失败: {e}")
        
        return api_response({
            'order_no': order_no,
            'order_status': order.status,
            'status_text': order.get_status_text(),
            'payment_status': result
        })
        
    except Exception as e:
        logger.error(f"查询支付失败: {e}")
        return api_error(f'查询失败: {str(e)}', 500)


@payment_bp.route('/notify', methods=['POST', 'GET'])
def payment_notify():
    """
    支付回调通知处理
    
    支付宝和微信支付完成后会回调此接口
    """
    if request.method == 'GET':
        # 支付宝同步回调（用户在支付宝客户端点击"完成"后跳转回来）
        return jsonify({
            'success': True,
            'message': '支付成功，请等待系统处理'
        })
    
    try:
        data = request.get_json() or {}
        
        # 区分支付平台
        platform = data.get('platform', 'alipay')
        
        if platform == 'wechat':
            # 微信支付回调
            return _handle_wechat_notify(data)
        else:
            # 支付宝回调
            return _handle_alipay_notify(data)
            
    except Exception as e:
        logger.error(f"支付回调处理失败: {e}")
        return jsonify({'code': 'FAIL', 'message': str(e)})


def _handle_alipay_notify(data: dict):
    """处理支付宝回调"""
    try:
        # 获取回调数据
        out_trade_no = data.get('out_trade_no')
        trade_status = data.get('trade_status')
        trade_no = data.get('trade_no')
        total_amount = data.get('total_amount')
        
        if not out_trade_no:
            return jsonify({'success': False, 'message': '缺少订单号'})
        
        # 查询订单
        order = Order.query.filter_by(order_no=out_trade_no).first()
        if not order:
            return jsonify({'success': False, 'message': '订单不存在'})
        
        logger.info(f"支付宝回调: order_no={out_trade_no}, status={trade_status}")
        
        # 处理支付成功
        if trade_status in ['TRADE_SUCCESS', 'TRADE_FINISHED']:
            if order.status == 1:  # 仅处理待支付订单
                order.status = 2  # 待服务
                order.payment_method = 'alipay'
                order.payment_time = datetime.now()
                order.pay_transaction_id = trade_no
                db.session.commit()
                
                logger.info(f"订单支付成功: {out_trade_no}")
                
                # 发送支付成功通知
                try:
                    _send_payment_success_notifications(order)
                except Exception as e:
                    logger.error(f"发送支付成功通知失败: {e}")
        
        return jsonify({'success': True, 'message': 'success'})
        
    except Exception as e:
        logger.error(f"支付宝回调处理失败: {e}")
        return jsonify({'success': False, 'message': str(e)})


def _handle_wechat_notify(data: dict):
    """处理微信支付回调"""
    try:
        out_trade_no = data.get('out_trade_no')
        trade_state = data.get('trade_state')
        transaction_id = data.get('transaction_id')
        
        if not out_trade_no:
            return jsonify({'code': 'FAIL', 'message': '缺少订单号'})
        
        order = Order.query.filter_by(order_no=out_trade_no).first()
        if not order:
            return jsonify({'code': 'FAIL', 'message': '订单不存在'})
        
        logger.info(f"微信支付回调: order_no={out_trade_no}, state={trade_state}")
        
        # 处理支付成功
        if trade_state == 'SUCCESS':
            if order.status == 1:
                order.status = 2
                order.payment_method = 'wechat'
                order.payment_time = datetime.now()
                order.pay_transaction_id = transaction_id
                db.session.commit()
                
                logger.info(f"订单支付成功: {out_trade_no}")
                
                # 发送支付成功通知
                try:
                    _send_payment_success_notifications(order)
                except Exception as e:
                    logger.error(f"发送支付成功通知失败: {e}")
        
        return jsonify({'code': 'SUCCESS', 'message': '成功'})
        
    except Exception as e:
        logger.error(f"微信回调处理失败: {e}")
        return jsonify({'code': 'FAIL', 'message': str(e)})


@payment_bp.route('/refund', methods=['POST'])
@require_token
def apply_refund(current_user):
    """
    申请退款
    
    请求参数:
        order_id: 订单ID
        reason: 退款原因
    """
    # 仅管理员和家属可以申请退款
    if current_user.user_type not in [3, 4]:
        return api_error('无权限申请退款', 403)
    
    data = request.get_json()
    order_id = data.get('order_id')
    reason = data.get('reason', '')
    
    if not order_id:
        return api_error('缺少订单ID', 400)
    
    order = Order.query.get(order_id)
    if not order:
        return api_error('订单不存在', 404)
    
    # 检查订单状态（已支付且未完成的订单可以退款）
    if order.status not in [2, 3]:
        return api_error(f'当前状态无法退款: {order.get_status_text()}', 400)
    
    platform = order.payment_method or 'alipay'
    
    try:
        result = payment_service.refund(
            order_no=order.order_no,
            amount=float(order.actual_amount),
            platform=platform,
            reason=reason
        )
        
        if result.get('success'):
            # 更新订单状态为已退款
            order.status = 5  # 已退款
            order.cancel_reason = reason
            order.cancel_time = datetime.now()
            db.session.commit()
            
            return api_response({
                'refund_id': result.get('refund_id'),
                'amount': float(order.actual_amount)
            }, '退款申请成功')
        else:
            return api_error(result.get('error', '退款申请失败'), 500)
            
    except Exception as e:
        logger.error(f"退款申请失败: {e}")
        return api_error(f'退款失败: {str(e)}', 500)


@payment_bp.route('/cancel/<int:order_id>', methods=['POST'])
@require_token
def cancel_payment(current_user, order_id):
    """
    取消订单（仅未支付的订单）
    
    参数:
        order_id: 订单ID
    """
    order = Order.query.get(order_id)
    if not order:
        return api_error('订单不存在', 404)
    
    # 检查权限
    if current_user.user_type != 3 and order.user_id != current_user.id:
        return api_error('无权限', 403)
    
    # 仅待支付订单可以取消
    if order.status != 1:
        return api_error(f'当前状态无法取消: {order.get_status_text()}', 400)
    
    order.status = 0  # 已取消
    order.cancel_time = datetime.now()
    db.session.commit()
    
    return api_response(message='订单已取消')


@payment_bp.route('/wechat/auth', methods=['GET'])
def wechat_auth():
    """
    微信支付授权（获取openid的前置接口）
    
    参数:
        code: 微信授权code
    """
    code = request.args.get('code')
    
    if not code:
        return api_error('缺少授权code', 400)
    
    try:
        # 调用微信接口获取openid
        config = payment_service.config
        
        # 请求微信获取openid
        url = 'https://api.weixin.qq.com/sns/oauth2/access_token'
        params = {
            'appid': config.WECHAT_APP_ID,
            'secret': config.WECHAT_APP_SECRET if hasattr(config, 'WECHAT_APP_SECRET') else '',
            'code': code,
            'grant_type': 'authorization_code'
        }
        
        import requests
        response = requests.get(url, params=params, timeout=10)
        result = response.json()
        
        if 'openid' in result:
            return api_response({
                'openid': result['openid'],
                'access_token': result.get('access_token')
            })
        else:
            return api_error(result.get('errmsg', '获取openid失败'), 500)
            
    except Exception as e:
        logger.error(f"微信授权失败: {e}")
        return api_error(f'授权失败: {str(e)}', 500)


@payment_bp.route('/config', methods=['GET'])
@require_token
def get_payment_config(current_user):
    """
    获取支付配置（用于前端初始化）
    
    返回:
        enabled_payments: 启用的支付���式
        alipay_enabled: 支付宝是否可用
        wechat_enabled: 微信支付是否可用
    """
    config = payment_service.config
    
    alipay_enabled = bool(config.ALIPAY_APP_ID and config.ALIPAY_PRIVATE_KEY)
    wechat_enabled = bool(config.WECHAT_APP_ID and config.WECHAT_MCH_ID)
    
    return api_response({
        'alipay_enabled': alipay_enabled,
        'wechat_enabled': wechat_enabled,
        'enabled_payments': [
            'alipay' if alipay_enabled else None,
            'wechat' if wechat_enabled else None
        ],
        'mock_mode': not alipay_enabled and not wechat_enabled
    })


@payment_bp.route('/mock', methods=['GET', 'POST'])
def mock_payment():
    """
    模拟支付回调（用于测试）

    参数:
        order_no: 订单编号
    """
    order_no = request.args.get('order_no')

    if not order_no:
        return jsonify({'success': False, 'message': '缺少订单号'})

    # 模拟支付成功，更新订单状态
    order = Order.query.filter_by(order_no=order_no).first()
    if order and order.status == 1:
        order.status = 2  # 待服务
        order.payment_method = 'mock'
        order.payment_time = datetime.now()
        order.pay_transaction_id = f'MOCK{datetime.now().strftime("%Y%m%d%H%M%S")}'
        db.session.commit()
        logger.info(f"模拟支付成功: {order_no}")
        
        # 发送支付成功通知
        try:
            _send_payment_success_notifications(order)
        except Exception as e:
            logger.error(f"发送支付成功通知失败: {e}")

    return jsonify({
        'success': True,
        'message': '模拟支付成功',
        'order_no': order_no
    })


def _send_payment_success_notifications(order):
    """
    发送支付成功通知给相关人员
    
    通知对象：
    1. 管理员（所有在线管理员）
    2. 老人（订单的服务对象）
    3. 家属（如果老人有绑定的家属）
    4. 护理员（如果订单已分配）
    """
    try:
        # 获取老人信息
        elder = User.query.get(order.elder_id) if order.elder_id else None
        elder_name = elder.real_name if elder else "未知"
        
        # 构建通知内容
        title = "支付成功"
        content = f"订单「{order.service_name}」已支付成功，服务对象：{elder_name}，服务时间：{order.appointment_date or '待定'} {order.appointment_time or ''}"
        
        notifications_to_send = []
        
        # 1. 通知所有管理员
        admins = User.query.filter_by(user_type=3, status=1).all()
        for admin in admins:
            notifications_to_send.append({
                'user_id': admin.id,
                'title': title,
                'content': content,
                'type': 4,  # 任务通知
                'priority': 1
            })
        
        # 2. 通知老人（服务对象）
        if elder and elder.status == 1:
            notifications_to_send.append({
                'user_id': elder.id,
                'title': title,
                'content': content,
                'type': 2,  # 护理提醒
                'priority': 1
            })
            
            # 3. 通知家属（如果老人绑定了家属）
            # 注意：老人表中的family_id字段，或通过users.binding_elder_id反向查找
            # 根据users.py，家属的binding_elder_id指向老人，老人的family_id指向家属
            # 但检查users.py，只有家属有binding_elder_id，老人没有family_id字段
            # 所以需要通过家属的binding_elder_id来查找
            families = User.query.filter_by(binding_elder_id=elder.id, user_type=4, status=1).all()
            for family in families:
                notifications_to_send.append({
                    'user_id': family.id,
                    'title': title,
                    'content': content,
                    'type': 4,  # 任务通知
                    'priority': 1
                })
        
        # 4. 通知护理员（如果已分配）
        if order.nurse_id:
            nurse = User.query.get(order.nurse_id)
            if nurse and nurse.status == 1:
                notifications_to_send.append({
                    'user_id': nurse.id,
                    'title': '新任务通知',
                    'content': f"订单「{order.service_name}」已支付，请准备提供服务。服务对象：{elder_name}，时间：{order.appointment_date or '待定'} {order.appointment_time or ''}",
                    'type': 2,  # 护理提醒
                    'priority': 2  # 紧急（护理任务需要及时处理）
                })
        
        # 批量创建通知
        for notif in notifications_to_send:
            notification = Notification(
                user_id=notif['user_id'],
                title=notif['title'],
                content=notif['content'],
                notification_type=notif['type'],
                priority=notif['priority'],
                created_by=order.user_id  # 下单人
            )
            db.session.add(notification)
        
        db.session.commit()
        logger.info(f"支付成功通知已发送: {len(notifications_to_send)}条，订单号={order.order_no}")
        
    except Exception as e:
        logger.error(f"发送支付成功通知失败: {e}")
        # 不影响支付流程，只记录错误
