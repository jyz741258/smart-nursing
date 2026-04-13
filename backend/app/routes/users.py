from flask import request, current_app
from . import user_bp
from ..models import User
from ..extensions import db
from ..utils.auth import generate_token, generate_sms_code, send_sms_code, verify_sms_code, require_token
from ..utils.response import api_response, api_error
from ..utils.validators import validate_phone, validate_password, validate_id_card


@user_bp.route('/send-sms', methods=['POST'])
def send_sms():
    """发送短信验证码"""
    data = request.get_json()
    phone = data.get('phone')

    valid, msg = validate_phone(phone)
    if not valid:
        return api_error(msg)

    code = generate_sms_code()
    send_sms_code(phone, code)
    # 返回验证码给前端显示（实际项目中应通过其他方式如邮件推送等）
    return api_response({
        'code': code,
        'message': '验证码已发送，请在页面查看'
    }, '验证码已发送')


@user_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    phone = data.get('phone')
    password = data.get('password')
    sms_code = data.get('sms_code')
    user_type = data.get('user_type', 1)
    admin_verify_code = data.get('admin_verify_code')  # 管理员注册验证码

    # 验证手机号
    valid, msg = validate_phone(phone)
    if not valid:
        return api_error(msg)

    # 验证密码
    valid, msg = validate_password(password)
    if not valid:
        return api_error(msg)

    # 验证短信验证码
    if not verify_sms_code(phone, sms_code):
        return api_error('验证码错误或已过期')

    # 检查用户是否已存在
    if User.query.filter_by(phone=phone).first():
        return api_error('该手机号已注册')

    # 管理员注册需要额外验证
    if user_type == 3:
        # 验证管理员注册密钥
        admin_key = current_app.config.get('ADMIN_REGISTRATION_KEY')
        if not admin_verify_code or admin_verify_code != admin_key:
            return api_error('管理员注册需要正确的验证密钥')

    # 创建用户
    user = User(
        phone=phone,
        username=phone,  # 默认用户名使用手机号
        user_type=user_type,
        real_name=data.get('name'),
        gender=data.get('gender'),
        age=data.get('age'),
        id_card=data.get('id_card')
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = generate_token(user.id, user.user_type)
    return api_response({
        'token': token,
        'user_id': user.id,
        'user_type': user.user_type
    }, '注册成功')


@user_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    phone = data.get('phone')
    password = data.get('password')

    valid, msg = validate_phone(phone)
    if not valid:
        return api_error(msg)

    user = User.query.filter_by(phone=phone).first()
    if not user or not user.check_password(password):
        return api_error('手机号或密码错误')

    token = generate_token(user.id, user.user_type)
    return api_response({
        'token': token,
        'user_id': user.id,
        'user_type': user.user_type,
        'name': user.name
    }, '登录成功')


@user_bp.route('/profile', methods=['GET'])
@require_token
def get_profile(current_user):
    """获取用户资料"""
    return api_response({
        'id': current_user.id,
        'phone': current_user.phone,
        'name': current_user.name,
        'gender': current_user.gender,
        'age': current_user.age,
        'id_card': current_user.id_card,
        'address': current_user.address,
        'avatar': current_user.avatar,
        'emergency_contact': current_user.emergency_contact,
        'emergency_phone': current_user.emergency_phone,
        'user_type': current_user.user_type
    })


@user_bp.route('/profile', methods=['PUT'])
@require_token
def update_profile(current_user):
    """更新用户资料"""
    data = request.get_json()

    if 'name' in data:
        current_user.name = data['name']
    if 'gender' in data:
        current_user.gender = data['gender']
    if 'age' in data:
        current_user.age = data['age']
    if 'id_card' in data:
        valid, msg = validate_id_card(data['id_card'])
        if not valid:
            return api_error(msg)
        current_user.id_card = data['id_card']
    if 'address' in data:
        current_user.address = data['address']
    if 'avatar' in data:
        current_user.avatar = data['avatar']
    if 'emergency_contact' in data:
        current_user.emergency_contact = data['emergency_contact']
    if 'emergency_phone' in data:
        current_user.emergency_phone = data['emergency_phone']

    db.session.commit()
    return api_response(message='资料更新成功')


@user_bp.route('/change-password', methods=['POST'])
@require_token
def change_password(current_user):
    """修改密码"""
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not current_user.check_password(old_password):
        return api_error('原密码错误')

    valid, msg = validate_password(new_password)
    if not valid:
        return api_error(msg)

    current_user.set_password(new_password)
    db.session.commit()
    return api_response(message='密码修改成功')


@user_bp.route('/elder/list', methods=['GET'])
@require_token
def get_elder_list(current_user):
    """获取老人列表"""
    elders = User.query.filter_by(user_type=1).all()
    return api_response([{
        'id': elder.id,
        'name': elder.name,
        'gender': elder.gender,
        'age': elder.age,
        'address': elder.address,
        'avatar': elder.avatar
    } for elder in elders])


@user_bp.route('/binding-elder', methods=['GET'])
@require_token
def get_binding_elder(current_user):
    """获取家属绑定的老人信息"""
    if current_user.user_type != 4:  # 家属
        return api_error('仅家属用户可以查看绑定信息', 403)

    if current_user.binding_elder_id:
        elder = User.query.get(current_user.binding_elder_id)
        if elder:
            return api_response({
                'id': elder.id,
                'name': elder.name,
                'gender': elder.gender,
                'age': elder.age,
                'address': elder.address,
                'avatar': elder.avatar,
                'phone': elder.phone
            })
        else:
            return api_error('绑定的老人不存在', 404)
    else:
        return api_response(None)


@user_bp.route('/binding-elder', methods=['POST'])
@require_token
def bind_elder(current_user):
    """家属绑定老人"""
    if current_user.user_type != 4:  # 家属
        return api_error('仅家属用户可以绑定老人', 403)

    data = request.get_json()
    elder_id = data.get('elder_id')

    if not elder_id:
        return api_error('请选择要绑定的老人')

    # 检查老人是否存在且确实是老人类型
    elder = User.query.filter_by(id=elder_id, user_type=1).first()
    if not elder:
        return api_error('老人不存在或用户类型不正确')

    # 检查是否已经绑定
    if current_user.binding_elder_id:
        return api_error('您已经绑定了老人，请先解绑')

    # 绑定老人
    current_user.binding_elder_id = elder_id
    db.session.commit()

    return api_response(message='绑定成功')


@user_bp.route('/binding-elder', methods=['DELETE'])
@require_token
def unbind_elder(current_user):
    """家属解绑老人"""
    if current_user.user_type != 4:  # 家属
        return api_error('仅家属用户可以解绑', 403)

    if not current_user.binding_elder_id:
        return api_error('您尚未绑定老人')

    current_user.binding_elder_id = None
    db.session.commit()

    return api_response(message='解绑成功')


@user_bp.route('/workers', methods=['GET'])
@require_token
def get_worker_list(current_user):
    """获取护工列表"""
    workers = User.query.filter_by(user_type=2).all()
    return api_response([{
        'id': worker.id,
        'name': worker.name,
        'gender': worker.gender,
        'age': worker.age,
        'avatar': worker.avatar,
        'phone': worker.phone
    } for worker in workers])
