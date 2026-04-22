from flask import request
from . import location_bp
from ..models import User, LocationRecord
from ..extensions import db
from ..utils.auth import require_token
from ..utils.response import api_response, api_error
import datetime


@location_bp.route('/update', methods=['POST'])
@require_token
def update_location(current_user):
    """更新位置信息"""
    data = request.get_json()
    longitude = data.get('longitude')
    latitude = data.get('latitude')
    accuracy = data.get('accuracy', 10)
    altitude = data.get('altitude', 0)
    speed = data.get('speed', 0)
    direction = data.get('direction', 0)
    location_name = data.get('location_name', '未知位置')
    
    if not longitude or not latitude:
        return api_error('经纬度不能为空')
    
    # 创建位置记录
    location_record = LocationRecord(
        user_id=current_user.id,
        longitude=longitude,
        latitude=latitude,
        accuracy=accuracy,
        altitude=altitude,
        speed=speed,
        direction=direction,
        location_name=location_name,
        timestamp=datetime.datetime.now()
    )
    
    db.session.add(location_record)
    db.session.commit()
    
    return api_response({
        'id': location_record.id,
        'longitude': location_record.longitude,
        'latitude': location_record.latitude,
        'location_name': location_record.location_name,
        'timestamp': location_record.timestamp
    }, '位置更新成功')


@location_bp.route('/current', methods=['GET'])
@require_token
def get_current_location(current_user):
    """获取当前位置"""
    # 获取用户最新的位置记录
    latest_location = LocationRecord.query.filter_by(
        user_id=current_user.id
    ).order_by(LocationRecord.timestamp.desc()).first()
    
    if not latest_location:
        return api_error('暂无位置信息')
    
    return api_response({
        'longitude': latest_location.longitude,
        'latitude': latest_location.latitude,
        'accuracy': latest_location.accuracy,
        'altitude': latest_location.altitude,
        'speed': latest_location.speed,
        'direction': latest_location.direction,
        'location_name': latest_location.location_name,
        'timestamp': latest_location.timestamp
    })


@location_bp.route('/history', methods=['GET'])
@require_token
def get_location_history(current_user):
    """获取位置历史记录"""
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    limit = request.args.get('limit', 100, type=int)
    
    query = LocationRecord.query.filter_by(user_id=current_user.id)
    
    if start_time:
        try:
            start_dt = datetime.datetime.fromisoformat(start_time)
            query = query.filter(LocationRecord.timestamp >= start_dt)
        except ValueError:
            pass
    
    if end_time:
        try:
            end_dt = datetime.datetime.fromisoformat(end_time)
            query = query.filter(LocationRecord.timestamp <= end_dt)
        except ValueError:
            pass
    
    records = query.order_by(LocationRecord.timestamp.desc()).limit(limit).all()
    
    history = []
    for record in records:
        history.append({
            'id': record.id,
            'longitude': record.longitude,
            'latitude': record.latitude,
            'accuracy': record.accuracy,
            'altitude': record.altitude,
            'speed': record.speed,
            'direction': record.direction,
            'location_name': record.location_name,
            'timestamp': record.timestamp
        })
    
    return api_response(history)


@location_bp.route('/elder/<int:elder_id>/current', methods=['GET'])
@require_token
def get_elder_current_location(current_user, elder_id):
    """获取老人当前位置（家属或管理员）"""
    # 验证权限：只有家属（绑定该老人）或管理员可以查看
    if current_user.user_type == 4:
        if current_user.binding_elder_id != elder_id:
            return api_error('无权限查看该老人位置', 403)
    elif current_user.user_type != 3:
        return api_error('无权限查看老人位置', 403)
    
    # 获取老人最新的位置记录
    latest_location = LocationRecord.query.filter_by(
        user_id=elder_id
    ).order_by(LocationRecord.timestamp.desc()).first()
    
    if not latest_location:
        return api_error('暂无位置信息')
    
    return api_response({
        'longitude': latest_location.longitude,
        'latitude': latest_location.latitude,
        'accuracy': latest_location.accuracy,
        'altitude': latest_location.altitude,
        'speed': latest_location.speed,
        'direction': latest_location.direction,
        'location_name': latest_location.location_name,
        'timestamp': latest_location.timestamp
    })


@location_bp.route('/elder/<int:elder_id>/history', methods=['GET'])
@require_token
def get_elder_location_history(current_user, elder_id):
    """获取老人位置历史记录（家属或管理员）"""
    # 验证权限：只有家属（绑定该老人）或管理员可以查看
    if current_user.user_type == 4:
        if current_user.binding_elder_id != elder_id:
            return api_error('无权限查看该老人位置', 403)
    elif current_user.user_type != 3:
        return api_error('无权限查看老人位置', 403)
    
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    limit = request.args.get('limit', 100, type=int)
    
    query = LocationRecord.query.filter_by(user_id=elder_id)
    
    if start_time:
        try:
            start_dt = datetime.datetime.fromisoformat(start_time)
            query = query.filter(LocationRecord.timestamp >= start_dt)
        except ValueError:
            pass
    
    if end_time:
        try:
            end_dt = datetime.datetime.fromisoformat(end_time)
            query = query.filter(LocationRecord.timestamp <= end_dt)
        except ValueError:
            pass
    
    records = query.order_by(LocationRecord.timestamp.desc()).limit(limit).all()
    
    history = []
    for record in records:
        history.append({
            'id': record.id,
            'longitude': record.longitude,
            'latitude': record.latitude,
            'accuracy': record.accuracy,
            'altitude': record.altitude,
            'speed': record.speed,
            'direction': record.direction,
            'location_name': record.location_name,
            'timestamp': record.timestamp
        })
    
    return api_response(history)
