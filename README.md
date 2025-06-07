# 智能充电桩调度计费系统

## 项目概述
基于Python后端和Vue前端的智能充电桩调度计费系统，支持快充/慢充模式，智能调度，动态计费。

## 技术栈
- **后端**: Python + FastAPI
- **前端**: Vue.js 3 + Element Plus
- **数据库**: SQLite (开发环境) / PostgreSQL (生产环境)
- **实时通信**: WebSocket

## 项目结构
```
PHYcharging/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   ├── utils/          # 工具函数
│   │   └── core/           # 核心配置
│   ├── requirements.txt    # Python依赖
│   └── main.py            # 应用入口
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── components/     # Vue组件
│   │   ├── views/          # 页面视图
│   │   ├── router/         # 路由配置
│   │   ├── store/          # 状态管理
│   │   └── utils/          # 工具函数
│   ├── package.json       # 前端依赖
│   └── vite.config.js     # Vite配置
└── docs/                  # 文档
```

## 功能特性
- 用户注册登录
- 充电请求提交（快充/慢充）
- 智能调度算法
- 动态计费系统
- 实时状态监控
- 报表统计
- 充电桩故障处理

## 安装运行

### 后端
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### 前端
```bash
cd frontend
npm install
npm run dev
```

## 测试参数
- 快充电桩数: 2个
- 慢充电桩数: 3个
- 等候区容量: 可配置
- 排队队列长度: 可配置 