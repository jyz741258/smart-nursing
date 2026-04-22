from flask import request
from . import medication_bp
from ..models import User, MedicationReminder
from ..extensions import db
from ..utils.auth import require_token
from ..utils.response import api_response, api_error


@medication_bp.route('/reminders', methods=['GET'])
@require_token
def get_medication_reminders(current_user):
    """获取用药提醒列表"""
    reminders = MedicationReminder.query.filter_by(user_id=current_user.id).all()
    
    reminder_list = []
    for reminder in reminders:
        reminder_list.append({
            'id': reminder.id,
            'medication_name': reminder.medication_name,
            'time': reminder.time,
            'dosage': reminder.dosage,
            'days': reminder.days.split(','),
            'notes': reminder.notes,
            'completed': reminder.completed
        })
    
    return api_response(reminder_list)


@medication_bp.route('/reminders', methods=['POST'])
@require_token
def create_medication_reminder(current_user):
    """创建用药提醒"""
    data = request.get_json()
    medication_name = data.get('medication_name')
    time = data.get('time')
    dosage = data.get('dosage')
    days = data.get('days', [])
    notes = data.get('notes', '')
    user_id = data.get('user_id', current_user.id)
    
    if not medication_name or not time or not dosage or not days:
        return api_error('请填写完整信息')
    
    # 管理员可以为其他用户创建提醒，普通用户只能为自己创建
    if current_user.user_type != 3 and user_id != current_user.id:
        return api_error('无权限为其他用户创建提醒')
    
    reminder = MedicationReminder(
        user_id=user_id,
        medication_name=medication_name,
        time=time,
        dosage=dosage,
        days=','.join(days),
        notes=notes,
        completed=False
    )
    
    db.session.add(reminder)
    db.session.commit()
    
    return api_response({
        'id': reminder.id,
        'medication_name': reminder.medication_name,
        'time': reminder.time,
        'dosage': reminder.dosage,
        'days': reminder.days.split(','),
        'notes': reminder.notes,
        'completed': reminder.completed
    }, '添加成功')


@medication_bp.route('/reminders/<int:reminder_id>/complete', methods=['PUT'])
@require_token
def complete_medication_reminder(current_user, reminder_id):
    """标记用药提醒为已完成"""
    reminder = MedicationReminder.query.filter_by(id=reminder_id, user_id=current_user.id).first()
    if not reminder:
        return api_error('提醒不存在')
    
    reminder.completed = True
    db.session.commit()
    
    return api_response({'completed': True}, '标记成功')


@medication_bp.route('/reminders/<int:reminder_id>/uncomplete', methods=['PUT'])
@require_token
def uncomplete_medication_reminder(current_user, reminder_id):
    """标记用药提醒为未完成"""
    reminder = MedicationReminder.query.filter_by(id=reminder_id, user_id=current_user.id).first()
    if not reminder:
        return api_error('提醒不存在')
    
    reminder.completed = False
    db.session.commit()
    
    return api_response({'completed': False}, '标记成功')


@medication_bp.route('/reminders/<int:reminder_id>', methods=['DELETE'])
@require_token
def delete_medication_reminder(current_user, reminder_id):
    """删除用药提醒"""
    reminder = MedicationReminder.query.filter_by(id=reminder_id, user_id=current_user.id).first()
    if not reminder:
        return api_error('提醒不存在')
    
    db.session.delete(reminder)
    db.session.commit()
    
    return api_response(message='删除成功')
