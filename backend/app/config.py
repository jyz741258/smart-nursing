import os


class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'smart-nursing-secret-key-2024'

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///smart_nursing.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-2024'
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24小时

    # Redis配置
    REDIS_HOST = os.environ.get('REDIS_HOST') or 'localhost'
    REDIS_PORT = os.environ.get('REDIS_PORT') or 6379
    REDIS_DB = os.environ.get('REDIS_DB') or 0
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')

    # 短信验证码配置
    SMS_CODE_EXPIRES = 300  # 5分钟

    # 管理员注册验证密钥
    # 注意：在生产环境中应该通过环境变量设置，并确保安全
    ADMIN_REGISTRATION_KEY = os.environ.get('ADMIN_REGISTRATION_KEY') or 'ADMIN_REGISTER_2024_SECRET'

    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # CORS配置
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS') or '*'

    # 讯飞星火AI配置
    XFYUN_APPID = os.environ.get('XFYUN_APPID') or ''
    XFYUN_API_KEY = os.environ.get('XFYUN_API_KEY') or ''
    XFYUN_API_SECRET = os.environ.get('XFYUN_API_SECRET') or ''


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}