from flask import request
from . import service_bp
from ..extensions import db
from ..models import Service
from ..utils.response import api_response, api_error, page_response
from ..utils import require_token


@service_bp.route('/', methods=['GET'])
def get_services():
    """获取服务列表（公开接口）"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    category = request.args.get('category')
    status = request.args.get('status', type=int)
    is_recommended = request.args.get('is_recommended', type=int)

    query = Service.query

    if category:
        query = query.filter_by(category=category)
    if status is not None:
        query = query.filter_by(status=status)
    if is_recommended is not None:
        query = query.filter_by(is_recommended=is_recommended)

    query = query.order_by(Service.sort_order.asc(), Service.id.asc())

    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    services = [s.to_dict() for s in pagination.items]

    return page_response(services, pagination.total, page, page_size)


@service_bp.route('/<int:service_id>', methods=['GET'])
def get_service_detail(service_id):
    """获取服务详情（公开接口）"""
    service = Service.query.get_or_404(service_id)
    return api_response(service.to_dict())


@service_bp.route('/categories', methods=['GET'])
def get_service_categories():
    """获取服务类别列表（公开接口）"""
    categories = db.session.query(Service.category).distinct().all()
    categories = [c[0] for c in categories]
    return api_response(categories)


@service_bp.route('/', methods=['POST'])
@require_token
def create_service(current_user):
    """创建服务"""
    # 只有管理员可以创建服务
    if current_user.user_type != 3:
        return api_error('无权限', 403)

    data = request.get_json()
    service = Service(
        name=data.get('name'),
        category=data.get('category'),
        description=data.get('description'),
        price=data.get('price'),
        unit=data.get('unit'),
        duration=data.get('duration'),
        image_url=data.get('imageUrl'),
        icons=data.get('icons'),
        details=data.get('details'),
        precautions=data.get('precautions'),
        requirements=data.get('requirements'),
        stock=data.get('stock', 999),
        status=data.get('status', 1),
        is_recommended=data.get('isRecommended', 0),
        sort_order=data.get('sortOrder', 0)
    )

    db.session.add(service)
    db.session.commit()

    return api_response(service.to_dict(), '服务创建成功')


@service_bp.route('/<int:service_id>', methods=['PUT'])
@require_token
def update_service(current_user, service_id):
    """更新服务"""
    # 只有管理员可以更新服务
    if current_user.user_type != 3:
        return api_error('无权限', 403)

    service = Service.query.get_or_404(service_id)
    data = request.get_json()

    if 'name' in data:
        service.name = data['name']
    if 'category' in data:
        service.category = data['category']
    if 'description' in data:
        service.description = data['description']
    if 'price' in data:
        service.price = data['price']
    if 'unit' in data:
        service.unit = data['unit']
    if 'duration' in data:
        service.duration = data['duration']
    if 'imageUrl' in data:
        service.image_url = data['imageUrl']
    if 'icons' in data:
        service.icons = data['icons']
    if 'details' in data:
        service.details = data['details']
    if 'precautions' in data:
        service.precautions = data['precautions']
    if 'requirements' in data:
        service.requirements = data['requirements']
    if 'stock' in data:
        service.stock = data['stock']
    if 'status' in data:
        service.status = data['status']
    if 'isRecommended' in data:
        service.is_recommended = data['isRecommended']
    if 'sortOrder' in data:
        service.sort_order = data['sortOrder']

    db.session.commit()
    return api_response(service.to_dict(), '服务更新成功')


@service_bp.route('/<int:service_id>', methods=['DELETE'])
@require_token
def delete_service(current_user, service_id):
    """删除服务"""
    # 只有管理员可以删除服务
    if current_user.user_type != 3:
        return api_error('无权限', 403)

    service = Service.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()

    return api_response(message='服务删除成功')
