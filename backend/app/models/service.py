from datetime import datetime
from ..extensions import db


class Service(db.Model):
    """服务项目模型"""
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, comment='服务名称')
    category = db.Column(db.String(50), nullable=False, comment='服务类别')
    description = db.Column(db.Text, comment='服务描述')
    price = db.Column(db.Numeric(10, 2), nullable=False, comment='服务价格')
    unit = db.Column(db.String(20), default='次', comment='计费单位')
    duration = db.Column(db.Integer, comment='预计时长(分钟)')
    image_url = db.Column(db.String(255), comment='服务图片')
    icons = db.Column(db.String(255), comment='服务图标')
    details = db.Column(db.Text, comment='详细说明')
    precautions = db.Column(db.Text, comment='注意事项')
    requirements = db.Column(db.Text, comment='服务要求')
    stock = db.Column(db.Integer, default=999, comment='库存')
    sales_count = db.Column(db.Integer, default=0, comment='销量')
    rating = db.Column(db.Numeric(3, 2), default=5.00, comment='评分')
    evaluation_count = db.Column(db.Integer, default=0, comment='评价数')
    status = db.Column(db.SmallInteger, default=1, comment='状态: 0-下架, 1-上架')
    is_recommended = db.Column(db.SmallInteger, default=0, comment='是否推荐: 0-否, 1-是')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'price': float(self.price) if self.price else 0,
            'unit': self.unit,
            'duration': self.duration,
            'imageUrl': self.image_url,
            'icons': self.icons,
            'details': self.details,
            'precautions': self.precautions,
            'requirements': self.requirements,
            'stock': self.stock,
            'salesCount': self.sales_count,
            'rating': float(self.rating) if self.rating else 5.0,
            'evaluationCount': self.evaluation_count,
            'status': self.status,
            'isRecommended': self.is_recommended,
            'sortOrder': self.sort_order,
            'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
