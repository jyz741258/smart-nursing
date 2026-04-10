from datetime import datetime
from ..extensions import db


class Address(db.Model):
    """服务地址模型"""
    __tablename__ = 'addresses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    contact_name = db.Column(db.String(50), nullable=False, comment='联系人姓名')
    contact_phone = db.Column(db.String(20), nullable=False, comment='联系人电话')
    province = db.Column(db.String(50), comment='省份')
    city = db.Column(db.String(50), comment='城市')
    district = db.Column(db.String(50), comment='区县')
    address_detail = db.Column(db.String(255), nullable=False, comment='详细地址')
    latitude = db.Column(db.Numeric(10, 6), comment='纬度')
    longitude = db.Column(db.Numeric(10, 6), comment='经度')
    tag = db.Column(db.String(20), comment='地址标签: home, company, other')
    is_default = db.Column(db.SmallInteger, default=0, comment='是否默认: 0-否, 1-是')
    status = db.Column(db.SmallInteger, default=1, comment='状态: 0-删除, 1-正常')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'userId': self.user_id,
            'contactName': self.contact_name,
            'contactPhone': self.contact_phone,
            'province': self.province,
            'city': self.city,
            'district': self.district,
            'addressDetail': self.address_detail,
            'fullAddress': f'{self.province or ""}{self.city or ""}{self.district or ""}{self.address_detail or ""}',
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'tag': self.tag,
            'isDefault': self.is_default,
            'status': self.status,
            'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
