from flask import request
from datetime import datetime
from . import evaluation_bp
from ..extensions import db
from ..models import WorkerEvaluation, User, Order
from ..utils.response import api_response, api_error, page_response
from ..utils import require_token


@evaluation_bp.route('/worker', methods=['POST'])
@require_token
def create_worker_evaluation(current_user):
    """老人/家属评价护工"""
    data = request.get_json()

    elder_id = data.get('elder_id')
    worker_id = data.get('worker_id')
    order_id = data.get('order_id')
    overall_rating = data.get('overall_rating')
    professionalism_rating = data.get('professionalism_rating', 5)
    attitude_rating = data.get('attitude_rating', 5)
    punctuality_rating = data.get('punctuality_rating', 5)
    skill_rating = data.get('skill_rating', 5)
    content = data.get('content')
    tags = data.get('tags')
    is_anonymous = data.get('is_anonymous', 0)

    # 验证参数
    if not elder_id or not worker_id or not overall_rating:
        return api_error('请填写必要信息（老人、护工、评分）')

    # 评分范围验证 1-5
    try:
        rating = float(overall_rating)
        if not (1 <= rating <= 5):
            return api_error('评分必须在1-5之间')
    except:
        return api_error('评分格式错误')

    # 验证老人是否存在
    elder = User.query.filter_by(id=elder_id, user_type=1).first()
    if not elder:
        return api_error('老人信息不存在')

    # 验证护工是否存在
    worker = User.query.filter_by(id=worker_id, user_type=2).first()
    if not worker:
        return api_error('护工信息不存在')

    # 验证订单（如果提供）
    if order_id:
        order = Order.query.get(order_id)
        if not order:
            return api_error('订单不存在')
        # 验证订单属于该老人
        if order.elder_id != elder_id:
            return api_error('订单不属于该老人')

    # 创建评价
    evaluation = WorkerEvaluation(
        elder_id=elder_id,
        worker_id=worker_id,
        order_id=order_id,
        overall_rating=overall_rating,
        professionalism_rating=professionalism_rating,
        attitude_rating=attitude_rating,
        punctuality_rating=punctuality_rating,
        skill_rating=skill_rating,
        content=content,
        tags=tags,
        is_anonymous=is_anonymous
    )

    db.session.add(evaluation)
    db.session.commit()

    return api_response({'id': evaluation.id}, '评价提交成功')


@evaluation_bp.route('/worker', methods=['GET'])
@require_token
def get_worker_evaluations(current_user):
    """获取护工评价列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    worker_id = request.args.get('worker_id', type=int)
    elder_id = request.args.get('elder_id', type=int)
    order_id = request.args.get('order_id', type=int)

    query = WorkerEvaluation.query.filter_by(status=1)

    # 筛选条件
    if worker_id:
        query = query.filter_by(worker_id=worker_id)
    if elder_id:
        query = query.filter_by(elder_id=elder_id)
    if order_id:
        query = query.filter_by(order_id=order_id)

    # 管理��可以查看所有，其他人只能查看自己相关的
    if current_user.user_type != 3:  # 非管理员
        if current_user.user_type == 1:  # 老人
            query = query.filter_by(elder_id=current_user.id)
        elif current_user.user_type == 4:  # 家属
            # 家属只能查看绑定老人的评价
            if current_user.binding_elder_id:
                query = query.filter_by(elder_id=current_user.binding_elder_id)
            else:
                return page_response([], 0, page, page_size)  # 未绑定老人，返回空

    query = query.order_by(WorkerEvaluation.created_at.desc())

    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    evaluations = [e.to_dict() for e in pagination.items]

    return page_response(evaluations, pagination.total, page, page_size)


@evaluation_bp.route('/worker/<int:evaluation_id>', methods=['GET'])
@require_token
def get_worker_evaluation_detail(current_user, evaluation_id):
    """获取护工评价详情"""
    evaluation = WorkerEvaluation.query.get_or_404(evaluation_id)

    # 权限验证
    if current_user.user_type != 3:  # 非管理员
        if current_user.user_type == 1:  # 老人
            if evaluation.elder_id != current_user.id:
                return api_error('无权查看', 403)
        elif current_user.user_type == 4:  # 家属
            if current_user.binding_elder_id and evaluation.elder_id != current_user.binding_elder_id:
                return api_error('无权查看', 403)

    return api_response(evaluation.to_dict())


@evaluation_bp.route('/worker/<int:evaluation_id>/reply', methods=['POST'])
@require_token
def reply_worker_evaluation(current_user, evaluation_id):
    """护工回复评价（仅管理员和护工本人可回复）"""
    evaluation = WorkerEvaluation.query.get_or_404(evaluation_id)

    # 权限验证：仅管理员和护工本人可回复
    if current_user.user_type != 3 and current_user.id != evaluation.worker_id:
        return api_error('无权回复', 403)

    data = request.get_json()
    reply_content = data.get('reply_content')

    if not reply_content or not reply_content.strip():
        return api_error('请填写回复内容')

    evaluation.reply_content = reply_content.strip()
    evaluation.reply_time = datetime.now()
    db.session.commit()

    return api_response({}, '回复成功')


@evaluation_bp.route('/worker/stats/<int:worker_id>', methods=['GET'])
@require_token
def get_worker_evaluation_stats(current_user, worker_id):
    """获取护工评价统计"""
    # 验证护工是否存在
    worker = User.query.filter_by(id=worker_id, user_type=2).first()
    if not worker:
        return api_error('护工不存在', 404)

    # 获取所有已显示的评价
    evaluations = WorkerEvaluation.query.filter_by(worker_id=worker_id, status=1).all()

    if not evaluations:
        return api_response({
            'total_count': 0,
            'average_rating': 0,
            'dimension_avg': {
                'professionalism': 0,
                'attitude': 0,
                'punctuality': 0,
                'skill': 0
            },
            'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        })

    # 计算统计信息
    total_count = len(evaluations)
    avg_overall = sum(float(e.overall_rating) for e in evaluations) / total_count

    # 维度平均分
    dimension_avg = {
        'professionalism': sum(e.professionalism_rating for e in evaluations) / total_count,
        'attitude': sum(e.attitude_rating for e in evaluations) / total_count,
        'punctuality': sum(e.punctuality_rating for e in evaluations) / total_count,
        'skill': sum(e.skill_rating for e in evaluations) / total_count
    }

    # 评分分布
    distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for e in evaluations:
        rating = int(float(e.overall_rating))
        distribution[rating] = distribution.get(rating, 0) + 1

    return api_response({
        'total_count': total_count,
        'average_rating': round(avg_overall, 1),
        'dimension_avg': {
            'professionalism': round(dimension_avg['professionalism'], 1),
            'attitude': round(dimension_avg['attitude'], 1),
            'punctuality': round(dimension_avg['punctuality'], 1),
            'skill': round(dimension_avg['skill'], 1)
        },
        'rating_distribution': distribution
    })
