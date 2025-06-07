# 智能充电桩调度计费系统 - 安装说明

## 环境要求

- **Python**: 3.8 或更高版本
- **Node.js**: 16.0 或更高版本
- **npm**: 8.0 或更高版本
- **操作系统**: Windows/Linux/macOS

## 📦 环境安装步骤

### 1. 安装 Python 环境

#### Windows
1. 从 [Python官网](https://www.python.org/downloads/) 下载 Python 3.8+
2. 安装时勾选 "Add Python to PATH"
3. 验证安装: `python --version`

#### Linux/macOS
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# CentOS/RHEL
sudo yum install python3 python3-pip

# macOS (使用 Homebrew)
brew install python
```

### 2. 安装 Node.js 环境

#### Windows
1. 从 [Node.js官网](https://nodejs.org/) 下载 LTS 版本
2. 运行安装程序
3. 验证安装: `node --version` 和 `npm --version`

#### Linux
```bash
# 使用 NodeSource 仓库 (推荐)
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# 或使用包管理器
sudo apt install nodejs npm
```

#### macOS
```bash
# 使用 Homebrew
brew install node npm
```

### 3. 创建Python虚拟环境 (推荐)

```bash
# 在项目根目录下创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

### 4. 安装项目依赖

#### 安装后端依赖
```bash
cd backend
pip install -r requirements.txt
```

#### 安装前端依赖
```bash
cd frontend
npm install
```

## 🚀 快速启动

### 方法一：使用启动脚本 (推荐)
```bash
python start.py
```

### 方法二：手动启动

#### 1. 初始化数据库
```bash
cd backend
python init_simple.py
```

#### 2. 启动后端服务
```bash
cd backend
python main.py
```

#### 3. 启动前端服务 (新终端)
```bash
cd frontend
npm run dev
```

## ⚙️ 系统配置

### 配置文件位置
- 主配置文件: `config.yaml`
- 环境变量: `backend/.env` (可选)

### 主要配置项

#### 充电桩配置
```yaml
charging_piles:
  fast_charging_pile_num: 2      # 快充桩数量
  trickle_charging_pile_num: 3   # 慢充桩数量
  fast_charging_power: 30.0      # 快充功率 (度/小时)
  trickle_charging_power: 10.0   # 慢充功率 (度/小时)
```

#### 队列和等候区配置
```yaml
queue_settings:
  waiting_area_size: 10          # 等候区车位容量
  charging_queue_len: 5          # 每个充电桩排队队列长度
  max_queue_wait_time: 120       # 最大排队等待时间(分钟)
```

#### 计费配置
```yaml
billing:
  prices:
    peak_time_price: 1.0         # 峰时电价 (元/度)
    normal_time_price: 0.7       # 平时电价 (元/度)
    valley_time_price: 0.4       # 谷时电价 (元/度)
    service_fee_price: 0.8       # 服务费单价 (元/度)
```

## 🔧 开发环境配置

### 代码编辑器配置

#### VS Code 推荐插件
- Python
- Pylance
- Vetur (Vue.js支持)
- YAML

#### PyCharm 配置
1. 打开项目目录
2. 配置Python解释器为虚拟环境
3. 安装Vue.js插件

### 数据库管理

#### SQLite 数据库文件
- 位置: `backend/charging_system.db`
- 推荐工具: DB Browser for SQLite

#### 重置数据库
```bash
# 删除数据库文件
rm backend/charging_system.db

# 重新初始化
cd backend
python init_simple.py
```

## 🐛 常见问题解决

### Python 相关问题

#### 1. pip 安装失败
```bash
# 升级 pip
python -m pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

#### 2. 虚拟环境问题
```bash
# 重新创建虚拟环境
rm -rf .venv
python -m venv .venv
```

### Node.js 相关问题

#### 1. npm 安装慢或失败
```bash
# 使用淘宝镜像
npm config set registry https://registry.npmmirror.com

# 或使用 cnpm
npm install -g cnpm --registry=https://registry.npmmirror.com
cnpm install
```

#### 2. 权限问题 (Linux/macOS)
```bash
# 全局安装时使用 sudo
sudo npm install -g <package>

# 或配置 npm 全局目录
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
export PATH=~/.npm-global/bin:$PATH
```

### 端口冲突问题

#### 后端端口 8000 被占用
```bash
# 查找占用进程
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows

# 修改后端端口 (backend/main.py)
uvicorn.run(app, host="0.0.0.0", port=8001)
```

#### 前端端口 3000 被占用
```bash
# 修改前端端口 (frontend/vite.config.js)
export default defineConfig({
  server: {
    port: 3001
  }
})
```

## 📚 系统架构

### 目录结构
```
PHYcharging/
├── backend/                 # 后端 (Python + FastAPI)
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   └── services/       # 业务逻辑
│   ├── main.py             # 应用入口
│   └── requirements.txt    # Python 依赖
├── frontend/               # 前端 (Vue.js 3)
│   ├── src/
│   │   ├── components/     # Vue 组件
│   │   ├── views/          # 页面视图
│   │   └── store/          # 状态管理
│   └── package.json        # Node.js 依赖
├── config.yaml             # 系统配置文件
├── start.py                # 一键启动脚本
└── INSTALL.md              # 安装说明
```

### 技术栈
- **后端**: Python 3.8+, FastAPI, SQLAlchemy, SQLite
- **前端**: Vue.js 3, Element Plus, Vite
- **认证**: JWT Token
- **文档**: Swagger UI (自动生成)

## 📞 技术支持

如果遇到问题，请按以下顺序尝试解决：

1. 检查本文档的常见问题部分
2. 确认环境要求是否满足
3. 查看控制台错误信息
4. 重新安装依赖包
5. 删除数据库文件重新初始化

---

💡 **提示**: 修改 `config.yaml` 配置文件后需要重启系统才能生效。 