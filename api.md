# 智能养老系统 API 文档

## 基础信息

- **基础URL**: `http://localhost:5000/api`
- **认证方式**: JWT Token (Bearer Token)
- **Content-Type**: `application/json`

---

## 支付相关接口

### 1. 获取支付配置

获取当前启用的支付方式配置。

**请求**

```
GET /api/payment/config
Authorization: Bearer <token>
```

**响应**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "alipay_enabled": true,
    "wechat_enabled": false,
    "sandbox_mode": true
  }
}
```

---

### 2. 创建支付订单

为已有订单创建支付记录。

**请求**

```
POST /api/payment/create
Authorization: Bearer <token>
Content-Type: application/json

{
  "order_id": 1,
  "platform": "alipay"    // alipay | wechat
}
```

**响应 (支付宝)**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "payment_data": {
      "payment_url": "https://openapi.alipay.com/gateway.do?..."
    }
  }
}
```

**响应 (微信支付)**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "payment_data": {
      "prepayid": "wx20170228xxxxx",
      "appid": "wx1234567890",
      "partnerid": "1234567890",
      "package": "Sign=WXPay",
      "noncestr": "xxxxx",
      "timestamp": "1234567890",
      "sign": "xxxxx"
    }
  }
}
```

---

### 3. 查询支付状态

查询订单的支付状态。

**请求**

```
GET /api/payment/query/<order_no>?platform=alipay
Authorization: Bearer <token>
```

**响应**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "order_status": 2,           // 0-已取消 1-待支付 2-已支付
    "payment_status": "paid",
    "payment_time": "2024-01-01 12:00:00"
  }
}
```

---

### 4. 支付回调通知

接收支付宝/微信的异步回调通知。

**支付宝回调**

```
POST /api/payment/notify
Content-Type: application/x-www-form-urlencoded

// 支付宝异步通知参数
```

**微信支付回调**

```
POST /api/payment/notify
Content-Type: application/json

// 微信异步通知参数
```

---

### 5. 申请退款

对已支付的订单申请退款。

**请求**

```
POST /api/payment/refund
Authorization: Bearer <token>
Content-Type: application/json

{
  "order_no": "ORD20240101120000",
  "platform": "alipay",
  "refund_amount": 100.00,
  "refund_reason": "用户申请退款"
}
```

**响应**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "refund_status": "success",
    "refund_no": "REF20240101120000"
  }
}
```

---

### 6. 取消未支付订单

取消待支付的订单。

**请求**

```
POST /api/payment/cancel/<order_id>
Authorization: Bearer <token>
```

**响应**

```json
{
  "code": 200,
  "message": "订单已取消"
}
```

---

## 订单相关接口

### 1. 创建订单

**请求**

```
POST /api/orders/
Authorization: Bearer <token>
Content-Type: application/json

{
  "service_id": 1,
  "service_time": "2024-01-15 10:00:00",
  "notes": "需要携带血压计"
}
```

**响应**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "order_no": "ORD2024011500001",
    "actual_amount": 150.00,
    "status": 1
  }
}
```

---

### 2. 获取订单列表

**请求**

```
GET /api/orders/?page=1&page_size=10
Authorization: Bearer <token>
```

---

## 服务相关接口

### 1. 获取服务列表

```
GET /api/services/?page=1&page_size=10&category=护理服务
```

### 2. 获取服务类别

```
GET /api/services/categories
```

---

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权/Token无效 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 支付状态说明

| 订单状态 | 说明 |
|----------|------|
| 0 | 已取消 |
| 1 | 待支付 |
| 2 | 已支付/待服务 |
| 3 | 服务中 |
| 4 | 已完成 |
| 5 | 已退款 |
