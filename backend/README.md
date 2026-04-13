# Smart Nursing Backend

智慧养老系统后端服务

## 技术栈

- Flask 2.3
- SQLAlchemy
- Redis
- JWT Authentication

## 安装

```bash
pip install -r requirements.txt
```

## 运行

```bash
python run.py
```

## API 端点

- 用户管理: `/api/users/*`
- 护理记录: `/api/nursing/*`
- 健康指标: `/api/health/*`
- 护理计划: `/api/care/*`
- 通知管理: `/api/notifications/*`
- 统计报表: `/api/statistics/*`