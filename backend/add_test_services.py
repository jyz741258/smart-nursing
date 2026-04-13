from app import create_app
from app.extensions import db
from app.models import Service
from datetime import datetime

# 创建应用实例
app = create_app('default')

# 在应用上下文中添加测试数据
with app.app_context():
    # 添加测试服务数据
    services = [
        # 日常护理服务
        Service(
            name='日常照护',
            category='日常护理',
            description='为老人提供日常生活照料，包括协助穿衣、进食、洗漱等',
            price=80.00,
            unit='小时',
            duration=60,
            details='专业护理人员提供的日常照护服务，包括协助老人进行日常生活活动，如穿衣、进食、洗漱、如厕等，确保老人的基本生活需求得到满足。',
            precautions='服务过程中请确保老人的安全，避免发生意外。',
            requirements='护理人员需具备相关护理经验，有爱心和耐心。',
            status=1,
            is_recommended=1,
            sort_order=1
        ),
        # 医疗护理服务
        Service(
            name='医疗护理',
            category='医疗护理',
            description='为老人提供专业的医疗护理服务，包括测量血压、血糖、协助服药等',
            price=120.00,
            unit='小时',
            duration=60,
            details='由专业医护人员提供的医疗护理服务，包括测量血压、血糖、体温等生命体征，协助老人服药，进行伤口护理等医疗相关服务。',
            precautions='服务人员需具备相关医疗资质，严格按照医疗规范操作。',
            requirements='服务人员需持有相关医疗护理证书，有医疗护理经验。',
            status=1,
            is_recommended=1,
            sort_order=2
        ),
        # 康复训练服务
        Service(
            name='康复训练',
            category='康复护理',
            description='为老人提供专业的康复训练服务，帮助老人恢复身体功能',
            price=150.00,
            unit='小时',
            duration=60,
            details='由专业康复师提供的康复训练服务，根据老人的身体状况制定个性化的康复训练计划，帮助老人恢复身体功能，提高生活质量。',
            precautions='康复训练需根据老人的身体状况进行，避免过度训练造成伤害。',
            requirements='服务人员需持有康复治疗师资格证书，有康复训练经验。',
            status=1,
            is_recommended=1,
            sort_order=3
        ),
        # 心理疏导服务
        Service(
            name='心理疏导',
            category='心理护理',
            description='为老人提供心理疏导服务，帮助老人缓解孤独、焦虑等情绪',
            price=100.00,
            unit='小时',
            duration=60,
            details='由专业心理咨询师提供的心理疏导服务，通过聊天、陪伴等方式，帮助老人缓解孤独、焦虑、抑郁等情绪问题，提高老人的心理健康水平。',
            precautions='服务过程中需保护老人的隐私，尊重老人的感受。',
            requirements='服务人员需持有心理咨询师资格证书，有老年心理疏导经验。',
            status=1,
            is_recommended=1,
            sort_order=4
        ),
        # 营养膳食服务
        Service(
            name='营养膳食',
            category='饮食护理',
            description='为老人提供营养均衡的膳食服务，根据老人的身体状况制定个性化的饮食方案',
            price=60.00,
            unit='次',
            duration=30,
            details='由专业营养师根据老人的身体状况和营养需求，制定个性化的饮食方案，提供营养均衡的膳食服务，确保老人的营养需求得到满足。',
            precautions='需考虑老人的饮食禁忌和特殊需求，避免食物过敏等问题。',
            requirements='服务人员需持有营养师资格证书，有老年营养配餐经验。',
            status=1,
            is_recommended=1,
            sort_order=5
        ),
        # 清洁护理服务
        Service(
            name='清洁护理',
            category='日常护理',
            description='为老人提供居住环境的清洁服务，包括房间清洁、衣物清洗等',
            price=50.00,
            unit='次',
            duration=120,
            details='为老人提供居住环境的清洁服务，包括房间清洁、衣物清洗、床上用品更换等，确保老人的居住环境干净整洁。',
            precautions='清洁过程中需注意安全，避免滑倒等意外。',
            requirements='服务人员需具备清洁服务经验，有责任心。',
            status=1,
            is_recommended=0,
            sort_order=6
        ),
        # 安全监护服务
        Service(
            name='安全监护',
            category='安全护理',
            description='为老人提供24小时安全监护服务，确保老人的安全',
            price=200.00,
            unit='天',
            duration=1440,
            details='为老人提供24小时安全监护服务，包括夜间陪护、安全巡查等，确保老人的安全，防止意外发生。',
            precautions='监护过程中需保持警觉，及时发现并处理异常情况。',
            requirements='服务人员需具备安全监护经验，有应急处理能力。',
            status=1,
            is_recommended=0,
            sort_order=7
        ),
        # 陪同就医服务
        Service(
            name='陪同就医',
            category='医疗护理',
            description='陪同老人前往医院就诊，协助老人完成就医流程',
            price=150.00,
            unit='次',
            duration=240,
            details='陪同老人前往医院就诊，协助老人完成挂号、检查、取药等就医流程，确保老人顺利完成就医。',
            precautions='就医过程中需全程陪同，确保老人的安全。',
            requirements='服务人员需熟悉医院就医流程，有陪同就医经验。',
            status=1,
            is_recommended=0,
            sort_order=8
        )
    ]
    
    # 添加到数据库
    db.session.add_all(services)
    db.session.commit()
    
    print(f"成功添加了 {len(services)} 条测试服务数据！")
