# 🚀 AI Partner Demo 快速启动指南

## 🎯 最简单启动方式

由于Windows环境的特殊性，推荐以下启动顺序：

### 第一步：启动后端

在项目根目录（`F:/person/3-数字化集锦/LangGraph/`）下运行：

```bash
# 1. 打开命令提示符 (cmd)
# 2. 激活虚拟环境
cd F:/person/3-数字化集锦/LangGraph
venv\Scripts\activate

# 3. 启动后端
cd demo\web_interface\backend
python run.py dev
```

### 第二步：启动前端（新开一个命令提示符）

```bash
# 1. 打开新的命令提示符
# 2. 进入前端目录
cd F:/person/3-数字化集锦/LangGraph\demo\web_interface\frontend

# 3. 安装依赖（首次运行）
npm install

# 4. 启动前端
npm run dev
```

### 第三步：访问Demo

- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 📋 启动前检查清单

- [ ] 虚拟环境存在 (`F:/person/3-数字化集锦/LangGraph/venv/`)
- [ ] Node.js已安装
- [ ] 智谱AI API密钥已配置
- [ ] AI Partner智能体可以导入

## 🔑 API密钥配置

1. **复制配置文件**:
```bash
cd F:/person/3-数字化集锦/LangGraph\demo\web_interface\backend
copy .env.example .env
```

2. **编辑.env文件**，设置API密钥：
```env
ZHIPU_API_KEY=your_actual_api_key_here
```

## 🎉 验证启动成功

当看到以下信息时，说明启动成功：

### 后端成功标识
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 前端成功标识
```
Local:   http://localhost:3000/
ready in 1.2s
```

## 🛠️ 故障排除

### 问题1：虚拟环境激活失败
```bash
# 检查虚拟环境路径
dir F:/person/3-数字化集锦/LangGraph/venv/Scripts/

# 重新激活
F:/person/3-数字化集锦/LangGraph/venv/Scripts/activate
```

### 问题2：AI Partner导入失败
```bash
# 在激活的虚拟环境中安装依赖
pip install langgraph langchain-core

# 测试导入
python -c "from agents.partner_agent import AIPartnerAgent; print('成功!')"
```

### 问题3：端口占用
```bash
# 检查端口占用
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# 结束占用进程
taskkill /PID <进程ID> /F
```

## 📞 成功指标

启动成功后，您可以：

✅ **访问前端界面**: http://localhost:3000
✅ **查看API文档**: http://localhost:8000/docs
✅ **测试对话功能**: 在前端界面与AI Partner对话
✅ **查看实时状态**: 观察LangGraph状态流程
✅ **体验记忆功能**: 测试跨会话记忆关联

---

**🎊 准备好体验AI Partner的强大功能了吗？**