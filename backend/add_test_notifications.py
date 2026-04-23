#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加测试通知数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.notification import Notification
from datetime import datetime, timedelta

# 创建Flask应用
app = create_app()

# 上下文管理器
def add_test_notifications():
    with app.app_context():
        # 查找王家人（家属用户）
        family_user = User.query.filter_by(phone='13900001004', user_type=4).first()
        if not family_user:
            print('未找到王家人用户')
            return
        
        # 查找管理员用户
        admin_user = User.query.filter_by(user_type=3).first()
        if not admin_user:
            print('未找到管理员用户')
            return
        
        # 查找护理员用户
        nurse_user = User.query.filter_by(user_type=2).first()
        if not nurse_user:
            print('未找到护理员用户')
            return
        
        # 查找老人用户
        elder_user = User.query.filter_by(user_type=1).first()
        if not elder_user:
            print('未找到老人用户')
            return
        
        # 通知类型
        notification_types = [
            (1, '系统通知'),
            (2, '任务通知'),
            (3, '健康提醒'),
            (4, '紧急通知'),
            (5, '订单通知')
        ]
        
        # 通知内容
        notifications_data = [
            # 系统通知
            {
                'title': '系统更新通知',
                'content': '智慧养老系统已更新至最新版本，新增了多项功能，包括健康数据分析、智能提醒等。',
                'notification_type': 1,
                'priority': 1,
                'created_by': admin_user.id
            },
            # 任务通知
            {
                'title': '新订单预约',
                'content': f'老人 {elder_user.name} 已预约护理服务，请及时处理。',
                'notification_type': 2,
                'priority': 2,
                'created_by': admin_user.id
            },
            # 健康提醒
            {
                'title': '健康检测提醒',
                'content': f'老人 {elder_user.name} 的健康数据异常，收缩压偏高，请关注。',
                'notification_type': 3,
                'priority': 1,
                'created_by': nurse_user.id
            },
            # 订单通知
            {
                'title': '订单状态更新',
                'content': '您为老人预约的护理服务已被护理员接收，预计明天开始服务。',
                'notification_type': 5,
                'priority': 1,
                'created_by': admin_user.id
            },
            # 系统通知
            {
                'title': '账户安全提醒',
                'content': '您的账户最近在新设备上登录，如非本人操作，请及时修改密码。',
                'notification_type': 1,
                'priority': 1,
                'created_by': admin_user.id
            },
            # 任务通知
            {
                'title': '护理计划更新',
                'content': f'老人 {elder_user.name} 的护理计划已更新，请查看详情。',
                'notification_type': 2,
                'priority': 1,
                'created_by': nurse_user.id
            },
            # 健康提醒
            {
                'title': '用药提醒',
                'content': f'老人 {elder_user.name} 今天需要服用降压药，请提醒老人按时服药。',
                'notification_type': 3,
                'priority': 1,
                'created_by': nurse_user.id
            },
            # 订单通知
            {
                'title': '服务完成通知',
                'content': '您为老人预约的护理服务已完成，护理员李护理已提交护理记录。',
                'notification_type': 5,
                'priority': 1,
                'created_by': admin_user.id
            }
        ]
        
        # 插入通知数据
        for i, data in enumerate(notifications_data):
            # 计算创建时间，使通知按时间顺序排列
            created_at = datetime.now() - timedelta(days=i)
            
            notification = Notification(
                user_id=family_user.id,
                title=data['title'],
                content=data['content'],
                notification_type=data['notification_type'],
                priority=data['priority'],
                created_by=data['created_by'],
                is_read=False,
                created_at=created_at
            )
            db.session.add(notification)
        
        # 提交事务
        db.session.commit()
        print(f'已为王家人添加 {len(notifications_data)} 条通知')

if __name__ == '__main__':
    add_test_notifications()
