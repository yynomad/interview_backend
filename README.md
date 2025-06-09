# 面试助手后端服务

一个基于 Flask 和 Google Gemini API 的智能面试助手后端服务，提供实时的面试问题回答建议。

## ✨ 功能特性

- **🤖 智能回答生成**: 基于 Google Gemini AI 模型生成专业的面试回答建议
- **⚡ 实时通信**: 支持 WebSocket 实时推送对话更新
- **📚 对话历史**: 自动保存和管理对话记录
- **🔍 健康检查**: 提供服务状态监控接口
- **🌐 跨域支持**: 完整的 CORS 配置
- **⚙️ 智能配置**: 自动配置管理和验证

## 📋 系统要求

- Python 3.8+
- Google Gemini API Key
- 网络连接（访问 Google AI 服务）

## 🚀 快速开始

### 第一步：配置环境

```bash
# 1. 克隆项目
git clone <repository-url>
cd interview-backend

# 2. 复制配置文件
cp .env.example .env

# 3. 编辑配置文件
# 使用你喜欢的编辑器打开 .env 文件
nano .env  # 或 vim .env 或 code .env

# 4. 配置必要信息
# - 设置 GEMINI_API_KEY（必须）
# - 设置 SECRET_KEY（推荐）
```

### 第二步：获取 Gemini API Key

1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 登录你的 Google 账户
3. 创建新的 API Key
4. 复制 API Key 到 .env 文件的 `GEMINI_API_KEY` 配置项

### 第三步：生成安全密钥（推荐）

```bash
# 生成安全密钥
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 或使用配置管理器
python config_manager.py generate-key

# 将生成的密钥复制到 .env 文件的 SECRET_KEY 配置项
```

### 第四步：启动服务

```bash
# 方式一：使用启动脚本（推荐）
./start.sh

# 方式二：手动启动
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
python app.py
```

服务将在 `http://localhost:5001` 启动

## ⚙️ 配置说明

### 配置文件结构

`.env` 文件包含以下主要配置项：

```bash
# 必须配置
GEMINI_API_KEY=your_gemini_api_key_here  # Gemini API 密钥
SECRET_KEY=your_secret_key_here          # Flask 安全密钥

# 可选配置
GEMINI_MODEL=gemini-1.5-flash           # AI 模型
DEBUG=True                              # 调试模式
FLASK_ENV=development                   # 运行环境
HOST=0.0.0.0                           # 监听地址
PORT=5001                              # 监听端口
CORS_ORIGINS=*                         # 跨域设置
LOG_LEVEL=INFO                         # 日志级别
```

### 配置验证和管理

```bash
# 验证配置
python config_manager.py validate

# 查看配置摘要
python config_manager.py summary

# 生成安全密钥
python config_manager.py generate-key

# 重新加载配置（无需重启服务）
python config_manager.py reload
```

### 动态配置重载 🔄

现在支持在不重启服务的情况下重新加载配置：

```bash
# 方式一：使用配置管理器
python config_manager.py reload

# 方式二：通过API（服务运行时）
curl -X POST http://localhost:5001/api/reload-config

# 方式三：使用测试脚本
python test_config_reload.py
```

**使用场景：**
- 修改 .env 文件后立即生效
- 切换不同的 API Key 进行测试
- 调整日志级别或其他配置
- 开发过程中快速调试配置

### 环境配置

#### 开发环境（默认）
```bash
FLASK_ENV=development
DEBUG=True
CORS_ORIGINS=*
RATE_LIMIT_ENABLED=False
```

#### 生产环境
```bash
FLASK_ENV=production
DEBUG=False
CORS_ORIGINS=https://yourdomain.com
RATE_LIMIT_ENABLED=True
SECRET_KEY=<强密码>
```

## 🔧 服务管理

### 启动脚本命令

```bash
./start.sh          # 启动服务（默认）
./start.sh start    # 启动服务
./start.sh stop     # 停止服务
./start.sh restart  # 重启服务
./start.sh health   # 健康检查
./start.sh help     # 显示帮助
```

### 配置管理

```bash
# 验证配置
python config_manager.py validate

# 查看配置摘要
python config_manager.py summary

# 生成安全密钥
python config_manager.py generate-key

# 重新加载配置
python config_manager.py reload
```

## 📡 API 接口

### REST API

#### 健康检查
```http
GET /health
```

响应：
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "gemini_available": true,
  "config": {
    "environment": "development",
    "debug": true,
    "port": 5001,
    "api_key_configured": true
  }
}
```

#### 提交问题
```http
POST /api/question
Content-Type: application/json

{
  "question": "请介绍一下你自己",
  "generate_answer": true
}
```

响应：
```json
{
  "success": true,
  "conversation": {
    "id": 1,
    "question": "请介绍一下你自己",
    "answer": "AI生成的回答建议...",
    "timestamp": "2024-01-01T12:00:00",
    "has_answer": true
  }
}
```

#### 获取对话历史
```http
GET /api/conversations
```

#### 重新加载配置
```http
POST /api/reload-config
```

响应：
```json
{
  "success": true,
  "message": "配置重载成功",
  "config": {
    "environment": "development",
    "debug": true,
    "port": 5001,
    "api_key_configured": true,
    "gemini_available": true
  }
}
```

### WebSocket 事件

#### 连接事件
- `connect`: 客户端连接时触发
- `disconnect`: 客户端断开连接时触发

#### 数据事件
- `conversation_history`: 发送历史对话记录
- `new_conversation`: 新对话创建时推送
- `conversation_updated`: 对话更新时推送
- `request_answer`: 请求生成回答
- `error`: 错误信息推送

## 🎯 部署特点

### ✅ 新架构优势

- **⚡ 极速启动** - 一键完成配置和启动
- **🔧 智能配置** - 自动检测并创建配置文件
- **💚 资源友好** - 直接运行，无容器开销
- **📝 调试友好** - 直观的日志输出和错误提示
- **🛠️ 开发便利** - 支持热重载和实时调试
- **🔒 配置安全** - 自动生成安全密钥

### 🎯 适用场景

- ✨ **开发环境** - 快速开发和测试
- 🧪 **原型验证** - 快速验证想法
- 📚 **学习使用** - 简单易懂的部署方式
- 🏠 **个人项目** - 轻量级部署方案
- 🏢 **小型团队** - 简化的运维管理

## 🔧 开发指南

### 项目结构
```
interview-backend/
├── app.py                 # 主应用文件
├── config.py              # 配置管理
├── config_manager.py      # 配置管理器
├── gemini_client.py       # Gemini API客户端
├── requirements.txt       # Python依赖
├── .env.example          # 环境变量示例
├── .env.development      # 开发环境配置
├── .env.production       # 生产环境配置
├── setup.sh              # 配置向导脚本
├── start.sh              # 启动脚本
├── test_api.py           # API测试脚本
├── .gitignore            # Git忽略文件
└── README.md             # 项目文档
```

### 本地开发
```bash
# 1. 配置环境
cp .env.example .env
# 编辑 .env 文件，配置 GEMINI_API_KEY

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 验证配置
python config_manager.py validate

# 5. 启动服务
python app.py
```

### 配置管理
```bash
# 验证配置
python config_manager.py validate

# 查看配置摘要
python config_manager.py summary

# 生成安全密钥
python config_manager.py generate-key
```

### 测试
```bash
# 使用测试脚本（推荐）
python test_api.py

# 手动测试
curl http://localhost:5001/health

# 测试问题提交
curl -X POST http://localhost:5001/api/question \
  -H "Content-Type: application/json" \
  -d '{"question": "测试问题"}'
```

## 🚀 生产环境部署

### 环境配置
```bash
# 1. 复制配置文件
cp .env.example .env

# 2. 编辑生产环境配置
nano .env

# 3. 验证配置
python config_manager.py validate
```

### 生产环境建议配置
```bash
# 必须修改的配置
GEMINI_API_KEY=your_actual_api_key
SECRET_KEY=your_strong_secret_key
FLASK_ENV=production
DEBUG=False

# 安全配置
CORS_ORIGINS=https://yourdomain.com
RATE_LIMIT_ENABLED=True
MAX_REQUESTS_PER_MINUTE=30

# 日志配置
LOG_LEVEL=INFO
```

### 进程管理
```bash
# 使用 PM2 管理进程
npm install -g pm2

# 创建 PM2 配置
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'interview-backend',
    script: 'app.py',
    interpreter: './venv/bin/python',
    env: {
      FLASK_ENV: 'production'
    }
  }]
}
EOF

# 启动服务
pm2 start ecosystem.config.js
```

## 🔍 故障排除

### 常见问题

#### 1. 配置文件问题
```bash
# 检查配置文件是否存在
ls -la .env

# 如果不存在，复制示例文件
cp .env.example .env

# 验证配置
python config_manager.py validate

# 查看配置摘要
python config_manager.py summary
```

#### 2. API Key 配置问题
```bash
# 检查 API Key 配置
grep GEMINI_API_KEY .env

# 确保不是默认值
# 应该是: GEMINI_API_KEY=your_actual_api_key
# 而不是: GEMINI_API_KEY=your_gemini_api_key_here

# 获取 API Key: https://makersuite.google.com/app/apikey
```

#### 3. 密钥配置问题
```bash
# 生成新的安全密钥
python config_manager.py generate-key

# 或使用 Python 命令
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 将生成的密钥复制到 .env 文件的 SECRET_KEY 配置项
```

#### 4. 端口占用
```bash
# 查看端口占用
lsof -i :5001

# 修改端口（编辑 .env 文件）
PORT=5002
```

#### 5. 配置修改不生效问题
```bash
# 问题：修改 .env 文件后配置不生效
# 解决方案：使用配置重载功能

# 方式一：重新加载配置
python config_manager.py reload

# 方式二：通过API重载（服务运行时）
curl -X POST http://localhost:5001/api/reload-config

# 方式三：重启服务
./start.sh restart
```

#### 6. Python 环境问题
```bash
# 检查 Python 版本
python3 --version

# 重新创建虚拟环境
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📝 更新日志

### v1.0.0
- 初始版本发布
- 支持Gemini API集成
- WebSocket实时通信
- 基础对话管理功能

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📋 快速命令参考

### 首次使用
```bash
# 1. 配置环境
cp .env.example .env
nano .env  # 编辑配置文件

# 2. 启动服务
./start.sh
```

### 启动和管理
```bash
./start.sh              # 启动服务
./start.sh stop         # 停止服务
./start.sh restart      # 重启服务
./start.sh health       # 健康检查
./start.sh help         # 显示帮助
```

### 配置管理
```bash
# 配置验证和管理
python config_manager.py validate      # 验证配置
python config_manager.py summary       # 查看配置摘要
python config_manager.py generate-key  # 生成安全密钥
python config_manager.py reload        # 重新加载配置

# 配置重载测试
python test_config_reload.py           # 测试配置重载功能
```

### 测试和验证
```bash
# API 测试
python test_api.py                    # 运行完整测试
curl http://localhost:5001/health     # 快速健康检查
```

### 开发调试
```bash
# 查看日志（服务运行时直接输出到控制台）
# 检查进程
ps aux | grep python

# 检查端口
lsof -i :5001

# 手动启动（调试模式）
python app.py
```

## �📞 支持

如有问题或建议，请：
- 创建 [Issue](https://github.com/your-repo/interview-backend/issues)
- 发送邮件至：your-email@example.com

---

**注意**: 请确保妥善保管你的Gemini API Key，不要将其提交到版本控制系统中。
