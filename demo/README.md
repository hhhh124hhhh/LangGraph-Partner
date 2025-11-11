# AI Partner 智能体演示系统

基于LangGraph的个性化AI对话伙伴完整演示系统，展示从Coze到LangGraph的技术升级价值。

## 🎯 核心功能演示

### 1. 个性化对话系统
- **画像驱动**: 基于用户和AI画像的个性化对话
- **动态学习**: 根据对话历史优化画像
- **上下文感知**: 深度理解对话场景和用户需求

### 2. 智能记忆管理
- **短期记忆**: 当前对话的上下文保持
- **长期记忆**: 跨会话的知识积累和关联
- **记忆网络**: 可视化的知识关联图谱

### 3. 向量化知识检索
- **语义搜索**: 基于ChromaDB的智能检索
- **上下文理解**: 超越关键词的语义匹配
- **知识关联**: 发现相关知识点的关联关系

### 4. LangGraph技术优势
- **状态图架构**: 可视化的决策流程
- **智能路由**: 基于上下文的智能决策
- **工具集成**: 无缝的外部工具调用

## 🏗️ 项目结构

```
demo/
├── web_interface/          # Web演示界面
│   ├── frontend/          # React前端
│   │   ├── src/
│   │   │   ├── components/    # UI组件
│   │   │   │   ├── Chat/      # 对话组件
│   │   │   │   ├── Visualization/  # 可视化组件
│   │   │   │   ├── Comparison/     # 对比面板
│   │   │   │   └── Demo/           # 演示组件
│   │   │   ├── pages/       # 页面组件
│   │   │   ├── hooks/       # 自定义hooks
│   │   │   ├── services/    # API服务
│   │   │   ├── utils/       # 工具函数
│   │   │   └── types/       # TypeScript类型
│   │   ├── public/
│   │   └── package.json
│   └── backend/           # FastAPI后端
│       ├── app/
│       │   ├── api/        # API路由
│       │   ├── core/       # 核心配置
│       │   ├── models/     # 数据模型
│       │   └── services/   # 业务服务
│       └── requirements.txt
├── demo_data/             # 演示数据
│   ├── sample_notes/      # 示例笔记
│   ├── personas/          # 预设画像
│   └── conversations/     # 演示对话
├── deployment/            # 部署配置
│   ├── docker/           # Docker配置
│   ├── netlify/          # Netlify配置
│   └── local/            # 本地部署配置
└── docs/                 # 文档
    ├── demo_guide.md     # 演示指南
    ├── api_reference.md  # API参考
    └── deployment.md     # 部署指南
```

## 🚀 快速开始 (推荐)

### 方法1: 简化启动 (复用现有环境)

```bash
# 1. 确保在项目根目录，激活虚拟环境
cd F:/person/3-数字化集锦/LangGraph
./venv/Scripts/activate

# 2. 进入demo目录并启动
cd demo
python start_demo_simplified.py
```

### 方法2: 手动启动

1. **激活现有虚拟环境**
```bash
cd F:/person/3-数字化集锦/LangGraph
./venv/Scripts/activate
```

2. **启动后端** (第一个终端)
```bash
cd demo/web_interface/backend
python run.py dev
```

3. **启动前端** (第二个终端)
```bash
cd demo/web_interface/frontend
npm install  # 首次运行需要
npm run dev
```

4. **访问演示**
- 前端界面: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

### API密钥配置

1. **复制配置文件**:
```bash
cd demo/web_interface/backend
cp .env.example .env
```

2. **设置智谱AI API密钥**:
编辑 `.env` 文件中的 `ZHIPU_API_KEY`

### 演示功能访问

1. **主演示界面**: `/demo` - 完整功能演示
2. **对话界面**: `/chat` - AI Partner对话体验
3. **可视化面板**: `/visualization` - 状态和记忆可视化
4. **对比分析**: `/comparison` - Coze vs LangGraph对比

## 🎨 演示流程

### 初识AI Partner (5分钟)
1. 个性化画像介绍
2. 基于画像的对话演示
3. 实时状态可视化展示

### 智能记忆体验 (5分钟)
1. 跨会话记忆关联演示
2. 记忆网络可视化展示
3. 知识图谱漫游体验

### 知识检索威力 (5分钟)
1. 语义搜索 vs 关键词搜索对比
2. 知识关联路径展示
3. 智能问答演示

### 技术优势解析 (5分钟)
1. LangGraph vs Coze详细对比
2. 状态图架构可视化
3. 技术升级价值展示

## 🛠️ 技术栈

### 前端
- **React 18** + TypeScript
- **Vite** - 快速构建
- **Tailwind CSS** - 样式框架
- **Recharts** - 数据可视化
- **D3.js** - 复杂网络图
- **Zustand** - 状态管理

### 后端
- **FastAPI** - 高性能API框架
- **Python** - 智能体语言
- **WebSockets** - 实时通信
- **现有AI Partner代码** - 核心智能体逻辑

### 数据存储
- **ChromaDB** - 向量数据库（复用现有）
- **浏览器存储** - 会话数据
- **文件系统** - 演示数据

## 📊 核心演示价值

### 相比Coze的技术优势
| 功能特性 | Coze | LangGraph AI Partner |
|---------|------|----------------------|
| **个性化程度** | 基础模板配置 | 深度画像驱动 + 动态学习 |
| **记忆能力** | 会话级别 | 多层记忆 + 跨会话关联 |
| **知识检索** | 关键词匹配 | 语义向量化 + 上下文理解 |
| **架构透明度** | 黑盒操作 | 状态图可视化 |
| **扩展性** | 平台限制 | 完全自定义 |

### 演示指标
- **个性化准确率**: 85%+ 的对话符合画像预期
- **记忆关联准确度**: 90%+ 的跨会话关联准确
- **知识检索相关性**: 平均相似度0.8+
- **响应延迟**: <2秒的智能体响应
- **用户体验评分**: 预期4.5/5.0+

## 🌟 创新亮点

1. **实时状态可视化**: LangGraph决策流程实时展示
2. **记忆网络图谱**: 可视化的知识关联网络
3. **智能画像学习**: 动态优化的个性化体验
4. **语义搜索威力**: 超越关键词的智能检索
5. **技术透明度**: 让AI决策过程可见可控

## 📞 联系和支持

- **技术文档**: `docs/` 目录
- **API参考**: `docs/api_reference.md`
- **部署指南**: `docs/deployment.md`
- **演示指南**: `docs/demo_guide.md`

这个演示系统完整展示了AI Partner从Coze到LangGraph的技术升级价值，为用户提供了直观、深入的AI智能体体验。