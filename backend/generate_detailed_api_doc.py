#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成详细的API文档（Markdown格式）
"""
import os
import sys

# 详细的API信息
API_DETAILS = {
    '用户模块': {
        'description': '用户管理相关API，包括注册、登录、个人资料管理等功能',
        'endpoints': [
            {
                'path': '/users/register',
                'method': 'POST',
                'description': '用户注册（老人或家属）',
                'params': [],
                'request_body': {
                    'phone': 'string',
                    'password': 'string',
                    'email': 'string',
                    'email_code': 'string',
                    'user_type': 'number (1=老人, 4=家属)',
                    'name': 'string',
                    'gender': 'number (0=未知, 1=男, 2=女)',
                    'age': 'number',
                    'id_card': 'string',
                    'relation_with_elder': 'string (家属与老人的关系)'
                },
                'response': {
                    'code': 'number',
                    'message': 'string',
                    'data': {
                        'token': 'string',
                        'user_id': 'number',
                        'user_type': 'number'
                    }
                },
                'used': True
            },
            {
                'path': '/users/login',
                'method': 'POST',
                'description': '用户登录',
                'params': [],
                'request_body': {
                    'phone': 'string',
                    'password': 'string'
                },
                'response': {
                    'code': 'number',
                    'message': 'string',
                    'data': {
                        'token': 'string',
                        'user_id': 'number',
                        'user_type': 'number',
                        'name': 'string',
                        'phone': 'string',
                        'gender': 'number'
                    }
                },
                'used': True
            },
            {
                'path': '/users/profile',
                'method': 'GET',
                'description': '获取用户资料',
                'params': [],
                'request_body': {},
                'response': {
                    'code': 'number',
                    'message': 'string',
                    'data': {
                        'id': 'number',
                        'phone': 'string',
                        'email': 'string',
                        'name': 'string',
                        'gender': 'number',
                        'age': 'number',
                        'id_card': 'string',
                        'address': 'string',
                        'avatar': 'string',
                        'emergency_contact': 'string',
                        'emergency_phone': 'string',
                        'user_type': 'number'
                    }
                },
                'used': True
            },
            {
                'path': '/users/profile',
                'method': 'PUT',
                'description': '更新用户资料',
                'params': [],
                'request_body': {
                    'name': 'string',
                    'gender': 'number',
                    'age': 'number',
                    'id_card': 'string',
                    'address': 'string',
                    'avatar': 'string',
                    'emergency_contact': 'string',
                    'emergency_phone': 'string'
                },
                'response': {
                    'code': 'number',
                    'message': 'string'
                },
                'used': True
            },
            {
                'path': '/users/elder/list',
                'method': 'GET',
                'description': '获取老人列表',
                'params': [],
                'request_body': {},
                'response': {
                    'code': 'number',
                    'message': 'string',
                    'data': [
                        {
                            'id': 'number',
                            'name': 'string',
                            'gender': 'number',
                            'age': 'number',
                            'address': 'string',
                            'avatar': 'string'
                        }
                    ]
                },
                'used': True
            },
            {
                'path': '/users/binding-elder',
                'method': 'POST',
                'description': '家属绑定老人',
                'params': [],
                'request_body': {
                    'elder_id': 'number',
                    'username': 'string (老人账号，支持手机号或用户名)',
                    'password': 'string (老人密码)'
                },
                'response': {
                    'code': 'number',
                    'message': 'string'
                },
                'used': True
            },
            {
                'path': '/users/workers',
                'method': 'GET',
                'description': '获取护工列表',
                'params': [],
                'request_body': {},
                'response': {
                    'code': 'number',
                    'message': 'string',
                    'data': [
                        {
                            'id': 'number',
                            'name': 'string',
                            'gender': 'number',
                            'age': 'number',
                            'avatar': 'string',
                            'phone': 'string'
                        }
                    ]
                },
                'used': True
            }
        ]
    },
    '订单模块': {
        'description': '订单管理相关API，包括订单的创建、查询、更新和删除',
        'endpoints': [
            {
                'path': '/orders/summary',
                'method': 'GET',
                'description': '获取订单统计信息',
                'params': [],
                'request_body': {},
                'response': {
                    'code': 'number',
                    'message': 'string',
                    'data': {
                        'total_orders': 'number',
                        'total_sales': 'number',
                        'completed_orders': 'number',
                        'pending_orders': 'number'
                    }
                },
                'used': True
            },
            {
                'path': '/orders/',
                'method': 'GET',
                'description': '获取订单列表',
                'params': [
                    'status: number (订单状态)',
                    'page: number (页码)',
                    'page_size: number (每页数量)'
                ],
                'request_body': {},
                'response': {
                    'code': 'number',
                    'message': 'string',
                    'data': {
                        'items': [
                            {
                                'id': 'number',
                                'order_no': 'string',
                                'service_name': 'string',
                                'elder_name': 'string',
                                'nurse_name': 'string',
                                'total_amount': 'number',
                                'appointment_date': 'string',
                                'appointment_time': 'string',
                                'status': 'number',
                                'status_name': 'string',
                                'created_at': 'string'
                            }
                        ],
                        'total': 'number'
                    }
                },
                'used': True
            },
            {
                'path': '/orders/',
                'method': 'POST',
                'description': '创建订单',
                'params': [],
                'request_body': {
                    'elder_id': 'number',
                    'service_id': 'number',
                    'nurse_id': 'number',
                    'appointment_date': 'string',
                    'appointment_time': 'string',
                    'remark': 'string'
                },
                'response': {
                    'code': 'number',
                    'message': 'string',
                    'data': {
                        'order_id': 'number',
                        'order_no': 'string'
                    }
                },
                'used': True
            },
            {
                'path': '/orders/<int:order_id>',
                'method': 'PUT',
                'description': '更新订单信息',
                'params': [],
                'request_body': {
                    'nurse_id': 'number',
                    'appointment_date': 'string',
                    'appointment_time': 'string',
                    'status': 'number',
                    'remark': 'string'
                },
                'response': {
                    'code': 'number',
                    'message': 'string'
                },
                'used': True
            }
        ]
    },
    '护理记录模块': {
        'description': '护理记录相关API，包括记录的创建、查询等',
        'endpoints': [
            {
                'path': '/nursing/records',
                'method': 'GET',
                'description': '获取护理记录列表',
                'params': [
                    'elder_id: number (老人ID)',
                    'page_size: number (每页数量)'
                ],
                'request_body': {},
                'response': {
                    'code': 'number',
                    'message': 'string',
                    'data': {
                        'items': [
                            {
                                'id': 'number',
                                'nursing_type_name': 'string',
                                'description': 'string',
                                'staff_name': 'string',
                                'created_at': 'string'
                            }
                        ]
                    }
                },
                'used': True
            },
            {
                'path': '/nursing/types',
                'method': 'GET',
                'description': '获取护理类型列表',
                'params': [],
                'request_body': {},
                'response': {
                    'code': 'number',
                    'message': 'string',
                    'data': [
                        {
                            'id': 'number',
                            'name': 'string'
                        }
                    ]
                },
                'used': True
            }
        ]
    },
    '用药提醒模块': {
        'description': '用药提醒相关API，包括提醒的创建、查询、标记等',
        'endpoints': [
            {
                'path': '/medication/reminders',
                'method': 'GET',
                'description': '获取用药提醒列表',
                'params': [],
                'request_body': {},
                'response': {
                    'code': 'number',
                    'message': 'string',
                    'data': [
                        {
                            'id': 'number',
                            'medication_name': 'string',
                            'time': 'string',
                            'dosage': 'string',
                            'days': 'array',
                            'notes': 'string',
                            'completed': 'boolean'
                        }
                    ]
                },
                'used': True
            },
            {
                'path': '/medication/reminders',
                'method': 'POST',
                'description': '创建用药提醒',
                'params': [],
                'request_body': {
                    'user_id': 'number (可选，管理员为老人创建时使用)',
                    'medication_name': 'string',
                    'time': 'string',
                    'dosage': 'string',
                    'days': 'array',
                    'notes': 'string'
                },
                'response': {
                    'code': 'number',
                    'message': 'string',
                    'data': {
                        'id': 'number',
                        'medication_name': 'string',
                        'time': 'string',
                        'dosage': 'string',
                        'days': 'array',
                        'notes': 'string',
                        'completed': 'boolean'
                    }
                },
                'used': True
            },
            {
                'path': '/medication/reminders/<int:reminder_id>/complete',
                'method': 'PUT',
                'description': '标记用药提醒为已完成',
                'params': [],
                'request_body': {},
                'response': {
                    'code': 'number',
                    'message': 'string',
                    'data': {
                        'completed': 'boolean'
                    }
                },
                'used': True
            }
        ]
    },
    '紧急呼叫模块': {
        'description': '紧急呼叫相关API，包括发起呼叫、响应和完成',
        'endpoints': [
            {
                'path': '/emergency/call',
                'method': 'POST',
                'description': '发起紧急呼叫',
                'params': [],
                'request_body': {
                    'elder_id': 'number',
                    'type': 'string (sos或其他类型)'
                },
                'response': {
                    'code': 'number',
                    'message': 'string',
                    'data': {
                        'call_id': 'number'
                    }
                },
                'used': True
            },
            {
                'path': '/emergency/calls',
                'method': 'GET',
                'description': '获取紧急呼叫列表',
                'params': [],
                'request_body': {},
                'response': {
                    'code': 'number',
                    'message': 'string',
                    'data': [
                        {
                            'id': 'number',
                            'elder_id': 'number',
                            'elder_name': 'string',
                            'type': 'string',
                            'location': 'string',
                            'status': 'string',
                            'assigned_worker_id': 'number',
                            'assigned_worker_name': 'string',
                            'response_time': 'string',
                            'completed_at': 'string',
                            'created_at': 'string'
                        }
                    ]
                },
                'used': True
            }
        ]
    },
    '打卡模块': {
        'description': '打卡相关API，包括执行打卡和查询打卡记录',
        'endpoints': [
            {
                'path': '/checkin/',
                'method': 'POST',
                'description': '执行打卡',
                'params': [],
                'request_body': {},
                'response': {
                    'code': 'number',
                    'message': 'string',
                    'data': {
                        'date': 'string',
                        'time': 'string'
                    }
                },
                'used': True
            },
            {
                'path': '/checkin/history',
                'method': 'GET',
                'description': '获取打卡历史',
                'params': [],
                'request_body': {},
                'response': {
                    'code': 'number',
                    'message': 'string',
                    'data': [
                        {
                            'date': 'string',
                            'time': 'string'
                        }
                    ]
                },
                'used': True
            },
            {
                'path': '/checkin/admin/history',
                'method': 'GET',
                'description': '获取所有用户的打卡历史',
                'params': [
                    'page: number (页码)',
                    'page_size: number (每页数量)',
                    'user_id: number (可选，用户ID)'
                ],
                'request_body': {},
                'response': {
                    'code': 'number',
                    'message': 'string',
                    'data': {
                        'list': [
                            {
                                'id': 'number',
                                'user_id': 'number',
                                'user_name': 'string',
                                'date': 'string',
                                'time': 'string'
                            }
                        ],
                        'total': 'number'
                    }
                },
                'used': True
            }
        ]
    },
    '通知模块': {
        'description': '通知相关API，包括发送和获取通知',
        'endpoints': [
            {
                'path': '/notifications/',
                'method': 'GET',
                'description': '获取通知列表',
                'params': [],
                'request_body': {},
                'response': {
                    'code': 'number',
                    'message': 'string',
                    'data': [
                        {
                            'id': 'number',
                            'title': 'string',
                            'content': 'string',
                            'is_read': 'boolean',
                            'created_at': 'string'
                        }
                    ]
                },
                'used': True
            },
            {
                'path': '/notifications/unread-count',
                'method': 'GET',
                'description': '获取未读通知数量',
                'params': [],
                'request_body': {},
                'response': {
                    'code': 'number',
                    'message': 'string',
                    'data': {
                        'count': 'number'
                    }
                },
                'used': True
            },
            {
                'path': '/notifications/create',
                'method': 'POST',
                'description': '创建通知',
                'params': [],
                'request_body': {
                    'user_ids': 'array',
                    'title': 'string',
                    'content': 'string',
                    'notification_type': 'number',
                    'priority': 'number'
                },
                'response': {
                    'code': 'number',
                    'message': 'string'
                },
                'used': True
            }
        ]
    },
    '评价模块': {
        'description': '护工评价相关API，包括创建评价和获取评价',
        'endpoints': [
            {
                'path': '/evaluation/worker',
                'method': 'POST',
                'description': '创建护工评价',
                'params': [],
                'request_body': {
                    'elder_id': 'number',
                    'worker_id': 'number',
                    'overall_rating': 'number',
                    'professionalism_rating': 'number',
                    'attitude_rating': 'number',
                    'punctuality_rating': 'number',
                    'skill_rating': 'number',
                    'content': 'string',
                    'tags': 'string (JSON字符串)',
                    'is_anonymous': 'number (0=否, 1=是)'
                },
                'response': {
                    'code': 'number',
                    'message': 'string'
                },
                'used': True
            },
            {
                'path': '/evaluation/worker',
                'method': 'GET',
                'description': '获取护工评价列表',
                'params': [
                    'worker_id: number (可选，护工ID)',
                    'page: number (页码)',
                    'page_size: number (每页数量)'
                ],
                'request_body': {},
                'response': {
                    'code': 'number',
                    'message': 'string',
                    'data': {
                        'items': [
                            {
                                'id': 'number',
                                'elder_name': 'string',
                                'worker_name': 'string',
                                'overall_rating': 'number',
                                'professionalism_rating': 'number',
                                'attitude_rating': 'number',
                                'punctuality_rating': 'number',
                                'content': 'string',
                                'tags': 'string',
                                'created_at': 'string'
                            }
                        ],
                        'total': 'number'
                    }
                },
                'used': True
            },
            {
                'path': '/evaluation/worker/stats/<int:worker_id>',
                'method': 'GET',
                'description': '获取护工评分统计',
                'params': [],
                'request_body': {},
                'response': {
                    'code': 'number',
                    'message': 'string',
                    'data': {
                        'average_rating': 'number',
                        'total_count': 'number',
                        'dimension_avg': {
                            'professionalism': 'number',
                            'attitude': 'number',
                            'punctuality': 'number',
                            'skill': 'number'
                        },
                        'rating_distribution': {
                            '1': 'number',
                            '2': 'number',
                            '3': 'number',
                            '4': 'number',
                            '5': 'number'
                        }
                    }
                },
                'used': True
            }
        ]
    },
    '健康模块': {
        'description': '健康数据相关API，包括获取老人健康数据',
        'endpoints': [
            {
                'path': '/health/metrics/latest/<int:elder_id>',
                'method': 'GET',
                'description': '获取老人最新健康数据',
                'params': [],
                'request_body': {},
                'response': {
                    'code': 'number',
                    'message': 'string',
                    'data': {
                        '心率': {
                            'value': 'number',
                            'unit': 'string'
                        },
                        '血压-收缩压': {
                            'value': 'number',
                            'unit': 'string'
                        },
                        '血压-舒张压': {
                            'value': 'number',
                            'unit': 'string'
                        },
                        '睡眠时长': {
                            'value': 'number',
                            'unit': 'string'
                        },
                        '今日步数': {
                            'value': 'number',
                            'unit': 'string'
                        }
                    }
                },
                'used': True
            }
        ]
    },
    'AI模块': {
        'description': 'AI相关API，包括AI聊天功能',
        'endpoints': [
            {
                'path': '/ai/chat',
                'method': 'POST',
                'description': 'AI聊天',
                'params': [],
                'request_body': {
                    'message': 'string',
                    'user_type': 'number',
                    'elder_id': 'number (可选)'
                },
                'response': {
                    'code': 'number',
                    'message': 'string',
                    'data': {
                        'response': 'string'
                    }
                },
                'used': True
            }
        ]
    },
    '服务模块': {
        'description': '服务相关API，包括获取服务列表',
        'endpoints': [
            {
                'path': '/service/',
                'method': 'GET',
                'description': '获取服务列表',
                'params': [],
                'request_body': {},
                'response': {
                    'code': 'number',
                    'message': 'string',
                    'data': [
                        {
                            'id': 'number',
                            'name': 'string',
                            'price': 'number',
                            'description': 'string',
                            'duration': 'number',
                            'category': 'string'
                        }
                    ]
                },
                'used': True
            }
        ]
    },
    '统计模块': {
        'description': '统计相关API，包括获取仪表盘数据',
        'endpoints': [
            {
                'path': '/statistics/dashboard',
                'method': 'GET',
                'description': '获取仪表盘统计数据',
                'params': [],
                'request_body': {},
                'response': {
                    'code': 'number',
                    'message': 'string',
                    'data': {
                        'elder_count': 'number',
                        'staff_count': 'number',
                        'family_count': 'number',
                        'today_orders': 'number'
                    }
                },
                'used': True
            }
        ]
    }
}

def generate_detailed_api_doc():
    """生成详细的API文档"""
    content = []
    
    # 添加标题
    content.append('# 智能护理系统 API 文档')
    content.append('')
    
    # 添加版本信息
    content.append('## 版本信息')
    content.append('- 版本: 1.0.0')
    content.append('- 生成日期: 2026-04-22')
    content.append('')
    
    # 添加基础信息
    content.append('## 基础信息')
    content.append('- **基础URL**: `http://localhost:5000/api`')
    content.append('- **认证方式**: JWT Token（在请求头中添加 `Authorization: Bearer <token>`）')
    content.append('- **响应格式**: JSON')
    content.append('')
    
    # 添加错误处理
    content.append('## 错误处理')
    content.append('| 错误码 | 描述 |')
    content.append('|---------|------|')
    content.append('| 400 | 请求参数错误 |')
    content.append('| 401 | 未授权，token无效或过期 |')
    content.append('| 403 | 权限不足 |')
    content.append('| 404 | 资源不存在 |')
    content.append('| 500 | 服务器内部错误 |')
    content.append('')
    
    # 遍历每个模块
    for module_index, module_name in enumerate(API_DETAILS, start=1):
        # 添加模块标题
        content.append(f'## {module_index}. {module_name}')
        content.append('')
        
        # 添加模块描述
        content.append(f'> {API_DETAILS[module_name]["description"]}')
        content.append('')
        
        # 遍历每个端点
        endpoints = API_DETAILS[module_name]['endpoints']
        for endpoint_index, endpoint in enumerate(endpoints, start=1):
            # 添加端点标题
            content.append(f'### {module_index}.{endpoint_index} {endpoint["path"]} ({endpoint["method"]})')
            content.append('')
            
            # 添加端点描述
            content.append(f'**描述**: {endpoint["description"]}')
            content.append('')
            
            # 添加是否被使用
            content.append(f'**是否被使用**: {"是" if endpoint["used"] else "否"}')
            content.append('')
            
            # 添加参数
            if endpoint['params']:
                content.append('**查询参数**:')
                content.append('| 参数名 | 类型 | 描述 |')
                content.append('|---------|------|---------|')
                for param in endpoint['params']:
                    param_parts = param.split(': ')
                    if len(param_parts) == 2:
                        param_name, param_desc = param_parts
                        content.append(f'| {param_name} | - | {param_desc} |')
                content.append('')
            
            # 添加请求体
            if endpoint['request_body']:
                content.append('**请求体**:')
                content.append('```json')
                content.append(str(endpoint['request_body']).replace("'", '"'))
                content.append('```')
                content.append('')
            
            # 添加响应
            content.append('**响应**:')
            content.append('```json')
            content.append(str(endpoint['response']).replace("'", '"'))
            content.append('```')
            content.append('')
    
    # 添加总结
    content.append('## 总结')
    content.append('- **已使用的API**：大部分核心功能的API都已被使用，包括用户登录注册、订单管理、护理记录、用药提醒、紧急呼叫、打卡、通知等。')
    content.append('- **未使用的API**：主要是一些高级功能或管理功能的API，如大数据分析、支付、AI健康检查、电子围栏等。')
    content.append('- **需要注意的API**：部分API虽然存在，但前端代码中没有直接调用，可能需要根据实际需求进行集成。')
    
    # 保存文档
    doc_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'detailed_api_document.md')
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
    
    print(f'详细API文档已生成：{doc_path}')

if __name__ == '__main__':
    generate_detailed_api_doc()
