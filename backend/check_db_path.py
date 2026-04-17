"""检查Flask应用的数据库路径"""
from app import create_app

app = create_app('default')

with app.app_context():
    print(f"数据库URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # 尝试访问数据库
    from app.extensions import db
    print(f"数据库引擎: {db.engine}")
    print(f"数据库URL: {db.engine.url}")