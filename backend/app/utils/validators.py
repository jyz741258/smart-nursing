import re


def validate_phone(phone):
    """验证手机号格式"""
    if not phone:
        return False, '手机号不能为空'
    pattern = r'^1[3-9]\d{9}$'
    if not re.match(pattern, phone):
        return False, '手机号格式不正确'
    return True, None


def validate_password(password):
    """验证密码强度"""
    if not password:
        return False, '密码不能为空'
    if len(password) < 6:
        return False, '密码长度不能少于6位'
    if len(password) > 20:
        return False, '密码长度不能超过20位'
    return True, None


def validate_id_card(id_card):
    """验证身份证号格式"""
    if not id_card:
        return True, None
    pattern = r'^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$'
    if not re.match(pattern, id_card):
        return False, '身份证号格式不正确'
    return True, None


def validate_email(email):
    """验证邮箱格式"""
    if not email:
        return True, None
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, '邮箱格式不正确'
    return True, None
