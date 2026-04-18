from flask import Flask
from flask_cors import CORS
import redis
from dotenv import load_dotenv
import os
from .config import config
from .extensions import db

# 加载 .env 文件
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)
print(f"加载环境配置文件: {env_path}")
print(f"XFYUN_APPID: {'已设置' if os.getenv('XFYUN_APPID') else '未设置'}")
redis_client = None


def create_app(config_name='default'):
    """Flask应用工厂函数"""
    app = Flask(__name__)

    # 加载配置
    app.config.from_object(config[config_name])

    # 初始化CORS（允许跨域访问）
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://192.168.61.18:3000", "http://tf958e9b.natappfree.cc:3000", "http://tf958e9b.natappfree.cc", "*"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # 初始化数据库
    db.init_app(app)

    # 初始化Redis
    global redis_client
    try:
        redis_client = redis.Redis(
            host=app.config['REDIS_HOST'],
            port=app.config['REDIS_PORT'],
            db=app.config['REDIS_DB'],
            password=app.config['REDIS_PASSWORD'],
            decode_responses=True
        )
        redis_client.ping()
    except Exception as e:
        print(f"Redis连接失败: {e}，短信验证功能将不可用")
        redis_client = None

    # 注册蓝图
    from .routes import user_bp, nursing_bp, health_bp, care_bp, notification_bp, statistics_bp, service_bp, order_bp, ai_bp, payment_bp
    from .routes import bigdata_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(nursing_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(care_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(statistics_bp)
    app.register_blueprint(service_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(bigdata_bp)
    app.register_blueprint(payment_bp)

    # 创建数据库表
    with app.app_context():
        db.create_all()

    # 健康检查接口
    @app.route('/api/health')
    def health_check():
        return {'status': 'ok', 'message': '智慧护理平台服务运行中'}

    return app


def get_redis():
    """获取Redis客户端"""
    return redis_client
