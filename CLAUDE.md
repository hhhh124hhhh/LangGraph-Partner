# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个基于 LangGraph 的 AI 智能体开发项目，集成了 AI Partner Chat 个性化对话系统。项目从 Coze 平台迁移而来，提供更强大的个性化和记忆管理功能。

## 常用命令

### 环境设置
```bash
# 安装依赖
pip install -r requirements.txt

# 激活虚拟环境（如果使用）
source venv/bin/activate  # Linux/Mac
./venv/Scripts/activate   # Windows
```

### 运行示例
```bash
# 基础智能体演示
python examples/basic_usage.py

# 工具调用智能体演示
python examples/tools_demo.py

# AI Partner 完整功能演示
python examples/partner_chat_demo.py

# 快速启动（推荐）
python examples/quick_start.py

# API连接测试
python test_api.py
```

### 知识库管理
```bash
# 重新索引笔记
python scripts/chunk_and_index.py
```

## 项目架构

### 核心技术栈
- **LangGraph**: 智能体状态图框架
- **LangChain**: LLM集成和工具管理
- **ChromaDB**: 向量数据库存储
- **sentence-transformers**: 文本向量化
- **智谱AI API**: 大语言模型服务

### 目录结构
```
agents/           # 智能体实现
├── basic_agent.py      # 基础对话智能体
├── tools_agent.py      # 工具调用智能体
└── partner_agent.py    # AI Partner Chat 智能体

tools/            # 自定义工具
├── weather.py          # 天气查询工具
└── calculator.py       # 数学计算工具

utils/            # 核心工具模块
├── llm.py              # LLM配置管理
├── vector_store.py     # 向量化存储系统
├── persona_manager.py  # 画像管理系统
└── memory_manager.py   # 对话记忆管理

config/           # 配置文件
├── user-persona.md     # 用户画像定义
└── ai-persona.md       # AI画像定义

examples/         # 示例和演示
scripts/          # 工具脚本
notes/            # 用户笔记（知识库源）
vector_db/        # 向量数据库存储
memory/           # 对话记忆存储
```

### 智能体状态图设计

项目中的智能体都基于 LangGraph 的状态图模式：

1. **基础智能体** (`basic_agent.py`): 简单的线性对话流程
2. **工具智能体** (`tools_agent.py`): 集成工具调用的条件分支流程
3. **Partner智能体** (`partner_agent.py`): 复杂的多节点状态管理，包括：
   - 上下文加载 (`load_context`)
   - 查询分析 (`analyze_query`)
   - 决策分支 (`decide_action`)
   - 笔记搜索 (`search_notes`)
   - 工具调用 (`call_tools`)
   - 回复生成 (`generate_response`)
   - 记忆更新 (`update_memory`)

### LLM配置系统

项目使用自定义的 `CustomLLM` 类 (`utils/llm.py`) 来统一管理LLM调用：
- 支持智谱AI API
- 兼容 LangChain 消息格式
- 提供环境变量配置管理
- 包含完整的错误处理和调试信息

## 配置管理

### 环境变量配置 (`.env.local`)
```
AI_DEFAULT_AGENT="claude"
AI_CLAUDE_BASE_URL="https://open.bigmodel.cn/api/anthropic"
AI_CLAUDE_API_KEY="your_api_key"
ANTHROPIC_MODEL="glm-4.6"
OPENAI_API_KEY="your_api_key"
OPENAI_BASE_URL="https://open.bigmodel.cn/api/paas/v4/chat/completions"
ZHIPU_API_KEY="your_api_key"
```

### 个性化配置
- 用户画像：`config/user-persona.md`
- AI画像：`config/ai-persona.md`
- 知识笔记：`notes/` 目录下的 Markdown 文件

## 开发指导

### 添加新智能体
1. 在 `agents/` 目录创建新文件
2. 定义状态类（继承 BaseModel）
3. 实现节点函数
4. 构建状态图（使用 StateGraph）
5. 在 `examples/` 中添加演示

### 添加新工具
1. 在 `tools/` 目录创建工具函数
2. 遵循统一的工具接口规范
3. 添加完整的错误处理
4. 在智能体中注册工具

### 调试技巧
- 使用 `test_api.py` 验证API连接
- 查看详细的调试输出（CustomLLM包含完整日志）
- 使用状态图的调试模式检查流程
- 验证环境变量配置是否正确

### 常见问题排查
1. **API连接失败**: 检查 `.env.local` 中的API密钥和URL
2. **向量检索问题**: 重新运行 `scripts/chunk_and_index.py`
3. **记忆功能异常**: 检查 `memory/` 目录权限
4. **依赖包问题**: 确保使用虚拟环境并正确安装依赖

## 测试和验证

项目提供多个层次的测试示例：
- 单元测试：`test_api.py`
- 集成测试：各个 `examples/` 文件
- 功能演示：`partner_chat_demo.py`, `memory_demo.py`, `multi_session_demo.py`