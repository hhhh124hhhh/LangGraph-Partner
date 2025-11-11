# 🚀 AI Partner Demo 简化启动指南

## 📋 前置要求

确保您的系统已安装：
- **Python 3.8+** (已有虚拟环境)
- **Node.js 16+**
- **智谱AI API密钥**

## ⚡ 一键启动 (复用现有环境)

### 方法1: 简化启动脚本 (推荐)

```bash
# 1. 确保在项目根目录
cd F:/person/3-数字化集锦/LangGraph

# 2. 激活现有虚拟环境
./venv/Scripts/activate

# 3. 进入demo目录并启动
cd demo
python start_demo_simplified.py
```

脚本将自动：
- ✅ 检查现有虚拟环境
- ✅ 安装Demo特有的依赖
- ✅ 启动后端和前端服务
- ✅ 打开浏览器访问演示页面

### 方法2: 手动启动 (最简单)

```bash
# 1. 激活虚拟环境
cd F:/person/3-数字化集锦/LangGraph
./venv/Scripts/activate

# 2. 启动后端 (在第一个终端)
cd demo/web_interface/backend
python run.py dev

# 3. 启动前端 (在第二个终端)
cd demo/web_interface/frontend
npm install  # 首次运行需要
npm run dev
```

## 🔑 API密钥配置

### 快速配置
1. 复制环境变量文件：
```bash
cd demo/web_interface/backend
cp .env.example .env
```

2. 编辑 `.env` 文件，设置智谱AI API密钥：
```bash
ZHIPU_API_KEY=your_actual_api_key_here
```

### 获取智谱AI API密钥
1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册并登录账户
3. 创建API密钥
4. 复制密钥到 `.env` 文件中

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

## 🛠️ 故障排除

### 常见问题

#### 1. 虚拟环境问题
```bash
# 确保在正确的目录激活环境
cd F:/person/3-数字化集锦/LangGraph
./venv/Scripts/activate

# 验证环境
python --version
pip list | grep fastapi
```

#### 2. 端口占用
```bash
# 检查端口占用
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# 关闭占用进程
taskkill /PID <进程ID> /F
```

#### 3. 前端依赖问题
```bash
# 清理并重新安装
cd demo/web_interface/frontend
rm -rf node_modules package-lock.json
npm install
```

#### 4. API密钥问题
```bash
# 验证API密钥设置
cd demo/web_interface/backend
cat .env | grep ZHIPU_API_KEY

# 测试API连接
python -c "from utils.llm import get_llm; llm=get_llm(); print('API连接成功')"
```

#### 5. 后端启动失败
```bash
# 检查依赖是否完整
pip install -r requirements.txt

# 检查Python路径
where python
```

## 📞 环境验证

### 验证脚本
```python
# 在demo目录下运行验证脚本
python -c "
import sys
sys.path.append('../')
from utils.llm import get_llm
try:
    llm = get_llm()
    print('✅ AI Partner智能体加载成功')
except Exception as e:
    print(f'❌ 智能体加载失败: {e}')
"
```

### 检查点清单
- [ ] 虚拟环境已激活
- [ ] 智谱AI API密钥已设置
- [ ] Node.js和npm已安装
- [ ] 端口8000和3000未被占用
- [ ] AI Partner智能体可以正常导入

## 🎉 成功指标

当您看到以下内容时，说明启动成功：

✅ **后端启动成功**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

✅ **前端启动成功**:
```
Local:   http://localhost:3000/
ready in 1.2s
```

✅ **浏览器自动打开**演示页面

✅ **API文档可访问**: http://localhost:8000/docs

## 🔗 相关文件

- **完整启动脚本**: `start_demo.py` (包含虚拟环境创建)
- **简化启动脚本**: `start_demo_simplified.py` (复用现有环境)
- **环境配置**: `web_interface/backend/.env`
- **API密钥申请**: https://open.bigmodel.cn/

---

**享受您的AI Partner演示体验！** 🎊

💡 **提示**: 如果遇到问题，请先检查虚拟环境是否正确激活，这是最常见的启动失败原因。