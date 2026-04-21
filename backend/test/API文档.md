# Smart Nursing Platform - API接口文档

## 文档信息
- **项目名称**: 智慧养老护理平台 (Smart Nursing Platform)
- **基础路径**: `/api`
- **认证方式**: JWT Token (Bearer Token)
- **数据格式**: JSON
- **服务地址**: `http://localhost:5000`
- **前端代理**: `http://localhost:3000` (Vite开发服务器)

---

## 目录
1. [用户认证模块](#1-用户认证模块)
2. [用户管理模块](#2-用户管理模块)
3. [服务模块](#3-服务模块)
4. [订单模块](#4-订单模块)
5. [护理记录模块](#5-护理记录模块)
6. [健康指标模块](#6-健康指标模块)
7. [护理计划模块](#7-护理计划模块)
8. [通知模块](#8-通知模块)
9. [数据统计模块](#9-数据统计模块)
10. [护工评价模块](#10-护工评价模块)
11. [用户类型说明](#11-用户类型说明)

---

## 1. 用户认证模块

### 1.1 发送短信验证码
```
POST /api/users/send-sms
```

**请求参数**:
```json
{
  "phone": "13900001001"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "验证码已发送",
  "data": {
    "code": "123456"
  }
}
```

**注意**: 开发环境下验证码会直接返回在响应中。

### 1.2 用户注册
```
POST /api/users/register
```

**请求参数**:
```json
{
  "phone": "13900001001",
  "password": "123456",
  "sms_code": "123456",
  "user_type": 1,
  "name": "张三",
  "gender": "男",
  "age": 70
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "token": "eyJhbGci...",
    "user_id": 5,
    "user_type": 1
  }
}
```

**说明**: 管理员注册需要`admin_verify_code`（配置在`ADMIN_REGISTRATION_KEY`中）。

### 1.3 用户登录
```
POST /api/users/login
```

**请求参数**:
```json
{
  "phone": "13900001001",
  "password": "123456"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGci...",
    "user_id": 5,
    "user_type": 1,
    "name": "张三"
  }
}
```

### 1.4 获取用户资料
```
GET /api/users/profile
```
**Headers**: `Authorization: Bearer {token}`

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "id": 5,
    "phone": "13900001001",
    "name": "张三",
    "gender": "男",
    "age": 70,
    "id_card": "110101199001011234",
    "address": "北京市朝阳区",
    "avatar": null,
    "emergency_contact": "李四",
    "emergency_phone": "13900001002",
    "user_type": 1
  }
}
```

### 1.5 更新用户资料
```
PUT /api/users/profile
```

**请求参数** (部分字段):
```json
{
  "name": "张三",
  "age": 71,
  "address": "北京市海淀区"
}
```

### 1.6 修改密码
```
POST /api/users/change-password
```

**请求参数**:
```json
{
  "old_password": "123456",
  "new_password": "654321"
}
```

---

## 2. 用户管理模块

### 2.1 获取老人列表
```
GET /api/users/elder/list
```
**权限**: 需要登录

**响应示例**:
```json
{
  "code": 200,
  "data": [
    {
      "id": 5,
      "name": "张三",
      "gender": "男",
      "age": 70,
      "address": "北京市朝阳区",
      "avatar": null
    }
  ]
}
```

### 2.2 获取护工列表
```
GET /api/users/workers
```
**权限**: 需要登录

### 2.3 家属绑定老人
```
POST /api/users/binding-elder
```
**权限**: 仅家属 (user_type=4)

**请求参数**:
```json
{
  "elder_id": 5
}
```

### 2.4 家属解绑老人
```
DELETE /api/users/binding-elder
```
**权限**: 仅家属

### 2.5 获取家属绑定的老人信息
```
GET /api/users/binding-elder
```
**权限**: 仅家属

---

## 3. 服务模块

### 3.1 获取服务列表
```
GET /api/services/
```
**权限**: 需要登录

**查询参数**:
- `page` (int, 默认1): 页码
- `page_size` (int, 默认10): 每页数量
- `category` (string): 服务类别筛选

**响应示例** (普通用户):
```json
{
  "code": 200,
  "data": {
    "items": [
      {
        "id": 1,
        "name": "日常照护服务",
        "category": "日常照护",
        "description": "提供日常生活照料服务",
        "price": 150.00,
        "unit": "次",
        "duration": 60,
        "imageUrl": null,
        "icons": null,
        "details": "详细说明...",
        "precautions": "注意事项...",
        "requirements": "服务要求...",
        "stock": 999,
        "salesCount": 100,
        "rating": 5.00,
        "evaluationCount": 50,
        "status": 1,
        "isRecommended": 1,
        "sortOrder": 0,
        "createdAt": "2026-01-01 10:00:00"
      }
    ],
    "total": 10,
    "page": 1,
    "page_size": 10,
    "total_pages": 1
  }
}
```

**响应示例** (护理人员 - user_type=2):
护理人员看不到`price`字段，但能看到`requirements`字段。

### 3.2 获取服务详情
```
GET /api/services/{service_id}
```
**权限**: 需要登录

### 3.3 获取服务类别
```
GET /api/services/categories
```
**权限**: 公开接口（不需要登录）

**响应示例**:
```json
{
  "code": 200,
  "data": ["日常照护", "医疗护理", "康复训练"]
}
```

### 3.4 创建服务
```
POST /api/services/
```
**权限**: 仅管理员 (user_type=3)

### 3.5 更新服务
```
PUT /api/services/{service_id}
```
**权限**: 仅管理员

### 3.6 删除服务
```
DELETE /api/services/{service_id}
```
**权限**: 仅管理员

---

## 4. 订单模块

### 4.1 获取订单列表
```
GET /api/orders/
```
**权限**: 需要登录

**查询参数**:
- `page`, `page_size`: 分页
- `status` (int): 订单状态 (0-已取消, 1-待支付, 2-待服务, 3-服务中, 4-已完成, 5-已退款)
- `elder_id` (int): 老人ID
- `service_id` (int): 服务ID
- `start_date`, `end_date` (string): 日期范围

**权限说明**:
- 管理员: 查看所有订单
- 老人: 只能查看自己的订单
- 护理员: 只能查看自己的订单
- 家属: 只能查看绑定老人的订单

### 4.2 获取订单详情
```
GET /api/orders/{order_id}
```

### 4.3 创建订单
```
POST /api/orders/
```

**请求参数**:
```json
{
  "service_id": 1,
  "elder_id": 5,
  "service_time": "2026-01-01T14:00:00",
  "notes": "请准时到达",
  "appointment_date": "2026-01-01",
  "appointment_time": "14:00:00"
}
```

**说明**:
- 老人下单可自动关联自己为elder_id
- 家属下单需要指定elder_id

### 4.4 更新订单
```
PUT /api/orders/{order_id}
```
可更新字段: status, nurse_id, notes, appointment_date, appointment_time, remark

### 4.5 删除订单
```
DELETE /api/orders/{order_id}
```
**权限**: 仅管理员

---

## 5. 护理记录模块

### 5.1 获取护理记录列表
```
GET /api/nursing/records
```
**权限**: 需要登录

**查询参数**:
- `page`, `page_size`: 分页
- `elder_id` (int): 按老人筛选
- `nursing_type` (int): 护理类型

### 5.2 获取护理记录详情
```
GET /api/nursing/records/{record_id}
```

### 5.3 创建护理记录
```
POST /api/nursing/records
```
**权限**: 护理人员和管理员

**请求参数**:
```json
{
  "elder_id": 5,
  "nursing_type": 1,
  "description": "日常体温测量",
  "start_time": "2026-01-01T09:00:00",
  "end_time": "2026-01-01T09:30:00"
}
```

### 5.4 更新护理记录
```
PUT /api/nursing/records/{record_id}
```

### 5.5 完成护理记录
```
POST /api/nursing/records/{record_id}/complete
```
将记录状态设置为"已完成"

### 5.6 获取护理类型列表
```
GET /api/nursing/types
```

**响应示例**:
```json
{
  "code": 200,
  "data": [
    {"value": 1, "label": "日常照护"},
    {"value": 2, "label": "医疗护理"},
    {"value": 3, "label": "康复训练"},
    {"value": 4, "label": "心理疏导"},
    {"value": 5, "label": "饮食护理"},
    {"value": 6, "label": "清洁护理"},
    {"value": 7, "label": "安全护理"}
  ]
}
```

---

## 6. 健康指标模块

### 6.1 获取健康指标列表
```
GET /api/health/metrics
```

**查询参数**:
- `page`, `page_size`: 分页
- `elder_id` (int): 老人ID
- `metric_type` (int): 指标类型
- `start_date`, `end_date` (string): 日期范围

### 6.2 获取健康指标详情
```
GET /api/health/metrics/{metric_id}
```

### 6.3 创建健康指标
```
POST /api/health/metrics
```

**请求参数**:
```json
{
  "elder_id": 5,
  "metric_type": 1,
  "metric_value": 36.5,
  "unit": "℃",
  "notes": "正常",
  "recorded_at": "2026-01-01T08:00:00"
}
```

### 6.4 获取老人最新健康指标
```
GET /api/health/metrics/latest/{elder_id}
```

### 6.5 获取健康指标历史
```
GET /api/health/metrics/history/{elder_id}/{metric_type}
```
**查询参数**: `days` (int, 默认7): 查询天数

### 6.6 获取指标类型列表
```
GET /api/health/metrics/types
```

**指标类型**:
| value | label | unit |
|-------|-------|------|
| 1 | 体温 | ℃ |
| 2 | 血压-收缩压 | mmHg |
| 3 | 血压-舒张压 | mmHg |
| 4 | 心率 | 次/分 |
| 5 | 血氧 | % |
| 6 | 血糖 | mmol/L |
| 7 | 体重 | kg |
| 8 | 身高 | cm |
| 9 | 睡眠时长 | h |
| 10 | 今日步数 | 步 |

---

## 7. 护理计划模块

### 7.1 获取护理计划列表
```
GET /api/care/plans
```

**查询参数**:
- `page`, `page_size`: 分页
- `elder_id` (int): 老人ID
- `status` (int): 计划状态

### 7.2 获取护理计划详情
```
GET /api/care/plans/{plan_id}
```
包含关联的任务列表

### 7.3 创建护理计划
```
POST /api/care/plans
```

**请求参数**:
```json
{
  "elder_id": 5,
  "title": "糖尿病护理计划",
  "description": "控制血糖，定期监测",
  "start_date": "2026-01-01",
  "end_date": "2026-12-31"
}
```

### 7.4 更新护理计划
```
PUT /api/care/plans/{plan_id}
```

### 7.5 创建护理任务
```
POST /api/care/tasks
```

**请求参数**:
```json
{
  "care_plan_id": 1,
  "task_name": "测量血糖",
  "task_type": 1,
  "description": "每日空腹测量血糖",
  "frequency": "daily",
  "scheduled_time": "2026-01-01T07:00:00"
}
```

### 7.6 为护理计划添加任务
```
POST /api/care/plans/{plan_id}/tasks
```

### 7.7 完成任务
```
POST /api/care/tasks/{task_id}/complete
```

### 7.8 获取今日任务
```
GET /api/care/tasks/today
```

---

## 8. 通知模块

### 8.1 获取通知列表
```
GET /api/notifications/
```
**权限说明**:
- 管理员: 查看所有通知
- 其他用户: 仅查看自己的通知

**查询参数**:
- `page`, `page_size`: 分页
- `is_read` (boolean): 是否已读

### 8.2 标记通知已读
```
POST /api/notifications/{notification_id}/read
```

### 8.3 标记所有通知已读
```
POST /api/notifications/read-all
```

### 8.4 获取未读通知数量
```
GET /api/notifications/unread-count
```

### 8.5 创建通知
```
POST /api/notifications/
```
**权限**: 管理员

**请求参数**:
```json
{
  "user_id": 5,
  "title": "系统通知",
  "content": "请及时完成护理任务",
  "notification_type": 2,
  "priority": 1
}
```

### 8.6 广播通知
```
POST /api/notifications/broadcast
```
**权限**: 管理员

**请求参数**:
```json
{
  "user_ids": [5, 6, 7],
  "title": "紧急通知",
  "content": "系统将于今晚维护",
  "notification_type": 5,
  "priority": 2
}
```

### 8.7 获取通知类型列表
```
GET /api/notifications/types
```

---

## 9. 数据统计模块

### 9.1 仪表盘统计
```
GET /api/statistics/dashboard
```

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "today_nursing_count": 15,
    "today_completed_tasks": 12,
    "elder_count": 50,
    "staff_count": 10,
    "family_count": 30,
    "today_orders": 8,
    "pending_tasks": 5
  }
}
```

### 9.2 护理统计摘要
```
GET /api/statistics/nursing-summary?days=7
```
按护理类型统计最近N天的护理记录数

### 9.3 健康指标趋势
```
GET /api/statistics/health-trend?elder_id=5&days=30
```

### 9.4 护理人员工作量统计
```
GET /api/statistics/workload?days=7
```

### 9.5 健康预警统计
```
GET /api/statistics/alerts?days=7
```
返回notes中包含"异常"的健康指标记录

### 9.6 护理计划执行进度
```
GET /api/statistics/care-plan-progress
```

---

## 10. 护工评价模块

### 10.1 获取护工评价列表
```
GET /api/evaluations/worker?worker_id=1&elder_id=5
```

**查询参数**:
- `worker_id` (int): 护工ID
- `elder_id` (int): 老人ID
- `order_id` (int): 订单ID

**权限**:
- 管理员: 查看所有评价
- 老人: 仅查看自己的评价
- 家属: 仅查看绑定老人的评价

### 10.2 获取护工评价详情
```
GET /api/evaluations/worker/{evaluation_id}
```

### 10.3 提交护工评价
```
POST /api/evaluations/worker
```

**请求参数**:
```json
{
  "elder_id": 5,
  "worker_id": 2,
  "order_id": 1,
  "overall_rating": 5,
  "professionalism_rating": 5,
  "attitude_rating": 4,
  "punctuality_rating": 5,
  "skill_rating": 5,
  "content": "服务非常专业，态度很好",
  "tags": ["专业", "守时"],
  "is_anonymous": 0
}
```

### 10.4 护工回复评价
```
POST /api/evaluations/worker/{evaluation_id}/reply
```
**权限**: 仅管理员和该护工本人

### 10.5 获取护工评价统计
```
GET /api/evaluations/worker/stats/{worker_id}
```

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "total_count": 20,
    "average_rating": 4.8,
    "dimension_avg": {
      "professionalism": 4.9,
      "attitude": 4.8,
      "punctuality": 4.7,
      "skill": 4.9
    },
    "rating_distribution": {
      "1": 0,
      "2": 0,
      "3": 1,
      "4": 5,
      "5": 14
    }
  }
}
```

---

## 11. 用户类型说明

| user_type | 角色 | 描述 |
|-----------|------|------|
| 1 | 老人 | 可以查看服务、下单、查看自己的护理记录和健康指标 |
| 2 | 护理员 | 可以查看服务要求、接受订单、创建护理记录 |
| 3 | 管理员 | 拥有所有权限，包括服务管理、用户管理、订单管理等 |
| 4 | 家属 | 可以绑定老人、为老人下单、查看老人的相关信息 |

---

## 通用响应格式

### 成功响应
```json
{
  "code": 200,
  "message": "操作成功",
  "data": { ... }
}
```

### 错误响应
```json
{
  "code": 400,
  "message": "错误信息",
  "errors": { ... }  // 可选，详细错误信息
}
```

### 分页响应格式
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "items": [ ... ],
    "total": 100,
    "page": 1,
    "page_size": 10,
    "total_pages": 10
  }
}
```

---

## 错误码说明

| code | 说明 |
|------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未登录或token失效 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 注意事项

1. **URL路径问题**: 所有API路径都以 `/api/` 开头，且**Flask路由需要带尾部斜杠**（如 `/api/services/` 而不是 `/api/services`）

2. **认证方式**: 所有需要认证的接口需要在请求头中添加:
   ```
   Authorization: Bearer {token}
   ```

3. **时间格式**: 日期时间字段使用ISO 8601格式，如 `"2026-01-01T14:00:00"`

4. **数据权限**: 非管理员用户只能访问自己相关或自己角色的数据

5. **服务状态**: 服务有`status`字段控制上架/下架 (1=上架, 0=下架)

6. **开发环境**: Redis未连接时，短信验证码会直接打印在控制台，且验证会自动通过

---

## 样例测试账号

| 角色 | 手机号 | 密码 | user_type |
|------|--------|------|-----------|
| 老人 | 13900001001 | 123456 | 1 |
| 护理员 | 13900001002 | 123456 | 2 |
| 管理员 | 13800138000 | 123456 | 3 |
| 家属 | 13900001004 | 123456 | 4 |
