"""调试路由注册"""
from flask import Flask, Blueprint

# 创建一个简单的测试蓝图
test_bp = Blueprint('test', __name__, url_prefix='/api/test')

@test_bp.route('/hello', methods=['GET'])
def hello():
    return {'message': 'Hello'}

# 创建一个应用并注册
app = Flask(__name__)
app.register_blueprint(test_bp)

print("Routes in test blueprint:")
for rule in app.url_map.iter_rules():
    if rule.endpoint.startswith('test.'):
        print(f"  {rule.methods} {rule.rule} -> {rule.endpoint}")

# 现在测试真实的 payment.py
print("\n\nTesting payment.py:")

# 模拟 app/__init__.py 的导入
import sys
sys.path.insert(0, 'app')

# 手动导入 payment 模块
from routes import payment

print(f"\npayment_bp: {payment.payment_bp}")
print(f"payment_bp name: {payment.payment_bp.name}")
print(f"payment_bp url_prefix: {payment.payment_bp.url_prefix}")

# 查看 payment 模块中的所有函数
print("\nFunctions in payment module:")
for name in dir(payment):
    if not name.startswith('_'):
        obj = getattr(payment, name)
        if callable(obj):
            print(f"  {name}: {type(obj)}")