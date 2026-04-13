# -*- coding: utf-8 -*-
"""添加服务项目数据"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from app import create_app
from app.extensions import db
from app.models import Service

app = create_app('default')


def add_services():
    """添加服务项目"""
    services_data = [
        {
            'name': '日常照护服务',
            'category': '日常照护',
            'description': '提供老人日常生活的全面照护，包括饮食、洗漱、行动协助等',
            'price': 150.00,
            'unit': '次',
            'duration': 60,
            'details': '包括晨间护理（协助起床、洗漱、穿衣）、午间护理（协助用餐、如厕）、晚间护理（协助沐浴、更换衣物）',
            'precautions': '服务过程中注意老人安全，动作轻柔，注意保护隐私',
            'requirements': '服务人员需经过专业培训，持有护理证书',
            'icons': 'user-check'
        },
        {
            'name': '医疗护理服务',
            'category': '医疗护理',
            'description': '专业医疗护理，包括伤口处理、输液、用药指导等',
            'price': 200.00,
            'unit': '次',
            'duration': 45,
            'details': '包括生命体征监测（血压、血糖、体温等）、伤口护理、药物管理、协助就医等',
            'precautions': '需具备医疗护理资质，操作严格遵守医疗规范，发现异常及时报告',
            'requirements': '服务人员需持有护士执业证书，有丰富临床经验',
            'icons': 'medicine-box'
        },
        {
            'name': '康复训练服务',
            'category': '康复训练',
            'description': '根据老人身体状况制定康复计划，进行专业康复训练',
            'price': 180.00,
            'unit': '次',
            'duration': 40,
            'details': '包括肢体功能训练、语言康复训练、认知功能训练、日常生活能力训练等',
            'precautions': '训练强度根据老人身体状况调整，避免过度疲劳',
            'requirements': '服务人员需持有康复治疗师证书',
            'icons': 'activity'
        },
        {
            'name': '心理疏导服务',
            'category': '心理疏导',
            'description': '专业心理咨询师提供心理疏导服务',
            'price': 160.00,
            'unit': '次',
            'duration': 50,
            'details': '包括情绪疏导、心理慰藉、认知行为疗法、团体心理辅导等',
            'precautions': '尊重老人隐私，建立信任关系，发现严重心理问题及时转介专业机构',
            'requirements': '服务人员需持有心理咨询师证书',
            'icons': 'headset'
        },
        {
            'name': '营养配餐服务',
            'category': '饮食护理',
            'description': '根据老人健康状况制定营养食谱',
            'price': 120.00,
            'unit': '次',
            'duration': 30,
            'details': '包括营养评估、食谱制定、特殊饮食指导（糖尿病、高血压等）、膳食制作指导',
            'precautions': '注意食物过敏史，遵守医嘱饮食要求',
            'requirements': '服务人员需具备营养师资质',
            'icons': 'coffee'
        },
        {
            'name': '24小时紧急护理',
            'category': '医疗护理',
            'description': '全天候紧急护理服务',
            'price': 500.00,
            'unit': '天',
            'duration': 1440,
            'details': '提供24小时不间断护理服务，包括紧急情况处理、持续生命体征监测、紧急就医协助等',
            'precautions': '随时待命，响应迅速，遇到紧急情况立即启动急救流程',
            'requirements': '需配备专业医护团队，24小时在线',
            'icons': 'alert-circle'
        },
        {
            'name': '定期体检服务',
            'category': '医疗护理',
            'description': '定期健康体检和健康评估',
            'price': 300.00,
            'unit': '次',
            'duration': 60,
            'details': '包括全面体检（血常规、尿常规、心电图、B超等）、健康风险评估、建立健康档案',
            'precautions': '体检前需空腹，体检后提供详细报告解读',
            'requirements': '需与专业医疗机构合作',
            'icons': 'file-text'
        },
        {
            'name': '沐浴护理服务',
            'category': '日常照护',
            'description': '协助老人沐浴、清洁护理',
            'price': 80.00,
            'unit': '次',
            'duration': 30,
            'details': '包括协助沐浴、洗头、修剪指甲、皮肤护理等',
            'precautions': '注意水温适宜，地面防滑，保护老人隐私',
            'requirements': '服务人员需经过专业培训',
            'icons': 'droplet'
        },
        {
            'name': '睡眠照护服务',
            'category': '日常照护',
            'description': '改善老人睡眠质量的护理服务',
            'price': 100.00,
            'unit': '次',
            'duration': 45,
            'details': '包括睡眠评估、睡前护理（泡脚、按摩等）、睡眠环境调整、睡眠指导',
            'precautions': '避免影响老人正常作息',
            'requirements': '服务人员需了解睡眠护理知识',
            'icons': 'moon'
        },
        {
            'name': '特殊饮食照料',
            'category': '饮食护理',
            'description': '为有特殊饮食需求的老人提供定制化饮食服务',
            'price': 180.00,
            'unit': '天',
            'duration': 60,
            'details': '包括糖尿病饮食、低盐低脂饮食、流质/半流质饮食等定制化服务',
            'precautions': '严格遵守医嘱饮食要求',
            'requirements': '需由专业营养师指导',
            'icons': 'edit'
        }
    ]

    with app.app_context():
        for data in services_data:
            existing = Service.query.filter_by(name=data['name']).first()
            if not existing:
                service = Service(
                    name=data['name'],
                    category=data['category'],
                    description=data['description'],
                    price=data['price'],
                    unit=data['unit'],
                    duration=data['duration'],
                    details=data['details'],
                    precautions=data['precautions'],
                    requirements=data['requirements'],
                    icons=data['icons'],
                    status=1,
                    stock=999,
                    is_recommended=1 if data['name'] in ['日常照护服务', '医疗护理服务', '康复训练服务'] else 0,
                    sort_order=services_data.index(data)
                )
                db.session.add(service)
                print(f'已添加服务: {data["name"]} - ¥{data["price"]}/{data["unit"]}')
        
        db.session.commit()
        
        # 显示所有服务
        print('\n========== 当前服务列表 ==========')
        services = Service.query.order_by(Service.sort_order).all()
        for s in services:
            print(f'{s.id}. {s.name} [{s.category}] - ¥{s.price}/{s.unit}')
            print(f'   描述: {s.description}')
            print(f'   详情: {s.details}')
            print()


if __name__ == '__main__':
    add_services()