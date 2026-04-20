from flask import request, current_app
from . import user_bp
from ..models import User, Order, Evaluation, Complaint
from ..extensions import db
from ..utils.auth import generate_token, generate_sms_code, send_sms_code, verify_sms_code, send_email_code, verify_email_code, require_token
from ..utils.response import api_response, api_error
from ..utils.validators import validate_phone, validate_password, validate_id_card


@user_bp.route('/send-email-code', methods=['POST'])
def send_email_code_api():
    """发送邮箱验证码"""
    data = request.get_json()
    email = data.get('email')

    if not email:
        return api_error('请输入邮箱地址')

    # 验证邮箱格式
    import re
    email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    if not re.match(email_regex, email):
        return api_error('邮箱格式不正确')

    code = generate_sms_code()
    send_email_code(email, code)
    return api_response({
        'code': code,
        'message': '验证码已发送'
    }, '验证码已发送至邮箱')


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
    email_code = data.get('email_code')
    user_type = data.get('user_type', 1)

    # 限制只能注册老人(1)或家属(4)
    if user_type not in [1, 4]:
        return api_error('仅允许注册老人或家属账号')

    # 验证手机号
    valid, msg = validate_phone(phone)
    if not valid:
        return api_error(msg)

    # 验证密码
    valid, msg = validate_password(password)
    if not valid:
        return api_error(msg)

    # 验证邮箱验证码
    email = data.get('email')
    if not email_code:
        return api_error('请输入验证码')
    if not verify_email_code(email, email_code):
        return api_error('验证码错误或已过期')

    # 检查用户是否已存在
    if User.query.filter_by(phone=phone).first():
        return api_error('该手机号已注册')

    # 创建用户
    user = User(
        phone=phone,
        username=phone,
        user_type=user_type,
        real_name=data.get('name'),
        gender=data.get('gender'),
        age=data.get('age'),
        id_card=data.get('id_card'),
        email=email
    )
    # 如果是家属，保存与老人的关系
    if user_type == 4:
        user.relation_with_elder = data.get('relation_with_elder')
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
        return api_error('账号或密码错误')

    token = generate_token(user.id, user.user_type)
    return api_response({
        'token': token,
        'user_id': user.id,
        'user_type': user.user_type,
        'name': user.real_name or user.username or phone,
        'phone': phone
    }, '登录成功')


@user_bp.route('/profile', methods=['GET'])
@require_token
def get_profile(current_user):
    """获取用户资料"""
    profile_data = {
        'id': current_user.id,
        'phone': current_user.phone,
        'email': current_user.email,
        'name': current_user.name,
        'gender': current_user.gender,
        'age': current_user.age,
        'id_card': current_user.id_card,
        'address': current_user.address,
        'avatar': current_user.avatar,
        'emergency_contact': current_user.emergency_contact,
        'emergency_phone': current_user.emergency_phone,
        'user_type': current_user.user_type
    }
    # 如果是家属，添加与老人的关系
    if current_user.user_type == 4:
        profile_data['relation_with_elder'] = current_user.relation_with_elder
    return api_response(profile_data)


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
        age = data['age']
        if age is not None:
            if not isinstance(age, int) or age <= 0 or age > 150:
                return api_error('年龄必须为1-150之间的整数')
        current_user.age = age
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


@user_bp.route('/elder', methods=['POST'])
@require_token
def create_elder_by_admin(current_user):
    """管理员创建老人账号"""
    if current_user.user_type != 3:
        return api_error('无权限', 403)

    data = request.get_json()
    phone = data.get('phone')
    name = data.get('name')
    gender = data.get('gender', 0)
    age = data.get('age')
    id_card = data.get('id_card')
    address = data.get('address')
    emergency_contact = data.get('emergency_contact')
    emergency_phone = data.get('emergency_phone')

    # 验证必填字段
    if not phone:
        return api_error('请输入手机号')
    if not name:
        return api_error('请输入姓名')

    # 验证手机号
    valid, msg = validate_phone(phone)
    if not valid:
        return api_error(msg)

    # 验证身份证（如果提供）
    if id_card:
        valid, msg = validate_id_card(id_card)
        if not valid:
            return api_error(msg)

    # 检查用户是否已存在
    if User.query.filter_by(phone=phone).first():
        return api_error('该手机号已注册')

    # 创建老人用户（默认密码：123456，需要首次登录修改）
    user = User(
        phone=phone,
        username=phone,
        user_type=1,  # 老人
        real_name=name,
        gender=gender,
        age=age,
        id_card=id_card,
        address=address,
        emergency_contact=emergency_contact,
        emergency_phone=emergency_phone
    )
    user.set_password('123456')  # 默认密码
    db.session.add(user)
    db.session.commit()

    return api_response({
        'id': user.id,
        'phone': user.phone,
        'name': user.real_name
    }, '老人账号创建成功，默认密码：123456')


@user_bp.route('/<int:user_id>', methods=['PUT'])
@require_token
def update_user_by_admin(current_user, user_id):
    """管理员更新用户信息（用于编辑老人信息）"""
    # 只有管理员可以更新用户信息
    if current_user.user_type != 3:
        return api_error('无权限', 403)

    user = User.query.get_or_404(user_id)
    data = request.get_json()

    # 只允许更新这些字段
    if 'name' in data:
        user.real_name = data['name']
    if 'gender' in data:
        user.gender = data['gender']
    if 'age' in data:
        age = data['age']
        if age is not None:
            if not isinstance(age, int) or age <= 0 or age > 150:
                return api_error('年龄必须为1-150之间的整数')
        user.age = age
    if 'id_card' in data:
        valid, msg = validate_id_card(data['id_card'])
        if not valid:
            return api_error(msg)
        user.id_card = data['id_card']
    if 'address' in data:
        user.address = data['address']
    if 'emergency_contact' in data:
        user.emergency_contact = data['emergency_contact']
    if 'emergency_phone' in data:
        user.emergency_phone = data['emergency_phone']

    db.session.commit()
    return api_response(message='用户信息更新成功')


@user_bp.route('/<int:user_id>', methods=['DELETE'])
@require_token
def delete_user_by_admin(current_user, user_id):
    """管理员删除用户（仅限删除老人）"""
    if current_user.user_type != 3:
        return api_error('无权限', 403)

    user = User.query.get_or_404(user_id)

    # 只能删除老人账号（user_type=1）
    if user.user_type != 1:
        return api_error('只能删除老人账号', 400)

    # 检查是否有订单引用该用户（作为老人）
    order_count = Order.query.filter_by(elder_id=user_id).count()
    if order_count > 0:
        return api_error(f'无法删除：该老人已有 {order_count} 个订单记录，请先处理相关订单', 400)

    # 检查是否有评价引用该用户
    evaluation_count = Evaluation.query.filter_by(user_id=user_id).count()
    if evaluation_count > 0:
        return api_error(f'无法删除：该老人已有 {evaluation_count} 条评价记录，请先处理', 400)

    # 检查是否有投诉引用该用户
    complaint_count = Complaint.query.filter_by(user_id=user_id).count()
    if complaint_count > 0:
        return api_error(f'无法删除：该老人已有 {complaint_count} 条投诉记录，请先处理', 400)

    try:
        db.session.delete(user)
        db.session.commit()
        return api_response(message='老人账号删除成功')
    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        print(f'[Error] 删除用户失败: {error_msg}')
        return api_error('删除失败：' + error_msg, 500)

