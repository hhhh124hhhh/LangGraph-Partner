# 🚀 AI Partner Demo 快速启动指南

## 📋 前置要求

确保您的系统已安装：
- **Python 3.8+**
- **Node.js 16+**
- **Git**

## ⚡ 一键启动 (推荐)

### 方法1: 使用启动脚本 (Windows/Linux/Mac)

```bash
# 1. 进入demo目录
cd demo

# 2. 运行启动脚本
python start_demo.py
```

脚本将自动：
- ✅ 检查系统要求
- ✅ 创建虚拟环境
- ✅ 安装所有依赖
- ✅ 启动后端和前端服务
- ✅ 打开浏览器访问演示页面

### 方法2: 使用Docker (推荐用于生产环境)

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置您的 API 密钥

# 2. 启动所有服务
docker-compose up -d

# 3. 访问演示页面
open http://localhost:3000
```

## 🔧 手动启动

### 启动后端服务

```bash
# 1. 进入后端目录
cd demo/web_interface/backend

# 2. 创建并激活虚拟环境
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置 ZHIPU_API_KEY

# 5. 启动服务
python run.py dev
```

后端将在 http://localhost:8000 启动

### 启动前端服务

```bash
# 1. 进入前端目录
cd demo/web_interface/frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev
```

前端将在 http://localhost:3000 启动

## 🔑 API密钥配置

### 获取智谱AI API密钥

1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册并登录账户
3. 创建API密钥
4. 复制密钥到环境变量中

### 配置方式

编辑 `.env` 文件：
```bash
# 设置智谱AI API密钥
ZHIPU_API_KEY=your_actual_api_key_here
```

## 🌐 访问演示

启动成功后，您可以访问：

- **主演示页面**: http://localhost:3000
- **后端API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 🎯 演示功能

### 核心功能展示

1. **🤖 个性化对话**
   - 基于用户画像的智能回应
   - 动态学习用户偏好
   - 上下文感知对话

2. **🧠 智能记忆系统**
   - 跨会话记忆关联
   - 智能知识网络可视化
   - 对话历史管理

3. **🔍 向量知识检索**
   - 语义搜索演示
   - 知识关联图谱
   - 实时检索对比

4. **📊 LangGraph vs Coze 对比**
   - 功能特性对比
   - 性能指标展示
   - 技术优势分析

### 演示流程

1. **初识AI Partner** (5分钟)
   - 个性化画像介绍
   - 基于画像的对话演示

2. **智能记忆体验** (5分钟)
   - 跨会话记忆关联
   - 记忆网络可视化

3. **知识检索威力** (5分钟)
   - 语义搜索对比
   - 知识关联展示

4. **技术优势解析** (5分钟)
   - LangGraph vs Coze对比
   - 技术架构可视化

## 🛠️ 故障排除

### 常见问题

#### 1. 端口冲突
```bash
# 检查端口占用
netstat -tulpn | grep :8000
netstat -tulpn | grep :3000

# 或修改端口配置
# 后端: 编辑 run.py 中的端口设置
# 前端: 编辑 vite.config.ts 中的端口设置
```

#### 2. Python虚拟环境问题
```bash
# 删除并重新创建虚拟环境
rm -rf venv
python -m venv venv
source venv/bin/activate  # Mac/Linux
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

#### 3. Node.js依赖问题
```bash
# 清理并重新安装
rm -rf node_modules package-lock.json
npm install
```

#### 4. API密钥问题
```bash
# 检查环境变量是否正确设置
echo $ZHIPU_API_KEY

# 测试API连接
python -c "from utils.llm import get_llm; llm=get_llm(); print('API连接成功')"
```

#### 5. 依赖安装失败
```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 日志查看

```bash
# 查看后端日志
tail -f logs/app.log

# 查看Docker日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 📞 获取帮助

如果遇到问题：

1. 查看详细文档: `docs/` 目录
2. 检查API文档: http://localhost:8000/docs
3. 查看系统状态: http://localhost:8000/health
4. 提交Issue: 在项目仓库创建Issue

## 🎉 演示成功！

当您看到以下界面时，说明演示系统启动成功：

- ✅ 后端服务运行正常
- ✅ 前端界面可访问
- ✅ API连接正常
- ✅ 演示数据加载完成

现在您可以开始体验AI Partner的强大功能了！

---

**享受您的AI Partner演示体验！** 🎊