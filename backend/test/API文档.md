# 智能护理系统 API 文档

## 版本信息
- 版本: 1.0.0
- 生成日期: 2026-04-22

## 基础信息
- **基础URL**: `http://localhost:5000/api`
- **认证方式**: JWT Token（在请求头中添加 `Authorization: Bearer <token>`）
- **响应格式**: JSON

## 错误处理
| 错误码 | 描述 |
|---------|------|
| 400 | 请求参数错误 |
| 401 | 未授权，token无效或过期 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 1. 用户模块

> 用户管理相关API，包括注册、登录、个人资料管理等功能

### 1.1 /users/register (POST)

**描述**: 用户注册（老人或家属）

**是否被使用**: 是

**请求体**:
```json
{"phone": "string", "password": "string", "email": "string", "email_code": "string", "user_type": "number (1=老人, 4=家属)", "name": "string", "gender": "number (0=未知, 1=男, 2=女)", "age": "number", "id_card": "string", "relation_with_elder": "string (家属与老人的关系)"}
```

**响应**:
```json
{"code": "number", "message": "string", "data": {"token": "string", "user_id": "number", "user_type": "number"}}
```

### 1.2 /users/login (POST)

**描述**: 用户登录

**是否被使用**: 是

**请求体**:
```json
{"phone": "string", "password": "string"}
```

**响应**:
```json
{"code": "number", "message": "string", "data": {"token": "string", "user_id": "number", "user_type": "number", "name": "string", "phone": "string", "gender": "number"}}
```

### 1.3 /users/profile (GET)

**描述**: 获取用户资料

**是否被使用**: 是

**响应**:
```json
{"code": "number", "message": "string", "data": {"id": "number", "phone": "string", "email": "string", "name": "string", "gender": "number", "age": "number", "id_card": "string", "address": "string", "avatar": "string", "emergency_contact": "string", "emergency_phone": "string", "user_type": "number"}}
```

### 1.4 /users/profile (PUT)

**描述**: 更新用户资料

**是否被使用**: 是

**请求体**:
```json
{"name": "string", "gender": "number", "age": "number", "id_card": "string", "address": "string", "avatar": "string", "emergency_contact": "string", "emergency_phone": "string"}
```

**响应**:
```json
{"code": "number", "message": "string"}
```

### 1.5 /users/elder/list (GET)

**描述**: 获取老人列表

**是否被使用**: 是

**响应**:
```json
{"code": "number", "message": "string", "data": [{"id": "number", "name": "string", "gender": "number", "age": "number", "address": "string", "avatar": "string"}]}
```

### 1.6 /users/binding-elder (POST)

**描述**: 家属绑定老人

**是否被使用**: 是

**请求体**:
```json
{"elder_id": "number", "username": "string (老人账号，支持手机号或用户名)", "password": "string (老人密码)"}
```

**响应**:
```json
{"code": "number", "message": "string"}
```

### 1.7 /users/workers (GET)

**描述**: 获取护工列表

**是否被使用**: 是

**响应**:
```json
{"code": "number", "message": "string", "data": [{"id": "number", "name": "string", "gender": "number", "age": "number", "avatar": "string", "phone": "string"}]}
```

## 2. 订单模块

> 订单管理相关API，包括订单的创建、查询、更新和删除

### 2.1 /orders/summary (GET)

**描述**: 获取订单统计信息

**是否被使用**: 是

**响应**:
```json
{"code": "number", "message": "string", "data": {"total_orders": "number", "total_sales": "number", "completed_orders": "number", "pending_orders": "number"}}
```

### 2.2 /orders/ (GET)

**描述**: 获取订单列表

**是否被使用**: 是

**查询参数**:
| 参数名 | 类型 | 描述 |
|---------|------|---------|
| status | - | number (订单状态) |
| page | - | number (页码) |
| page_size | - | number (每页数量) |

**响应**:
```json
{"code": "number", "message": "string", "data": {"items": [{"id": "number", "order_no": "string", "service_name": "string", "elder_name": "string", "nurse_name": "string", "total_amount": "number", "appointment_date": "string", "appointment_time": "string", "status": "number", "status_name": "string", "created_at": "string"}], "total": "number"}}
```

### 2.3 /orders/ (POST)

**描述**: 创建订单

**是否被使用**: 是

**请求体**:
```json
{"elder_id": "number", "service_id": "number", "nurse_id": "number", "appointment_date": "string", "appointment_time": "string", "remark": "string"}
```

**响应**:
```json
{"code": "number", "message": "string", "data": {"order_id": "number", "order_no": "string"}}
```

### 2.4 /orders/<int:order_id> (PUT)

**描述**: 更新订单信息

**是否被使用**: 是

**请求体**:
```json
{"nurse_id": "number", "appointment_date": "string", "appointment_time": "string", "status": "number", "remark": "string"}
```

**响应**:
```json
{"code": "number", "message": "string"}
```

## 3. 护理记录模块

> 护理记录相关API，包括记录的创建、查询等

### 3.1 /nursing/records (GET)

**描述**: 获取护理记录列表

**是否被使用**: 是

**查询参数**:
| 参数名 | 类型 | 描述 |
|---------|------|---------|
| elder_id | - | number (老人ID) |
| page_size | - | number (每页数量) |

**响应**:
```json
{"code": "number", "message": "string", "data": {"items": [{"id": "number", "nursing_type_name": "string", "description": "string", "staff_name": "string", "created_at": "string"}]}}
```

### 3.2 /nursing/types (GET)

**描述**: 获取护理类型列表

**是否被使用**: 是

**响应**:
```json
{"code": "number", "message": "string", "data": [{"id": "number", "name": "string"}]}
```

## 4. 用药提醒模块

> 用药提醒相关API，包括提醒的创建、查询、标记等

### 4.1 /medication/reminders (GET)

**描述**: 获取用药提醒列表

**是否被使用**: 是

**响应**:
```json
{"code": "number", "message": "string", "data": [{"id": "number", "medication_name": "string", "time": "string", "dosage": "string", "days": "array", "notes": "string", "completed": "boolean"}]}
```

### 4.2 /medication/reminders (POST)

**描述**: 创建用药提醒

**是否被使用**: 是

**请求体**:
```json
{"user_id": "number (可选，管理员为老人创建时使用)", "medication_name": "string", "time": "string", "dosage": "string", "days": "array", "notes": "string"}
```

**响应**:
```json
{"code": "number", "message": "string", "data": {"id": "number", "medication_name": "string", "time": "string", "dosage": "string", "days": "array", "notes": "string", "completed": "boolean"}}
```

### 4.3 /medication/reminders/<int:reminder_id>/complete (PUT)

**描述**: 标记用药提醒为已完成

**是否被使用**: 是

**响应**:
```json
{"code": "number", "message": "string", "data": {"completed": "boolean"}}
```

## 5. 紧急呼叫模块

> 紧急呼叫相关API，包括发起呼叫、响应和完成

### 5.1 /emergency/call (POST)

**描述**: 发起紧急呼叫

**是否被使用**: 是

**请求体**:
```json
{"elder_id": "number", "type": "string (sos或其他类型)"}
```

**响应**:
```json
{"code": "number", "message": "string", "data": {"call_id": "number"}}
```

### 5.2 /emergency/calls (GET)

**描述**: 获取紧急呼叫列表

**是否被使用**: 是

**响应**:
```json
{"code": "number", "message": "string", "data": [{"id": "number", "elder_id": "number", "elder_name": "string", "type": "string", "location": "string", "status": "string", "assigned_worker_id": "number", "assigned_worker_name": "string", "response_time": "string", "completed_at": "string", "created_at": "string"}]}
```

## 6. 打卡模块

> 打卡相关API，包括执行打卡和查询打卡记录

### 6.1 /checkin/ (POST)

**描述**: 执行打卡

**是否被使用**: 是

**响应**:
```json
{"code": "number", "message": "string", "data": {"date": "string", "time": "string"}}
```

### 6.2 /checkin/history (GET)

**描述**: 获取打卡历史

**是否被使用**: 是

**响应**:
```json
{"code": "number", "message": "string", "data": [{"date": "string", "time": "string"}]}
```

### 6.3 /checkin/admin/history (GET)

**描述**: 获取所有用户的打卡历史

**是否被使用**: 是

**查询参数**:
| 参数名 | 类型 | 描述 |
|---------|------|---------|
| page | - | number (页码) |
| page_size | - | number (每页数量) |
| user_id | - | number (可选，用户ID) |

**响应**:
```json
{"code": "number", "message": "string", "data": {"list": [{"id": "number", "user_id": "number", "user_name": "string", "date": "string", "time": "string"}], "total": "number"}}
```

## 7. 通知模块

> 通知相关API，包括发送和获取通知

### 7.1 /notifications/ (GET)

**描述**: 获取通知列表

**是否被使用**: 是

**响应**:
```json
{"code": "number", "message": "string", "data": [{"id": "number", "title": "string", "content": "string", "is_read": "boolean", "created_at": "string"}]}
```

### 7.2 /notifications/unread-count (GET)

**描述**: 获取未读通知数量

**是否被使用**: 是

**响应**:
```json
{"code": "number", "message": "string", "data": {"count": "number"}}
```

### 7.3 /notifications/create (POST)

**描述**: 创建通知

**是否被使用**: 是

**请求体**:
```json
{"user_ids": "array", "title": "string", "content": "string", "notification_type": "number", "priority": "number"}
```

**响应**:
```json
{"code": "number", "message": "string"}
```

## 8. 评价模块

> 护工评价相关API，包括创建评价和获取评价

### 8.1 /evaluation/worker (POST)

**描述**: 创建护工评价

**是否被使用**: 是

**请求体**:
```json
{"elder_id": "number", "worker_id": "number", "overall_rating": "number", "professionalism_rating": "number", "attitude_rating": "number", "punctuality_rating": "number", "skill_rating": "number", "content": "string", "tags": "string (JSON字符串)", "is_anonymous": "number (0=否, 1=是)"}
```

**响应**:
```json
{"code": "number", "message": "string"}
```

### 8.2 /evaluation/worker (GET)

**描述**: 获取护工评价列表

**是否被使用**: 是

**查询参数**:
| 参数名 | 类型 | 描述 |
|---------|------|---------|
| worker_id | - | number (可选，护工ID) |
| page | - | number (页码) |
| page_size | - | number (每页数量) |

**响应**:
```json
{"code": "number", "message": "string", "data": {"items": [{"id": "number", "elder_name": "string", "worker_name": "string", "overall_rating": "number", "professionalism_rating": "number", "attitude_rating": "number", "punctuality_rating": "number", "content": "string", "tags": "string", "created_at": "string"}], "total": "number"}}
```

### 8.3 /evaluation/worker/stats/<int:worker_id> (GET)

**描述**: 获取护工评分统计

**是否被使用**: 是

**响应**:
```json
{"code": "number", "message": "string", "data": {"average_rating": "number", "total_count": "number", "dimension_avg": {"professionalism": "number", "attitude": "number", "punctuality": "number", "skill": "number"}, "rating_distribution": {"1": "number", "2": "number", "3": "number", "4": "number", "5": "number"}}}
```

## 9. 健康模块

> 健康数据相关API，包括获取老人健康数据

### 9.1 /health/metrics/latest/<int:elder_id> (GET)

**描述**: 获取老人最新健康数据

**是否被使用**: 是

**响应**:
```json
{"code": "number", "message": "string", "data": {"心率": {"value": "number", "unit": "string"}, "血压-收缩压": {"value": "number", "unit": "string"}, "血压-舒张压": {"value": "number", "unit": "string"}, "睡眠时长": {"value": "number", "unit": "string"}, "今日步数": {"value": "number", "unit": "string"}}}
```

## 10. AI模块

> AI相关API，包括AI聊天功能

### 10.1 /ai/chat (POST)

**描述**: AI聊天

**是否被使用**: 是

**请求体**:
```json
{"message": "string", "user_type": "number", "elder_id": "number (可选)"}
```

**响应**:
```json
{"code": "number", "message": "string", "data": {"response": "string"}}
```

## 11. 服务模块

> 服务相关API，包括获取服务列表

### 11.1 /service/ (GET)

**描述**: 获取服务列表

**是否被使用**: 是

**响应**:
```json
{"code": "number", "message": "string", "data": [{"id": "number", "name": "string", "price": "number", "description": "string", "duration": "number", "category": "string"}]}
```

## 12. 统计模块

> 统计相关API，包括获取仪表盘数据

### 12.1 /statistics/dashboard (GET)

**描述**: 获取仪表盘统计数据

**是否被使用**: 是

**响应**:
```json
{"code": "number", "message": "string", "data": {"elder_count": "number", "staff_count": "number", "family_count": "number", "today_orders": "number"}}
```

## 总结
- **已使用的API**：大部分核心功能的API都已被使用，包括用户登录注册、订单管理、护理记录、用药提醒、紧急呼叫、打卡、通知等。
- **未使用的API**：主要是一些高级功能或管理功能的API，如大数据分析、支付、AI健康检查、电子围栏等。
- **需要注意的API**：部分API虽然存在，但前端代码中没有直接调用，可能需要根据实际需求进行集成。