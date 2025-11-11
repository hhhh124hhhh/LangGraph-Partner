# AI Partner API 快速启动指南

## 🚀 5分钟快速开始

### 1. 环境准备

```bash
# 克隆或下载项目到本地
cd demo/web_interface/backend

# 创建Python虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API密钥

```bash
# 复制环境变量配置文件
cp .env.example .env

# 编辑 .env 文件，设置智谱AI API密钥
# OPENAI_API_KEY=your_zhipu_api_key_here
```

### 3. 启动服务

```bash
# 方式1: 使用启动脚本 (推荐)
python run.py dev

# 方式2: 直接使用uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 方式3: 使用shell脚本 (Linux/Mac)
chmod +x start.sh
./start.sh dev
```

### 4. 访问服务

- **API服务**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 📋 功能验证

### 测试对话功能

```bash
curl -X POST "http://localhost:8000/api/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好，我想了解一下LangGraph",
    "context_turns": 5,
    "enable_search": true,
    "enable_tools": true
  }'
```

### 测试画像功能

```bash
curl -X GET "http://localhost:8000/api/persona/context"
```

### 测试记忆功能

```bash
curl -X GET "http://localhost:8000/api/memory/stats"
```

## 🔧 常见问题解决

### 问题1: API密钥错误

**错误信息**: `AI service initialization failed`

**解决方案**:
1. 检查 `.env` 文件中的 `OPENAI_API_KEY` 是否正确设置
2. 确认API密钥有效且有足够额度
3. 重启服务

```bash
# 验证环境变量
echo $OPENAI_API_KEY
```

### 问题2: 依赖安装失败

**错误信息**: `Package installation failed`

**解决方案**:
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 问题3: 端口占用

**错误信息**: `Address already in use`

**解决方案**:
```bash
# 查找占用端口的进程
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# 更换端口
uvicorn app.main:app --port 8001
```

### 问题4: 向量数据库初始化失败

**错误信息**: `Vector store connection failed`

**解决方案**:
```bash
# 删除并重建向量数据库
rm -rf vector_db
mkdir vector_db

# 重启服务
python run.py dev
```

## 🎯 核心功能演示

### 1. 智能对话

```python
import requests

# 发送消息
response = requests.post("http://localhost:8000/api/chat/", json={
    "message": "帮我设计一个LangGraph智能体",
    "session_id": "demo_session"
})

print(response.json()["response"])
```

### 2. 个性化画像

```python
# 获取画像上下文
response = requests.get("http://localhost:8000/api/persona/context")
context = response.json()

print(f"用户画像: {context['user_persona']['name']}")
print(f"AI画像: {context['ai_persona']['name']}")
print(f"兼容性: {context['compatibility_score']}")
```

### 3. 知识检索

```python
# 语义搜索
response = requests.post("http://localhost:8000/api/knowledge/search", json={
    "query": "FastAPI性能优化",
    "top_k": 3
})

for result in response.json():
    print(f"内容: {result['content'][:50]}...")
    print(f"相似度: {result['similarity']}")
```

### 4. 演示场景

```python
# 获取演示场景
response = requests.get("http://localhost:8000/api/demo/scenarios")
scenarios = response.json()

for scenario in scenarios:
    print(f"场景: {scenario['name']}")
    print(f"难度: {scenario['difficulty']}")
    print(f"描述: {scenario['description']}")
```

## 🛠️ 开发模式

### 启用调试模式

```bash
export API_DEBUG=true
export API_RELOAD=true
python run.py dev
```

### 运行测试

```bash
# 运行所有测试
python run.py test

# 或者直接使用pytest
pytest tests/ -v
```

### 查看日志

```bash
# 实时查看日志
tail -f app.log

# 查看错误日志
grep ERROR app.log
```

## 🐳 Docker部署

### 构建镜像

```bash
docker build -t ai-partner-api .
```

### 运行容器

```bash
# 确保.env文件存在
docker run -d \
  --name ai-partner-api \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  ai-partner-api
```

### 使用Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 停止服务
docker-compose down
```

## 📊 性能监控

### 健康检查

```bash
curl http://localhost:8000/health
```

### 性能测试

```bash
# 安装压测工具
pip install locust

# 运行压测
locust -f tests/locustfile.py --host=http://localhost:8000
```

## 🎚️ 配置调优

### 环境变量

```bash
# 高并发配置
export WORKERS=4
export MAX_CONNECTIONS=1000

# 性能优化
export LLM_TEMPERATURE=0.7
export DEFAULT_SEARCH_RESULTS=5

# 日志配置
export LOG_LEVEL=INFO
export LOG_FORMAT=json
```

### 资源限制

```python
# 在 uvicorn 启动参数中设置
uvicorn app.main:app \
  --workers 4 \
  --worker-connections 1000 \
  --timeout 120 \
  --keep-alive 2
```

## 🔍 故障排除

### 日志分析

```bash
# 查看启动日志
docker logs ai-partner-api

# 查看错误详情
grep -A 5 -B 5 "ERROR" app.log
```

### 性能分析

```bash
# 安装性能分析工具
pip install py-spy

# 分析CPU使用
py-spy top --pid <process_id>

# 生成性能报告
py-spy record -o profile.svg --pid <process_id>
```

## 📚 更多资源

### 文档
- [完整API文档](http://localhost:8000/docs)
- [架构设计](ARCHITECTURE.md)
- [项目说明](README.md)

### 示例代码
- [API使用示例](examples/)
- [测试用例](tests/)
- [配置示例](config/)

### 社区支持
- [GitHub Issues](https://github.com/your-repo/issues)
- [讨论区](https://github.com/your-repo/discussions)

## 🎉 成功验证

如果看到以下输出，说明启动成功：

```json
{
  "name": "AI Partner API",
  "version": "1.0.0",
  "status": "running",
  "docs_url": "/docs"
}
```

现在您可以开始使用AI Partner API构建您的应用了！