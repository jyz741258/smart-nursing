from flask import jsonify


def api_response(data=None, message='操作成功', code=200):
    """统一API响应格式"""
    response = {
        'code': code,
        'message': message
    }
    if data is not None:
        response['data'] = data
    return jsonify(response)


def api_error(message='操作失败', code=400, errors=None):
    """统一错误响应格式"""
    response = {
        'code': code,
        'message': message
    }
    if errors:
        response['errors'] = errors
    return jsonify(response)


def page_response(items, total, page, page_size, message='查询成功'):
    """分页响应格式"""
    return jsonify({
        'code': 200,
        'message': message,
        'data': {
            'items': items,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size if page_size > 0 else 0
        }
    })
