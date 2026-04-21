"""
批量插入测试用户数据
老人100个 + 护理人员100个 + 家属100个 = 300个用户
"""
import sys
import os
os.chdir('c:/Users/Jyz74/smart-nursing')
sys.path.insert(0, 'backend')

from app import create_app
from app.extensions import db
from app.models import User
from werkzeug.security import generate_password_hash
import random
from datetime import datetime

# 姓氏和名字库
surnames = ['Zhang', 'Wang', 'Li', 'Zhao', 'Liu', 'Chen', 'Yang', 'Huang', 'Zhou', 'Wu',
            'Xu', 'Sun', 'Ma', 'Zhu', 'Hu', 'Guo', 'Lin', 'He', 'Gao', 'Liang',
            'Zheng', 'Luo', 'Song', 'Xie', 'Tang', 'Han', 'Cao', 'Xu', 'Deng', 'Xiao']

elder_names_male = ['Wei', 'Qiang', 'Lei', 'Yang', 'Yong', 'Jun', 'Jie', 'Tao', 'Chao', 'Ming',
                    'Gang', 'Ping', 'Hui', 'Peng', 'Fei', 'Hua', 'Bo', 'Bin', 'Yu', 'Hao',
                    'Kai', 'Liang', 'Rui', 'Yi', 'Feng', 'Jian', 'Long', 'Zhi', 'Hai', 'Wen']

elder_names_female = ['Fang', 'Juan', 'Min', 'Jing', 'Li', 'Yan', 'Na', 'Xiu', 'Ying', 'Hua',
                     'Ping', 'Hong', 'Yu', 'Lan', 'Mei', 'Lan', 'Qin', 'Gui', 'Ying', 'Zhen',
                     'Xia', 'Xiu', 'Feng', 'Yun', 'Ling', 'Hua', 'Ting', 'Yan', 'Juan', 'Jie']

nurse_names = ['Nurse_Zhang', 'Nurse_Wang', 'Nurse_Li', 'Nurse_Liu', 'Nurse_Chen',
               'Nurse_Yang', 'Nurse_Huang', 'Nurse_Zhou', 'Nurse_Wu', 'Nurse_Xu',
               'Care_001', 'Care_002', 'Care_003', 'Care_004', 'Care_005',
               'Care_006', 'Care_007', 'Care_008', 'Care_009', 'Care_010']

family_titles = ['Son', 'Daughter', 'Wife', 'Husband', 'Grandson', 'Granddaughter']

# 随机电话号码生成器
def generate_phone(prefix='180'):
    return f"{prefix}{random.randint(10000000, 99999999)}"

def generate_id_card():
    """生成随机身份证号（仅用于测试）"""
    area = ['110101', '310101', '440103', '510104', '320105']
    birthday = f"{random.randint(1950, 2000)}{random.randint(1, 12):02d}{random.randint(1, 28):02d}"
    seq = f"{random.randint(100, 999)}"
    return f"{random.choice(area)}{birthday}{seq}X"

def create_test_users():
    app = create_app()
    with app.app_context():
        # 检查是否已有测试用户
        existing_count = User.query.filter(User.phone.like('180%')).count()
        if existing_count > 0:
            print(f"Found {existing_count} existing test users, deleting...")
            User.query.filter(User.phone.like('180%')).delete()
            db.session.commit()

        users_to_create = []
        base_phone = 18000000000

        print("=" * 60)
        print("Creating test users...")
        print("=" * 60)

        # 1. 创建老人用户 (100个)
        print("\n[1/3] Creating Elder Users (100)...")
        for i in range(100):
            gender = 1 if i % 2 == 0 else 2
            name_part = random.choice(elder_names_male) if gender == 1 else random.choice(elder_names_female)
            full_name = f"Elder_{i+1:03d}_{name_part}"

            user = User(
                username=f"elder_{i+1:03d}",
                real_name=full_name,
                phone=str(base_phone + i),
                password_hash=generate_password_hash('test123456'),
                user_type=1,  # 老人
                gender=gender,
                age=random.randint(65, 95),
                id_card=generate_id_card(),
                status=1
            )
            users_to_create.append(user)

        db.session.bulk_save_objects(users_to_create)
        db.session.commit()
        print(f"[OK] Elder users created (Phone: 18000000000 ~ 18000000099)")

        # 2. 创建护理人员 (100个)
        print("\n[2/3] Creating Nurse Users (100)...")
        users_to_create = []
        for i in range(100):
            gender = 1 if i % 3 != 0 else 2
            name = f"{random.choice(nurse_names)}_{i+1:03d}"

            user = User(
                username=f"nurse_{i+1:03d}",
                real_name=name,
                phone=str(base_phone + 100 + i),
                password_hash=generate_password_hash('test123456'),
                user_type=2,  # 护理人员
                gender=gender,
                age=random.randint(22, 50),
                id_card=generate_id_card(),
                status=1
            )
            users_to_create.append(user)

        db.session.bulk_save_objects(users_to_create)
        db.session.commit()
        print(f"[OK] Nurse users created (Phone: 18000000100 ~ 18000000199)")

        # 3. 创建家属用户 (100个)
        print("\n[3/3] Creating Family Users (100)...")
        users_to_create = []
        for i in range(100):
            gender = 1 if i % 2 == 0 else 2
            title = random.choice(family_titles)
            full_name = f"Family_{i+1:03d}_{title}"
            binding_elder_id = (i % 100) + 1

            user = User(
                username=f"family_{i+1:03d}",
                real_name=full_name,
                phone=str(base_phone + 200 + i),
                password_hash=generate_password_hash('test123456'),
                user_type=4,  # 家属
                gender=gender,
                age=random.randint(30, 65),
                id_card=generate_id_card(),
                binding_elder_id=binding_elder_id,
                relation_with_elder=title,
                status=1
            )
            users_to_create.append(user)

        db.session.bulk_save_objects(users_to_create)
        db.session.commit()
        print(f"[OK] Family users created (Phone: 18000000200 ~ 18000000299)")

        # 统计结果
        print("\n" + "=" * 60)
        print("Test Users Created Successfully!")
        print("=" * 60)

        # 重新查询统计
        total_users = User.query.count()
        elder_count = User.query.filter_by(user_type=1).count()
        nurse_count = User.query.filter_by(user_type=2).count()
        family_count = User.query.filter_by(user_type=4).count()

        print(f"\nDatabase User Statistics:")
        print(f"  Elder Users:   {elder_count}")
        print(f"  Nurse Users:   {nurse_count}")
        print(f"  Family Users:  {family_count}")
        print(f"  Admin Users:   {User.query.filter_by(user_type=3).count()}")
        print(f"  Total:         {total_users}")

        print(f"\nTest Account Info:")
        print(f"  Elder:   18000000000 ~ 18000000099")
        print(f"  Nurse:   18000000100 ~ 18000000199")
        print(f"  Family:  18000000200 ~ 18000000299")
        print(f"  Password: test123456")
        print("=" * 60)

if __name__ == '__main__':
    create_test_users()
