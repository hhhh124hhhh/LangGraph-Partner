# AI Partner API Backend

基于 FastAPI 的 AI Partner 智能体后端服务，提供完整的对话、画像、记忆和知识管理功能。

## 功能特性

### 🔥 核心功能
- **智能对话**: 基于LangGraph的AI对话系统
- **个性化画像**: 用户和AI画像管理与动态更新
- **记忆系统**: 对话历史记忆和上下文管理
- **知识检索**: 基于向量数据库的语义搜索
- **工具集成**: 天气查询、计算器等实用工具

### 🛠️ 技术特性
- **高性能**: FastAPI异步框架，支持高并发
- **类型安全**: Pydantic数据验证和序列化
- **API文档**: 自动生成Swagger文档
- **错误处理**: 完善的异常处理机制
- **安全性**: 输入验证、CORS支持、速率限制

## 项目结构

```
backend/
├── app/                    # 应用主目录
│   ├── api/                # API路由模块
│   │   ├── chat.py         # 对话相关API
│   │   ├── persona.py      # 画像管理API
│   │   ├── memory.py       # 记忆管理API
│   │   ├── knowledge.py    # 知识检索API
│   │   └── demo.py         # 演示功能API
│   ├── core/               # 核心配置
│   │   ├── config.py       # 应用配置
│   │   ├── exceptions.py   # 自定义异常
│   │   └── security.py     # 安全相关
│   ├── models/             # 数据模型
│   │   ├── chat.py         # 对话模型
│   │   ├── persona.py      # 画像模型
│   │   └── response.py     # 响应模型
│   ├── services/           # 业务服务
│   │   ├── chat_service.py # 对话服务
│   │   ├── persona_service.py # 画像服务
│   │   └── demo_service.py # 演示服务
│   ├── utils/              # 工具函数
│   │   └── ai_partner.py   # AI Partner集成
│   └── main.py             # 应用入口
├── requirements.txt        # Python依赖
├── requirements_simplified.txt # 简化版依赖（可选）
├── start_ai_partner.py     # 统一启动脚本（推荐使用）
├── README.md               # 项目说明
└── ...其他配置文件
```

## 快速开始

### 1. 环境准备

项目提供了统一的启动脚本 `start_ai_partner.py`，它会自动处理虚拟环境创建、依赖安装和环境配置。

### 2. 配置环境

在 demo 根目录创建 `.env` 文件（如果不存在），并设置必要的环境变量：

```bash
# 智谱AI API密钥（必填）
OPENAI_API_KEY=your_zhipu_api_key_here
```

### 3. 启动服务

使用统一启动脚本启动服务：

```bash
# 开发模式启动（推荐）
python start_ai_partner.py dev

# 生产模式启动
python start_ai_partner.py prod

# 仅安装依赖
python start_ai_partner.py install

# 检查服务健康状态
python start_ai_partner.py health

# 初始化项目（创建目录、安装依赖）
python start_ai_partner.py setup
```

#### 启动脚本参数说明

```bash
# 跳过依赖安装
python start_ai_partner.py dev --skip-install

# 强制重新加载环境变量
python start_ai_partner.py dev --force-reload

# 指定虚拟环境路径
python start_ai_partner.py dev --venv-path /path/to/venv
```

### 4. 访问服务

- **API服务**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## API接口

### 对话接口

#### 发送消息
```http
POST /api/chat/
Content-Type: application/json

{
  "message": "你好，我想了解一下LangGraph",
  "session_id": "optional_session_id",
  "context_turns": 5,
  "enable_search": true,
  "enable_tools": true
}
```

#### 获取会话状态
```http
GET /api/chat/state/{session_id}
```

#### 获取对话历史
```http
GET /api/chat/history?session_id=xxx&limit=10&offset=0
```

### 画像接口

#### 获取画像上下文
```http
GET /api/persona/context
```

#### 更新画像
```http
POST /api/persona/update
Content-Type: application/json

{
  "persona_type": "user",
  "attributes": {
    "name": "张三",
    "role": "软件工程师",
    "expertise_areas": ["Python", "FastAPI"]
  },
  "merge_strategy": "merge"
}
```

### 记忆接口

#### 获取记忆统计
```http
GET /api/memory/stats
```

#### 搜索记忆
```http
POST /api/memory/search
Content-Type: application/json

{
  "query": "LangGraph相关的讨论",
  "limit": 10
}
```

### 知识检索接口

#### 语义搜索
```http
POST /api/knowledge/search
Content-Type: application/json

{
  "query": "FastAPI最佳实践",
  "top_k": 5,
  "min_score": 0.3
}
```

#### 上传文档
```http
POST /api/knowledge/upload
Content-Type: multipart/form-data

file: document.pdf
title: 技术文档
tags: Python,Web开发
```

### 演示接口

#### 获取演示场景
```http
GET /api/demo/scenarios?category=基础教程&difficulty=初级
```

#### 运行演示
```http
POST /api/demo/run/langgraph_basics
Content-Type: application/json

{
  "params": {
    "interactive_mode": true
  }
}
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `API_HOST` | API服务器主机 | 0.0.0.0 |
| `API_PORT` | API服务器端口 | 8000 |
| `API_DEBUG` | 调试模式 | false |
| `OPENAI_API_KEY` | 智谱AI API密钥 | 必填 |
| `VECTOR_DB_PATH` | 向量数据库路径 | ./vector_db |
| `MEMORY_DIR` | 记忆存储目录 | ./memory |
| `CONFIG_DIR` | 配置文件目录 | ./config |
| `LLM_MODEL` | LLM模型名称 | glm-4.6 |
| `LLM_TEMPERATURE` | LLM温度参数 | 0.7 |

### 数据存储

系统使用以下目录存储数据：

- `./vector_db/`: ChromaDB向量数据库
- `./memory/`: 对话记忆数据
- `./config/`: 画像配置文件

## 部署指南

### Docker部署

```dockerfile
# Dockerfile示例
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# 构建镜像
docker build -t ai-partner-api .

# 运行容器
docker run -p 8000:8000 -v ./data:/app/data ai-partner-api
```

### 生产环境配置

使用统一启动脚本的生产模式：

```bash
python start_ai_partner.py prod
```

或者手动使用gunicorn部署：

```bash
# 使用gunicorn部署
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Nginx反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 开发指南

### 代码规范

- 使用Python类型注解
- 遵循PEP 8编码规范
- 编写单元测试
- 添加详细的文档字符串

### 测试

```bash
# 运行测试
pytest tests/

# 生成测试覆盖率报告
pytest --cov=app tests/
```

### 调试

使用统一启动脚本的开发模式自动启用调试功能：

```bash
python start_ai_partner.py dev
```

## 故障排除

### 常见问题

1. **API密钥错误**
   ```
   错误：AI service initialization failed
   解决：检查 .env 文件中的 OPENAI_API_KEY 设置
   ```

2. **向量数据库连接失败**
   ```
   错误：Vector store connection failed
   解决：检查向量数据库路径和权限
   ```

3. **依赖安装失败**
   ```
   错误：Package installation failed
   解决：升级pip版本，使用国内镜像源
   ```

### 日志查看

```bash
# 查看应用日志
tail -f app.log

# 查看错误日志
grep ERROR app.log
```

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

- 项目主页：[GitHub Repository]
- 问题反馈：[Issues]
- 技术讨论：[Discussions]

---

**注意**: 这是一个演示项目，请根据实际需求进行相应的安全配置和性能优化。