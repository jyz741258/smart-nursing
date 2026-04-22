from flask import request
from . import emergency_bp
from ..models import User, EmergencyCall
from ..extensions import db
from ..utils.auth import require_token
from ..utils.response import api_response, api_error
import datetime


@emergency_bp.route('/call', methods=['POST'])
@require_token
def emergency_call(current_user):
    """紧急呼叫API"""
    data = request.get_json()
    elder_id = data.get('elder_id') or current_user.id
    call_type = data.get('type', 'sos')
    location = data.get('location', '未知位置')
    
    # 验证老人ID
    elder = User.query.get(elder_id)
    if not elder or elder.user_type != 1:
        return api_error('老人不存在')
    
    # 创建紧急呼叫记录
    emergency_call = EmergencyCall(
        elder_id=elder_id,
        type=call_type,
        location=location,
        status='pending',
        created_at=datetime.datetime.now()
    )
    db.session.add(emergency_call)
    db.session.commit()
    
    # 自动分配给最近的护理员（这里简化处理，分配给第一个可用的护理员）
    worker = User.query.filter_by(user_type=2).first()
    if worker:
        emergency_call.assigned_worker_id = worker.id
        emergency_call.status = 'assigned'
        db.session.commit()
    
    # 模拟通知管理员和家属
    print(f"紧急呼叫通知：老人 {elder.name} 在 {location} 发起了紧急呼叫")
    
    return api_response({
        'call_id': emergency_call.id,
        'elder_id': elder_id,
        'status': emergency_call.status,
        'assigned_worker': worker.name if worker else None
    }, '紧急呼叫已发送')


@emergency_bp.route('/calls', methods=['GET'])
@require_token
def get_emergency_calls(current_user):
    """获取紧急呼叫列表"""
    # 管理员可以查看所有呼叫
    if current_user.user_type == 3:
        calls = EmergencyCall.query.order_by(EmergencyCall.created_at.desc()).all()
    # 护理员只能查看分配给自己的呼叫
    elif current_user.user_type == 2:
        calls = EmergencyCall.query.filter_by(assigned_worker_id=current_user.id).order_by(EmergencyCall.created_at.desc()).all()
    # 家属只能查看绑定老人的呼叫
    elif current_user.user_type == 4:
        if not current_user.binding_elder_id:
            return api_error('请先绑定老人')
        calls = EmergencyCall.query.filter_by(elder_id=current_user.binding_elder_id).order_by(EmergencyCall.created_at.desc()).all()
    else:
        return api_error('无权限', 403)
    
    call_list = []
    for call in calls:
        elder = User.query.get(call.elder_id)
        worker = User.query.get(call.assigned_worker_id) if call.assigned_worker_id else None
        call_list.append({
            'id': call.id,
            'elder_id': call.elder_id,
            'elder_name': elder.name if elder else '未知老人',
            'type': call.type,
            'location': call.location,
            'status': call.status,
            'assigned_worker_id': call.assigned_worker_id,
            'assigned_worker_name': worker.name if worker else None,
            'response_time': call.response_time,
            'completed_at': call.completed_at,
            'created_at': call.created_at
        })
    
    return api_response(call_list)


@emergency_bp.route('/calls/<int:call_id>/respond', methods=['POST'])
@require_token
def respond_to_call(current_user, call_id):
    """护理员响应紧急呼叫"""
    if current_user.user_type != 2:
        return api_error('只有护理员可以响应紧急呼叫', 403)
    
    call = EmergencyCall.query.get(call_id)
    if not call:
        return api_error('呼叫记录不存在')
    
    if call.assigned_worker_id != current_user.id:
        return api_error('该呼叫未分配给您')
    
    call.status = 'responding'
    call.response_time = datetime.datetime.now()
    db.session.commit()
    
    return api_response(message='已响应紧急呼叫')


@emergency_bp.route('/calls/<int:call_id>/complete', methods=['POST'])
@require_token
def complete_call(current_user, call_id):
    """护理员完成紧急呼叫处理"""
    if current_user.user_type != 2:
        return api_error('只有护理员可以完成紧急呼叫', 403)
    
    call = EmergencyCall.query.get(call_id)
    if not call:
        return api_error('呼叫记录不存在')
    
    if call.assigned_worker_id != current_user.id:
        return api_error('该呼叫未分配给您')
    
    call.status = 'completed'
    call.completed_at = datetime.datetime.now()
    db.session.commit()
    
    return api_response(message='紧急呼叫已处理完成')
