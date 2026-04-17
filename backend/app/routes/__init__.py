from flask import Blueprint

# 创建蓝图（除了payment蓝图，在payment.py中定义）
user_bp = Blueprint('user', __name__, url_prefix='/api/users')
nursing_bp = Blueprint('nursing', __name__, url_prefix='/api/nursing')
health_bp = Blueprint('health', __name__, url_prefix='/api/health')
care_bp = Blueprint('care', __name__, url_prefix='/api/care')
notification_bp = Blueprint('notification', __name__, url_prefix='/api/notifications')
statistics_bp = Blueprint('statistics', __name__, url_prefix='/api/statistics')
service_bp = Blueprint('service', __name__, url_prefix='/api/services')
order_bp = Blueprint('order', __name__, url_prefix='/api/orders')
evaluation_bp = Blueprint('evaluation', __name__, url_prefix='/api/evaluations')
ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')
bigdata_bp = Blueprint('bigdata', __name__, url_prefix='/api/bigdata')

# 导入路由（payment.py会导入payment_bp）
from . import users, nursing, health, care, notifications, statistics, service, order, ai, bigdata

# 导入payment蓝图（必须先导入payment.py，因为它定义了payment_bp）
from . import payment
payment_bp = payment.payment_bp

try:
    from . import worker_evaluation
except ImportError:
    pass
