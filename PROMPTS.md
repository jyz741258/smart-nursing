# Smart Nursing AI 助手常用提示词

## 🚀 快速开始（首次对话）
```
请参考项目文档，这是一个智慧养老系统，技术栈是 uni-app + Flask。
帮我生成一个【具体功能】。
```

## 📱 前端开发
```
为老人端生成一个健康数据展示页面，包含：
- 血压、心率、血糖的卡片展示
- 最近7天的趋势图表（使用 u-charts）
- 使用 <script setup> 语法
- 从 /api/v1/health-records 获取数据
```

## 🔧 后端开发
```
生成 Flask Blueprint：
模块：用药提醒
端点：
- GET /api/v1/medication/elder/<id> 获取老人用药列表
- POST /api/v1/medication/remind 创建提醒
需要 JWT 认证和角色权限校验。
```

## 🐛 调试Bug
```
问题：老人列表页面数据不刷新
代码：pages/elders/List.vue
现象：添加老人后，列表没有更新
请分析可能原因并给出修复方案。
```

## 📊 数据库设计
```
设计老人健康记录表：
字段：id, elder_id, blood_pressure, heart_rate, blood_sugar, measured_at
关系：属于某个老人（外键）
索引：elder_id + measured_at 联合索引
```
