from flask import Blueprint

# 创建蓝图
user_bp = Blueprint('user', __name__, url_prefix='/api/users')
nursing_bp = Blueprint('nursing', __name__, url_prefix='/api/nursing')
health_bp = Blueprint('health', __name__, url_prefix='/api/health')
care_bp = Blueprint('care', __name__, url_prefix='/api/care')
notification_bp = Blueprint('notification', __name__, url_prefix='/api/notifications')
statistics_bp = Blueprint('statistics', __name__, url_prefix='/api/statistics')

# 导入路由
from . import users, nursing, health, care, notifications, statistics
