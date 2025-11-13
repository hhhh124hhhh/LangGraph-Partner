/**
 * 文档系统页面
 * 提供完整的使用文档、教程和帮助中心
 */

import React, { useState, useEffect, useCallback } from 'react';
import Button from '@components/Button';
import { logger } from '@utils/logger';

// 文档类型定义
interface DocumentationSection {
  id: string;
  title: string;
  description: string;
  icon: string;
  articles: DocumentationArticle[];
}

interface DocumentationArticle {
  id: string;
  title: string;
  description: string;
  content: string;
  category: string;
  tags: string[];
  readTime: string;
  lastUpdated: string;
}

// 模拟文档数据
const DOCUMENTATION_SECTIONS: DocumentationSection[] = [
  {
    id: 'getting-started',
    title: '快速开始',
    description: '了解AI Partner的基本使用方法和核心概念',
    icon: '🚀',
    articles: [
      {
        id: 'installation',
        title: '安装与配置',
        description: '学习如何安装和配置AI Partner',
        category: '入门指南',
        tags: ['安装', '配置', '环境设置'],
        readTime: '5分钟',
        lastUpdated: '2024-01-15',
        content: `# 安装与配置

## 系统要求

- Node.js 16.0 或更高版本
- Python 3.8 或更高版本
- 4GB 以上内存
- 现代浏览器（Chrome、Firefox、Safari、Edge）

## 安装步骤

### 1. 克隆项目
\`\`\`bash
git clone https://github.com/your-repo/ai-partner.git
cd ai-partner
\`\`\`

### 2. 安装前端依赖
\`\`\`bash
cd frontend
npm install
\`\`\`

### 3. 安装后端依赖
\`\`\`bash
cd backend
pip install -r requirements.txt
\`\`\`

### 4. 配置环境变量
创建 \`.env\` 文件：
\`\`\`
AI_API_KEY=your_api_key_here
DATABASE_URL=your_database_url
VECTOR_DB_PATH=./vector_db
MEMORY_DIR=./memory
\`\`\`

### 5. 启动服务
\`\`\`bash
# 启动后端服务
cd backend
python main.py

# 启动前端服务
cd frontend
npm run dev
\`\`\`

## 验证安装

访问 http://localhost:3000 查看AI Partner界面。`
      },
      {
        id: 'first-conversation',
        title: '第一次对话',
        description: '学习如何与AI Partner进行第一次对话',
        category: '入门指南',
        tags: ['对话', '基础使用', '交互'],
        readTime: '3分钟',
        lastUpdated: '2024-01-15',
        content: `# 第一次对话

## 开始对话

1. 打开AI Partner界面
2. 在输入框中输入您的消息
3. 按Enter键或点击"发送"按钮
4. AI Partner将智能回复您的消息

## 对话技巧

- **清晰表达**：使用清晰、具体的语言描述您的问题
- **提供上下文**：如果您的问题涉及特定场景，请提供相关背景信息
- **多轮对话**：可以进行连续的对话，AI Partner会记住上下文
- **尝试不同功能**：探索AI Partner的各种功能，如知识检索、工具调用等

## 示例对话

**用户**：你好，我想了解一下AI Partner的功能

**AI Partner**：您好！我是AI Partner，一个智能对话助手。我可以帮助您：

💬 **自然语言对话** - 进行流畅的多轮对话
🧠 **记忆管理** - 记住重要的信息和偏好
📚 **知识检索** - 搜索和回答各种问题
🛠️ **工具调用** - 使用计算器、搜索等工具
🎯 **个性化服务** - 根据您的需求定制服务

请问有什么可以帮助您的吗？`
      },
      {
        id: 'basic-features',
        title: '核心功能概览',
        description: '了解AI Partner的主要功能特性',
        category: '功能介绍',
        tags: ['功能', '特性', '概览'],
        readTime: '8分钟',
        lastUpdated: '2024-01-15',
        content: `# 核心功能概览

## 🤖 智能对话

AI Partner的核心功能是智能对话，支持：
- 自然语言理解
- 上下文记忆
- 多轮对话
- 个性化回复

## 🧠 记忆管理

AI Partner具备强大的记忆能力：
- **短期记忆**：记住当前对话的上下文
- **长期记忆**：保存重要信息和用户偏好
- **记忆检索**：快速查找相关信息
- **记忆网络**：建立知识间的关联关系

## 📚 知识检索

内置知识库和检索功能：
- **语义搜索**：理解查询意图，找到相关信息
- **文档理解**：处理和分析各种文档
- **智能问答**：基于知识库回答问题
- **持续学习**：从对话中学习新知识

## 🛠️ 工具集成

集成多种实用工具：
- **计算器**：进行数学计算
- **搜索引擎**：获取最新信息
- **翻译工具**：多语言翻译
- **日历工具**：时间管理
- **更多工具**：持续扩展中

## 🎯 个性化服务

根据用户需求提供个性化体验：
- **用户画像**：理解用户特点和偏好
- **AI画像**：调整AI的个性风格
- **场景适配**：根据不同场景优化服务
- **推荐系统**：主动推荐相关内容`
      }
    ]
  },
  {
    id: 'advanced-features',
    title: '高级功能',
    description: '深入了解AI Partner的高级特性和使用技巧',
    icon: '⚡',
    articles: [
      {
        id: 'persona-system',
        title: '画像系统',
        description: '学习如何配置和使用用户画像与AI画像',
        category: '高级功能',
        tags: ['画像', '个性化', '配置'],
        readTime: '10分钟',
        lastUpdated: '2024-01-15',
        content: `# 画像系统

## 什么是画像系统

画像系统是AI Partner的核心特性之一，通过分析用户特点和行为模式，为每位用户提供个性化的对话体验。

## 用户画像

用户画像包含以下维度：

### 基本信息
- 姓名、年龄、职业
- 教育背景、专业领域
- 兴趣爱好、性格特点

### 行为模式
- 沟通风格偏好
- 信息处理习惯
- 决策方式倾向

### 需求偏好
- 关注的话题领域
- 期望的服务类型
- 交互方式偏好

## AI画像

AI画像定义了AI助手的个性特征：

### 沟通风格
- 正式 vs 轻松
- 简洁 vs 详细
- 直接 vs 委婉

### 专业领域
- 技术专家型
- 通识顾问型
- 生活助手型

### 服务特色
- 高效实用型
- 温暖关怀型
- 创新探索型

## 画像配置

### 1. 用户画像设置
在设置页面中填写您的个人信息：
\`\`\`json
{
  "name": "张三",
  "age": 28,
  "profession": "软件工程师",
  "interests": ["编程", "阅读", "旅行"],
  "personality": {
    "communication_style": "direct",
    "information_preference": "structured",
    "decision_making": "analytical"
  }
}
\`\`\`

### 2. AI画像选择
选择适合您需求的AI个性：
- **专业助手**：适合工作场景，专业高效
- **生活伙伴**：适合日常交流，温暖贴心
- **学习导师**：适合知识学习，循循善诱
- **创意伙伴**：适合头脑风暴，富有想象力

### 3. 画像匹配优化
系统会自动分析用户画像与AI画像的匹配度，并提供优化建议。

## 画像效果

启用画像系统后，您将体验到：

1. **个性化回复**：AI会根据您的特点调整回复风格
2. **精准推荐**：基于您的兴趣推荐相关内容
3. **高效沟通**：减少沟通成本，提高交流效率
4. **情感共鸣**：更好地理解您的情感需求`
      },
      {
        id: 'memory-management',
        title: '记忆管理',
        description: '掌握AI Partner的记忆功能和数据管理',
        category: '高级功能',
        tags: ['记忆', '数据管理', '隐私'],
        readTime: '12分钟',
        lastUpdated: '2024-01-15',
        content: `# 记忆管理

## 记忆系统架构

AI Partner采用分层记忆架构：

### 即时记忆 (工作记忆)
- 当前对话的上下文信息
- 临时状态和数据
- 自动清理，不长期保存

### 短期记忆 (会话记忆)
- 单次会话的重要信息
- 用户偏好和习惯
- 保留时间：7-30天

### 长期记忆 (永久记忆)
- 用户确认的重要信息
- 知识和经验积累
- 持久保存，可随时检索

## 记忆类型

### 事实记忆
\`\`\`
用户：我叫张三，是一名软件工程师
AI：已记住您是张三，软件工程师
\`\`\`

### 偏好记忆
\`\`\`
用户：我喜欢简洁明了的回答
AI：了解了，我会提供简洁的回答
\`\`\`

### 经验记忆
\`\`\`
用户：上次我们讨论的那个解决方案效果很好
AI：是的，记得上次的解决方案很成功
\`\`\`

### 关系记忆
\`\`\`
用户：我的同事李四也需要类似的帮助
AI：明白了，我会考虑李四与您的工作关系
\`\`\`

## 记忆管理功能

### 1. 记忆查看
在记忆管理页面可以：
- 查看所有保存的记忆
- 按类型和重要性筛选
- 搜索特定记忆内容

### 2. 记忆编辑
- 修正错误的记忆
- 更新过时的信息
- 补充缺失的细节

### 3. 记忆控制
- 设置记忆保留期限
- 选择记忆类型
- 管理隐私设置

### 4. 记忆导出
- 导出个人记忆数据
- 备份重要信息
- 数据迁移支持

## 隐私保护

### 数据加密
- 所有记忆数据采用端到端加密
- 传输过程使用SSL/TLS保护
- 存储数据加密处理

### 访问控制
- 严格的身份验证
- 细粒度权限管理
- 操作日志记录

### 数据清理
- 定期清理过期数据
- 用户主动删除支持
- 完全删除选项

## 使用建议

### 1. 重要信息确认
对于需要长期保存的重要信息，明确告知AI：
\`\`\`
用户：请记住这个信息：我的生日是5月20日
AI：好的，我已经记住了您的生日是5月20日
\`\`\`

### 2. 定期检查
定期查看和管理您的记忆数据，确保准确性。

### 3. 隐私设置
根据您的隐私需求，调整记忆保存策略。

### 4. 备份重要数据
对于特别重要的信息，考虑导出备份。`
      },
      {
        id: 'tools-integration',
        title: '工具集成',
        description: '了解和使用AI Partner集成的各种工具',
        category: '高级功能',
        tags: ['工具', '集成', '扩展'],
        readTime: '15分钟',
        lastUpdated: '2024-01-15',
        content: `# 工具集成

## 工具系统概述

AI Partner集成了多种实用工具，可以在对话中自动调用，为用户提供完整的解决方案。

## 内置工具

### 1. 计算器工具
**功能**：进行各种数学计算
**使用方式**：
\`\`\`
用户：帮我计算 15 * 8 + 120
AI：15 * 8 + 120 = 240
\`\`\`

**支持的计算类型**：
- 基础运算：加减乘除
- 高级运算：幂运算、三角函数
- 统计计算：平均值、标准差
- 单位转换：长度、重量、温度等

### 2. 搜索工具
**功能**：搜索网络信息和最新资讯
**使用方式**：
\`\`\`
用户：搜索最新的AI技术发展
AI：让我为您搜索最新的AI技术发展信息...
\`\`\`

**搜索能力**：
- 实时网络搜索
- 多语言搜索
- 结果筛选和排序
- 相关性评分

### 3. 翻译工具
**功能**：多语言文本翻译
**使用方式**：
\`\`\`
用户：请把"Hello World"翻译成中文
AI："Hello World" 的中文翻译是："你好世界"
\`\`\`

**支持语言**：
- 英语、中文、日语、韩语
- 法语、德语、西班牙语、俄语
- 阿拉伯语、印地语等100+种语言

### 4. 日历工具
**功能**：时间管理和日程安排
**使用方式**：
\`\`\`
用户：提醒我明天下午2点开会
AI：好的，我已经设置了明天下午2点的会议提醒
\`\`\`

**功能特性**：
- 日程创建和管理
- 提醒设置
- 时间冲突检测
- 定期活动安排

### 5. 文件处理工具
**功能**：文档处理和格式转换
**使用方式**：
\`\`\`
用户：帮我把这个Word文档转换成PDF
AI：我正在帮您转换文档格式...
\`\`\`

**支持格式**：
- 文档格式：DOC, DOCX, PDF, TXT
- 图片格式：JPG, PNG, GIF, SVG
- 数据格式：CSV, JSON, XML

## 工具调用机制

### 自动识别
AI会自动识别用户意图，选择合适的工具：
\`\`\`
用户：今天北京天气怎么样？
AI：[调用搜索工具] 今天北京天气晴朗，温度25°C...
\`\`\`

### 用户指定
用户可以明确指定使用某个工具：
\`\`\`
用户：用计算器帮我算一下
AI：好的，请告诉我需要计算什么
\`\`\`

### 组合使用
支持多个工具的组合使用：
\`\`\`
用户：帮我查一下去上海的机票，然后计算总费用
AI：[调用搜索工具] 正在查找机票...
    [调用计算器] 正在计算总费用...
\`\`\`

## 自定义工具

### 工具开发
开发者可以创建自定义工具：
\`\`\`python
from ai_partner.tools import BaseTool

class CustomTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "custom_tool"
        self.description = "自定义工具描述"

    def execute(self, parameters):
        # 工具执行逻辑
        return result
\`\`\`

### 工具注册
\`\`\`python
from ai_partner.registry import register_tool

register_tool(CustomTool())
\`\`\`

## 工具配置

### 工具启用/禁用
在设置页面可以：
- 启用或禁用特定工具
- 设置工具使用权限
- 配置工具参数

### 工具优先级
设置工具选择的优先级：
- 高优先级工具优先使用
- 冲突时的选择策略
- 用户偏好设置

## 使用技巧

### 1. 明确需求
清楚表达您需要什么工具帮助，提高识别准确性。

### 2. 提供上下文
为工具调用提供足够的上下文信息。

### 3. 验证结果
重要计算或查询后，验证工具结果的准确性。

### 4. 学习工具特性
了解各个工具的能力和限制，更好地利用它们。

## 安全考虑

### 数据保护
- 工具调用过程中的数据加密
- 敏感信息脱敏处理
- 访问权限控制

### 工具限制
- 恶意工具检测和阻止
- 使用频率限制
- 异常行为监控`
      }
    ]
  },
  {
    id: 'api-reference',
    title: 'API参考',
    description: '详细的API文档和开发指南',
    icon: '📚',
    articles: [
      {
        id: 'rest-api',
        title: 'REST API',
        description: '完整的REST API接口文档',
        category: 'API文档',
        tags: ['API', 'REST', '接口'],
        readTime: '20分钟',
        lastUpdated: '2024-01-15',
        content: `# REST API 文档

## API概述

AI Partner提供完整的REST API，支持以下功能：
- 对话管理
- 用户画像
- 记忆管理
- 知识检索
- 工具调用

## 基础信息

- **Base URL**: \`http://localhost:8000/api\`
- **认证方式**: Bearer Token
- **数据格式**: JSON
- **字符编码**: UTF-8

## 认证

### 获取访问令牌
\`\`\`bash
curl -X POST http://localhost:8000/api/auth/token \\
  -H "Content-Type: application/json" \\
  -d '{"username": "your_username", "password": "your_password"}'
\`\`\`

### 使用访问令牌
\`\`\`bash
curl -X GET http://localhost:8000/api/user/profile \\
  -H "Authorization: Bearer YOUR_TOKEN"
\`\`\`

## 对话API

### 发送消息
\`\`\`bash
curl -X POST http://localhost:8000/api/chat/ \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "message": "你好，AI Partner",
    "session_id": "optional_session_id"
  }'
\`\`\`

**响应**：
\`\`\`json
{
  "message_id": "msg_123456",
  "response": "您好！我是AI Partner...",
  "session_id": "session_789",
  "timestamp": "2024-01-15T10:30:00Z",
  "metadata": {
    "tokens_used": 150,
    "response_time": 1200
  }
}
\`\`\`

### 获取对话历史
\`\`\`bash
curl -X GET "http://localhost:8000/api/chat/history?session_id=session_789&limit=10&offset=0" \\
  -H "Authorization: Bearer YOUR_TOKEN"
\`\`\`

### 获取会话状态
\`\`\`bash
curl -X GET http://localhost:8000/api/chat/state/session_789 \\
  -H "Authorization: Bearer YOUR_TOKEN"
\`\`\`

## 用户画像API

### 获取用户画像
\`\`\`bash
curl -X GET http://localhost:8000/api/persona/user \\
  -H "Authorization: Bearer YOUR_TOKEN"
\`\`\`

### 更新用户画像
\`\`\`bash
curl -X POST http://localhost:8000/api/persona/update \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "type": "user",
    "data": {
      "name": "张三",
      "age": 28,
      "interests": ["编程", "阅读"]
    }
  }'
\`\`\`

### 获取AI画像
\`\`\`bash
curl -X GET http://localhost:8000/api/persona/ai \\
  -H "Authorization: Bearer YOUR_TOKEN"
\`\`\`

## 记忆管理API

### 获取记忆统计
\`\`\`bash
curl -X GET http://localhost:8000/api/memory/stats \\
  -H "Authorization: Bearer YOUR_TOKEN"
\`\`\`

### 搜索记忆
\`\`\`bash
curl -X POST http://localhost:8000/api/memory/search \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "重要项目",
    "limit": 10,
    "type": "fact"
  }'
\`\`\`

### 获取记忆网络
\`\`\`bash
curl -X GET http://localhost:8000/api/memory/network?session_id=session_789 \\
  -H "Authorization: Bearer YOUR_TOKEN"
\`\`\`

## 知识检索API

### 知识搜索
\`\`\`bash
curl -X POST http://localhost:8000/api/knowledge/search \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "人工智能的发展历史",
    "limit": 5,
    "threshold": 0.7
  }'
\`\`\`

### 获取文档列表
\`\`\`bash
curl -X GET "http://localhost:8000/api/knowledge/documents?limit=20&offset=0" \\
  -H "Authorization: Bearer YOUR_TOKEN"
\`\`\`

## 错误处理

### 错误响应格式
\`\`\`json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "请求参数无效",
    "details": {
      "field": "message",
      "reason": "消息不能为空"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
\`\`\`

### 常见错误码
- \`400 Bad Request\` - 请求参数错误
- \`401 Unauthorized\` - 认证失败
- \`403 Forbidden\` - 权限不足
- \`404 Not Found\` - 资源不存在
- \`429 Too Many Requests\` - 请求频率过高
- \`500 Internal Server Error\` - 服务器内部错误

## 限流规则

### 请求限制
- 每分钟最多100次请求
- 每天最多10000次请求
- 超出限制返回429状态码

### 响应头
\`\`\`http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248600
\`\`\`

## WebSocket API

### 连接WebSocket
\`\`\`javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = function() {
  // 认证
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'YOUR_TOKEN'
  }));
};
\`\`\`

### 实时消息
\`\`\`javascript
ws.send(JSON.stringify({
  type: 'chat_message',
  payload: {
    message: '你好',
    session_id: 'session_789'
  }
}));
\`\`\`

## SDK支持

### Python SDK
\`\`\`python
from ai_partner import AIPartner

client = AIPartner(api_key='YOUR_API_KEY')
response = client.chat.send_message('你好，AI Partner')
print(response.response)
\`\`\`

### JavaScript SDK
\`\`\`javascript
import { AIPartner } from 'ai-partner-js';

const client = new AIPartner({ apiKey: 'YOUR_API_KEY' });
const response = await client.chat.sendMessage('你好，AI Partner');
console.log(response.response);
\`\`\`

### 更多SDK
- Go SDK
- Java SDK
- PHP SDK
- Ruby SDK

## 更新日志

### v2.0.0 (2024-01-15)
- 新增画像管理API
- 改进记忆搜索功能
- 优化性能和稳定性

### v1.5.0 (2023-12-01)
- 添加WebSocket支持
- 增强工具调用功能
- 修复已知问题

查看完整的更新历史请访问：[更新日志](/changelog)`
      },
      {
        id: 'websocket-api',
        title: 'WebSocket API',
        description: '实时通信WebSocket接口文档',
        category: 'API文档',
        tags: ['WebSocket', '实时', '通信'],
        readTime: '15分钟',
        lastUpdated: '2024-01-15',
        content: `# WebSocket API 文档

## 概述

AI Partner WebSocket API提供实时双向通信能力，支持：
- 实时对话
- 状态同步
- 事件通知
- 流式响应

## 连接信息

- **WebSocket URL**: \`ws://localhost:8000/ws\`
- **协议版本**: WebSocket v13
- **支持子协议**: json

## 连接建立

### 基础连接
\`\`\`javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = function(event) {
  console.log('WebSocket连接已建立');
};
\`\`\`

### 带认证连接
\`\`\`javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = function(event) {
  // 发送认证信息
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'YOUR_ACCESS_TOKEN'
  }));
};

ws.onmessage = function(event) {
  const message = JSON.parse(event.data);
  if (message.type === 'auth_success') {
    console.log('认证成功');
  }
};
\`\`\`

## 消息格式

### 消息结构
\`\`\`json
{
  "type": "message_type",
  "payload": {
    // 消息数据
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "message_id": "msg_123456"
}
\`\`\`

### 认证消息
\`\`\`json
{
  "type": "auth",
  "payload": {
    "token": "your_access_token"
  }
}
\`\`\`

### 认证响应
\`\`\`json
{
  "type": "auth_success",
  "payload": {
    "user_id": "user_123",
    "session_id": "session_456"
  }
}
\`\`\`

## 对话消息

### 发送消息
\`\`\`json
{
  "type": "chat_message",
  "payload": {
    "message": "你好，AI Partner",
    "session_id": "session_789",
    "stream": true
  }
}
\`\`\`

### 流式响应
\`\`\`json
{
  "type": "chat_chunk",
  "payload": {
    "chunk": "您好",
    "message_id": "msg_123456",
    "is_final": false
  }
}
\`\`\`

### 完整响应
\`\`\`json
{
  "type": "chat_complete",
  "payload": {
    "message_id": "msg_123456",
    "response": "您好！我是AI Partner...",
    "session_id": "session_789",
    "metadata": {
      "tokens_used": 150,
      "response_time": 1200
    }
  }
}
\`\`\`

## 状态订阅

### 订阅会话状态
\`\`\`json
{
  "type": "subscribe",
  "payload": {
    "action": "subscribe_session",
    "session_id": "session_789"
  }
}
\`\`\`

### 状态更新通知
\`\`\`json
{
  "type": "state_update",
  "payload": {
    "session_id": "session_789",
    "status": "processing",
    "current_node": "generate_response",
    "progress": 0.6
  }
}
\`\`\`

### 取消订阅
\`\`\`json
{
  "type": "unsubscribe",
  "payload": {
    "action": "unsubscribe_session",
    "session_id": "session_789"
  }
}
\`\`\`

## 心跳机制

### 心跳请求
\`\`\`json
{
  "type": "ping"
}
\`\`\`

### 心跳响应
\`\`\`json
{
  "type": "pong",
  "payload": {
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
\`\`\`

### 自动心跳
\`\`\`javascript
let heartbeatInterval;

function startHeartbeat() {
  heartbeatInterval = setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'ping' }));
    }
  }, 30000); // 30秒一次
}

function stopHeartbeat() {
  if (heartbeatInterval) {
    clearInterval(heartbeatInterval);
  }
}

ws.onopen = startHeartbeat;
ws.onclose = stopHeartbeat;
\`\`\`

## 错误处理

### 错误消息
\`\`\`json
{
  "type": "error",
  "payload": {
    "code": "AUTHENTICATION_FAILED",
    "message": "认证失败",
    "details": "Token已过期"
  }
}
\`\`\`

### 连接错误处理
\`\`\`javascript
ws.onerror = function(error) {
  console.error('WebSocket错误:', error);
};

ws.onclose = function(event) {
  if (event.code !== 1000) {
    console.error('连接异常关闭:', event.code, event.reason);
    // 尝试重连
    setTimeout(connectWebSocket, 3000);
  }
};
\`\`\`

### 重连机制
\`\`\`javascript
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;

function connectWebSocket() {
  const ws = new WebSocket('ws://localhost:8000/ws');

  ws.onopen = function() {
    reconnectAttempts = 0;
    console.log('WebSocket连接成功');
  };

  ws.onclose = function(event) {
    if (reconnectAttempts < maxReconnectAttempts) {
      reconnectAttempts++;
      const delay = Math.pow(2, reconnectAttempts) * 1000; // 指数退避
      console.log(\`\${delay/1000}秒后尝试重连...\`);
      setTimeout(connectWebSocket, delay);
    } else {
      console.error('重连失败，请检查网络连接');
    }
  };

  return ws;
}
\`\`\`

## 完整示例

### React Hook示例
\`\`\`javascript
import { useState, useEffect, useRef } from 'react';

export function useWebSocket(token) {
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');

    ws.onopen = () => {
      setIsConnected(true);
      // 发送认证
      ws.send(JSON.stringify({
        type: 'auth',
        token: token
      }));
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);

      switch (message.type) {
        case 'chat_chunk':
          setMessages(prev => {
            const lastMessage = prev[prev.length - 1];
            if (lastMessage && lastMessage.id === message.payload.message_id) {
              // 更新最后一条消息
              return prev.map((msg, index) =>
                index === prev.length - 1
                  ? { ...msg, content: msg.content + message.payload.chunk }
                  : msg
              );
            } else {
              // 添加新消息
              return [...prev, {
                id: message.payload.message_id,
                content: message.payload.chunk,
                role: 'assistant',
                isComplete: false
              }];
            }
          });
          break;

        case 'chat_complete':
          setMessages(prev => prev.map(msg =>
            msg.id === message.payload.message_id
              ? { ...msg, isComplete: true }
              : msg
          ));
          break;
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
    };

    wsRef.current = ws;

    return () => {
      ws.close();
    };
  }, [token]);

  const sendMessage = (message, sessionId) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'chat_message',
        payload: { message, session_id: sessionId }
      }));
    }
  };

  return { messages, isConnected, sendMessage };
}
\`\`\`

### Node.js示例
\`\`\`javascript
const WebSocket = require('ws');

class AIPartnerWebSocket {
  constructor(token) {
    this.token = token;
    this.ws = null;
    this.handlers = new Map();
  }

  connect() {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket('ws://localhost:8000/ws');

      this.ws.on('open', () => {
        // 认证
        this.ws.send(JSON.stringify({
          type: 'auth',
          token: this.token
        }));
      });

      this.ws.on('message', (data) => {
        const message = JSON.parse(data);
        this.handleMessage(message);
      });

      this.ws.on('error', reject);
      this.ws.on('close', () => {
        console.log('WebSocket连接已关闭');
      });
    });
  }

  handleMessage(message) {
    const handler = this.handlers.get(message.type);
    if (handler) {
      handler(message.payload);
    }
  }

  on(type, handler) {
    this.handlers.set(type, handler);
  }

  sendMessage(message, sessionId) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'chat_message',
        payload: { message, session_id: sessionId }
      }));
    }
  }

  subscribe(sessionId) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'subscribe',
        payload: {
          action: 'subscribe_session',
          session_id: sessionId
        }
      }));
    }
  }
}

// 使用示例
const client = new AIPartnerWebSocket('your_token');

client.connect().then(() => {
  client.on('chat_complete', (payload) => {
    console.log('收到回复:', payload.response);
  });

  client.sendMessage('你好，AI Partner', 'session_123');
});
\`\`\`

## 性能优化

### 连接池管理
\`\`\`javascript
class WebSocketPool {
  constructor(maxConnections = 5) {
    this.connections = [];
    this.maxConnections = maxConnections;
  }

  getConnection() {
    const availableConnection = this.connections.find(
      conn => conn.readyState === WebSocket.OPEN
    );

    if (availableConnection) {
      return Promise.resolve(availableConnection);
    }

    if (this.connections.length < this.maxConnections) {
      const newConnection = new WebSocket('ws://localhost:8000/ws');
      this.connections.push(newConnection);
      return new Promise((resolve) => {
        newConnection.onopen = () => resolve(newConnection);
      });
    }

    return Promise.reject(new Error('连接池已满'));
  }
}
\`\`\`

### 消息队列
\`\`\`javascript
class MessageQueue {
  constructor() {
    this.queue = [];
    this.isProcessing = false;
  }

  enqueue(message) {
    this.queue.push(message);
    if (!this.isProcessing) {
      this.process();
    }
  }

  async process() {
    this.isProcessing = true;

    while (this.queue.length > 0) {
      const message = this.queue.shift();
      try {
        await this.sendMessage(message);
      } catch (error) {
        console.error('发送消息失败:', error);
      }
    }

    this.isProcessing = false;
  }

  async sendMessage(message) {
    // 实现消息发送逻辑
  }
}
\`\`\`

## 故障排除

### 常见问题

**Q: WebSocket连接失败**
A: 检查网络连接、防火墙设置，确保服务器正在运行

**Q: 认证失败**
A: 验证Token是否有效，检查Token是否过期

**Q: 消息发送失败**
A: 确认WebSocket连接状态，检查消息格式是否正确

**Q: 连接频繁断开**
A: 检查心跳机制，确认网络稳定性

### 调试工具
\`\`\`javascript
// WebSocket调试器
class WebSocketDebugger {
  constructor(ws) {
    this.ws = ws;
    this.messages = [];
  }

  log(type, data) {
    const message = {
      type,
      data,
      timestamp: new Date().toISOString()
    };
    this.messages.push(message);
    console.log('[WebSocket]', type, data);
  }

  exportLogs() {
    return JSON.stringify(this.messages, null, 2);
  }
}
\`\`\`

## 更新历史

- **v1.2.0**: 添加流式响应支持
- **v1.1.0**: 改进认证机制
- **v1.0.0**: 初始版本发布`
      }
    ]
  },
  {
    id: 'troubleshooting',
    title: '故障排除',
    description: '常见问题解决方案和故障排除指南',
    icon: '🔧',
    articles: [
      {
        id: 'common-issues',
        title: '常见问题',
        description: '用户经常遇到的问题及其解决方案',
        category: '故障排除',
        tags: ['问题', '解决', 'FAQ'],
        readTime: '10分钟',
        lastUpdated: '2024-01-15',
        content: `# 常见问题解答

## 连接问题

### Q: 无法连接到AI Partner
**症状**: 页面显示"连接失败"或"连接中..."
**可能原因**:
1. 后端服务未启动
2. 网络连接问题
3. 防火墙阻止
4. 端口被占用

**解决方案**:
1. 检查后端服务状态
   \`\`\`bash
   # 检查后端是否运行
   curl http://localhost:8000/health
   \`\`\`
2. 检查网络连接
   \`\`\`bash
   # 测试连接
   ping localhost
   \`\`\`
3. 检查防火墙设置
4. 更换端口（默认8000）

### Q: WebSocket连接频繁断开
**症状**: 对话过程中连接突然中断
**可能原因**:
1. 网络不稳定
2. 服务器超时
3. 心跳机制异常

**解决方案**:
1. 检查网络稳定性
2. 调整心跳间隔
3. 增加超时时间
4. 实现重连机制

## 性能问题

### Q: 响应速度很慢
**症状**: AI回复需要很长时间
**可能原因**:
1. 服务器负载过高
2. 网络延迟
3. 模型推理时间长

**解决方案**:
1. 检查服务器资源使用情况
2. 优化网络环境
3. 调整模型参数
4. 使用缓存机制

### Q: 内存使用过高
**症状**: 浏览器内存占用持续增长
**可能原因**:
1. 消息历史过多
2. 内存泄漏
3. 大文件处理

**解决方案**:
1. 定期清理对话历史
2. 限制消息数量
3. 检查内存泄漏
4. 优化数据结构

## 功能问题

### Q: AI回复不准确
**症状**: 回答内容与问题不符
**可能原因**:
1. 上下文理解错误
2. 训练数据限制
3. 参数配置不当

**解决方案**:
1. 提供更清晰的问题描述
2. 增加上下文信息
3. 调整温度参数
4. 使用提示工程技巧

### Q: 记忆功能不工作
**症状**: AI不记住之前的信息
**可能原因**:
1. 记忆功能未启用
2. 会话超时
3. 数据存储问题

**解决方案**:
1. 检查记忆设置
2. 延长会话时间
3. 验证数据库连接
4. 手动标记重要信息

## 界面问题

### Q: 页面显示异常
**症状**: 界面元素错位或样式错误
**可能原因**:
1. 浏览器兼容性问题
2. CSS加载失败
3. JavaScript错误

**解决方案**:
1. 更新浏览器版本
2. 清除浏览器缓存
3. 检查控制台错误
4. 禁用浏览器插件

### Q: 移动端适配问题
**症状**: 在手机上显示效果不佳
**可能原因**:
1. 响应式设计问题
2. 触摸事件处理
3. 屏幕适配

**解决方案**:
1. 优化CSS媒体查询
2. 改进触摸交互
3. 测试不同设备
4. 使用移动端框架

## 数据问题

### Q: 数据丢失
**症状**: 之前的对话或设置消失
**可能原因**:
1. 数据未正确保存
2. 缓存清理
3. 数据库问题

**解决方案**:
1. 检查数据保存状态
2. 备份重要数据
3. 验证数据库连接
4. 使用数据恢复工具

### Q: 导入/导出失败
**症状**: 无法导入或导出数据
**可能原因**:
1. 文件格式错误
2. 权限问题
3. 文件大小限制

**解决方案**:
1. 检查文件格式
2. 验证文件权限
3. 压缩大文件
4. 分批处理数据

## 安全问题

### Q: 认证失败
**症状**: 无法登录或访问被拒绝
**可能原因**:
1. 密码错误
2. Token过期
3. 账户被锁定

**解决方案**:
1. 重置密码
2. 刷新Token
3. 联系管理员
4. 检查账户状态

### Q: 权限不足
**症状**: 某些功能无法使用
**可能原因**:
1. 角色权限限制
2. 功能未授权
3. 设置问题

**解决方案**:
1. 检查用户角色
2. 申请相应权限
3. 联系管理员
4. 升级账户类型

## 开发问题

### Q: API调用失败
**症状**: 开发时API请求返回错误
**可能原因**:
1. 参数错误
2. 认证问题
3. 服务器错误

**解决方案**:
1. 检查API文档
2. 验证参数格式
3. 查看错误日志
4. 使用调试工具

### Q: 集成问题
**症状**: 第三方集成不工作
**可能原因**:
1. 版本不兼容
2. 配置错误
3. 接口变更

**解决方案**:
1. 检查版本兼容性
2. 验证配置参数
3. 更新接口文档
4. 使用官方SDK

## 报告问题

### 收集信息
在报告问题时，请提供以下信息：
1. 问题描述
2. 复现步骤
3. 预期结果
4. 实际结果
5. 环境信息（浏览器、操作系统等）
6. 错误日志或截图

### 联系方式
- 邮箱：support@ai-partner.com
- GitHub：https://github.com/ai-partner/issues
- 在线客服：工作日 9:00-18:00

### 问题分类
- **紧急**: 系统无法使用、数据丢失
- **重要**: 核心功能异常、性能问题
- **一般**: 界面问题、使用困难
- **建议**: 功能改进、体验优化

## 预防措施

### 定期维护
1. 清理浏览器缓存
2. 更新软件版本
3. 备份重要数据
4. 检查系统日志

### 监控设置
1. 设置性能监控
2. 配置错误告警
3. 建立日志分析
4. 制定应急预案

### 用户培训
1. 阅读使用文档
2. 参加培训课程
3. 加入用户社区
4. 关注更新公告`
      },
      {
        id: 'performance-optimization',
        title: '性能优化',
        description: '系统性能调优和最佳实践',
        category: '优化指南',
        tags: ['性能', '优化', '调优'],
        readTime: '15分钟',
        lastUpdated: '2024-01-15',
        content: `# 性能优化指南

## 系统性能概览

AI Partner的性能涉及多个方面：
- **响应时间**：AI回复的速度
- **并发处理**：同时处理多个用户请求
- **内存使用**：系统资源占用
- **网络传输**：数据传输效率

## 响应时间优化

### 1. 模型优化
\`\`\`python
# 调整模型参数以提升响应速度
model_config = {
    "temperature": 0.7,        # 降低随机性
    "max_tokens": 1000,        # 限制生成长度
    "top_p": 0.9,              # 核心采样
    "frequency_penalty": 0.1,  # 降低重复性
}
\`\`\`

### 2. 缓存策略
\`\`\`javascript
// 实现智能缓存
class ResponseCache {
  constructor(maxSize = 1000, ttl = 3600000) { // 1小时TTL
    this.cache = new Map();
    this.maxSize = maxSize;
    this.ttl = ttl;
  }

  get(key) {
    const item = this.cache.get(key);
    if (!item) return null;

    if (Date.now() - item.timestamp > this.ttl) {
      this.cache.delete(key);
      return null;
    }

    return item.value;
  }

  set(key, value) {
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }

    this.cache.set(key, {
      value,
      timestamp: Date.now()
    });
  }
}
\`\`\`

### 3. 预计算常用回复
\`\`\`javascript
// 预计算常见问题的回复
const commonResponses = {
  "greeting": [
    "您好！我是AI Partner，很高兴为您服务！",
    "Hi there! How can I help you today?",
    "你好！有什么可以帮助您的吗？"
  ],
  "capabilities": [
    "我可以帮助您进行对话分析、记忆管理和数据可视化。",
    "My capabilities include chat analysis, memory management, and data visualization.",
    "我的功能包括智能对话、知识检索、工具调用等。"
  ]
};

function getCommonResponse(category) {
  const responses = commonResponses[category];
  return responses[Math.floor(Math.random() * responses.length)];
}
\`\`\`

## 并发处理优化

### 1. 连接池管理
\`\`\`python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class ConnectionPool:
    def __init__(self, max_connections=10):
        self.semaphore = asyncio.Semaphore(max_connections)
        self.executor = ThreadPoolExecutor(max_workers=max_connections)

    async def process_request(self, request_data):
        async with self.semaphore:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                self.executor,
                self._process_request,
                request_data
            )

    def _process_request(self, request_data):
        # 实际的请求处理逻辑
        return process_request(request_data)
\`\`\`

### 2. 负载均衡
\`\`\`javascript
// 简单的负载均衡器
class LoadBalancer {
  constructor(servers) {
    this.servers = servers;
    this.current = 0;
  }

  getServer() {
    const server = this.servers[this.current];
    this.current = (this.current + 1) % this.servers.length;
    return server;
  }

  async makeRequest(request) {
    const server = this.getServer();
    try {
      return await server.request(request);
    } catch (error) {
      // 尝试下一个服务器
      return this.makeRequest(request);
    }
  }
}
\`\`\`

### 3. 请求队列
\`\`\`javascript
// 请求队列管理
class RequestQueue {
  constructor(maxConcurrent = 5) {
    this.queue = [];
    this.processing = 0;
    this.maxConcurrent = maxConcurrent;
  }

  async enqueue(request) {
    return new Promise((resolve, reject) => {
      this.queue.push({ request, resolve, reject });
      this.process();
    });
  }

  async process() {
    if (this.processing >= this.maxConcurrent || this.queue.length === 0) {
      return;
    }

    this.processing++;
    const { request, resolve, reject } = this.queue.shift();

    try {
      const result = await this.executeRequest(request);
      resolve(result);
    } catch (error) {
      reject(error);
    } finally {
      this.processing--;
      this.process(); // 处理下一个请求
    }
  }

  async executeRequest(request) {
    // 执行实际请求
    return await request.execute();
  }
}
\`\`\`

## 内存优化

### 1. 消息历史管理
\`\`\`javascript
// 滑动窗口管理消息历史
class MessageHistory {
  constructor(maxSize = 100) {
    this.messages = [];
    this.maxSize = maxSize;
  }

  addMessage(message) {
    this.messages.push(message);

    if (this.messages.length > this.maxSize) {
      // 保留重要的上下文消息
      this.messages = this.messages.slice(-this.maxSize);
    }
  }

  getContext(tokenLimit = 2000) {
    // 从最新消息开始，保留在token限制内的上下文
    let context = [];
    let tokenCount = 0;

    for (let i = this.messages.length - 1; i >= 0; i--) {
      const message = this.messages[i];
      const messageTokens = this.estimateTokens(message.content);

      if (tokenCount + messageTokens > tokenLimit) {
        break;
      }

      context.unshift(message);
      tokenCount += messageTokens;
    }

    return context;
  }

  estimateTokens(text) {
    // 简单的token估算（实际应该使用tokenizer）
    return Math.ceil(text.length / 4);
  }
}
\`\`\`

### 2. 内存监控
\`\`\`javascript
// 内存使用监控
class MemoryMonitor {
  constructor() {
    this.threshold = 100 * 1024 * 1024; // 100MB
    this.checkInterval = 30000; // 30秒
    this.monitor();
  }

  monitor() {
    setInterval(() => {
      const memoryUsage = this.getMemoryUsage();

      if (memoryUsage > this.threshold) {
        this.cleanup();
      }
    }, this.checkInterval);
  }

  getMemoryUsage() {
    if (performance.memory) {
      return performance.memory.usedJSHeapSize;
    }
    return 0;
  }

  cleanup() {
    // 清理策略
    this.clearOldCache();
    this.compressData();
    this.garbageCollect();
  }

  clearOldCache() {
    // 清理过期缓存
  }

  compressData() {
    // 压缩数据结构
  }

  garbageCollect() {
    // 触发垃圾回收
    if (window.gc) {
      window.gc();
    }
  }
}
\`\`\`

## 网络优化

### 1. 请求合并
\`\`\`javascript
// 请求合并器
class RequestBatcher {
  constructor(batchSize = 10, flushInterval = 100) {
    this.batch = [];
    this.batchSize = batchSize;
    this.flushInterval = flushInterval;
    this.flushTimer = null;
  }

  addRequest(request) {
    return new Promise((resolve, reject) => {
      this.batch.push({ request, resolve, reject });

      if (this.batch.length >= this.batchSize) {
        this.flush();
      } else if (!this.flushTimer) {
        this.flushTimer = setTimeout(() => this.flush(), this.flushInterval);
      }
    });
  }

  async flush() {
    if (this.batch.length === 0) return;

    const currentBatch = this.batch;
    this.batch = [];

    if (this.flushTimer) {
      clearTimeout(this.flushTimer);
      this.flushTimer = null;
    }

    try {
      const requests = currentBatch.map(item => item.request);
      const responses = await this.executeBatch(requests);

      currentBatch.forEach((item, index) => {
        item.resolve(responses[index]);
      });
    } catch (error) {
      currentBatch.forEach(item => item.reject(error));
    }
  }

  async executeBatch(requests) {
    // 实现批量请求逻辑
    return await Promise.all(requests.map(req => req.execute()));
  }
}
\`\`\`

### 2. 数据压缩
\`\`\`javascript
// 数据压缩传输
class DataCompressor {
  static compress(data) {
    const jsonString = JSON.stringify(data);
    return this.gzipCompress(jsonString);
  }

  static decompress(compressedData) {
    const jsonString = this.gzipDecompress(compressedData);
    return JSON.parse(jsonString);
  }

  static gzipCompress(str) {
    // 使用CompressionStream API（现代浏览器）
    if ('CompressionStream' in window) {
      const stream = new CompressionStream('gzip');
      return new Response(str).body
        .pipeThrough(stream)
        .then(response => response.arrayBuffer())
        .then(buffer => new Uint8Array(buffer));
    }

    // 降级方案：返回原始数据
    return new TextEncoder().encode(str);
  }

  static gzipDecompress(compressedData) {
    // 使用DecompressionStream API
    if ('DecompressionStream' in window) {
      const stream = new DecompressionStream('gzip');
      return new Response(compressedData).body
        .pipeThrough(stream)
        .then(response => response.text());
    }

    // 降级方案
    return new TextDecoder().decode(compressedData);
  }
}
\`\`\`

## 前端优化

### 1. 虚拟滚动
\`\`\`javascript
// 大列表虚拟滚动
class VirtualScroller {
  constructor(container, itemHeight, renderItem) {
    this.container = container;
    this.itemHeight = itemHeight;
    this.renderItem = renderItem;
    this.visibleItems = Math.ceil(container.clientHeight / itemHeight) + 2;
    this.scrollTop = 0;
    this.data = [];

    this.container.addEventListener('scroll', this.handleScroll.bind(this));
  }

  setData(data) {
    this.data = data;
    this.render();
  }

  handleScroll() {
    this.scrollTop = this.container.scrollTop;
    this.render();
  }

  render() {
    const startIndex = Math.floor(this.scrollTop / this.itemHeight);
    const endIndex = Math.min(startIndex + this.visibleItems, this.data.length);

    const fragment = document.createDocumentFragment();

    for (let i = startIndex; i < endIndex; i++) {
      const item = this.renderItem(this.data[i], i);
      item.style.position = 'absolute';
      item.style.top = i * this.itemHeight + 'px';
      fragment.appendChild(item);
    }

    this.container.innerHTML = '';
    this.container.appendChild(fragment);
    this.container.style.height = this.data.length * this.itemHeight + 'px';
  }
}
\`\`\`

### 2. 懒加载
\`\`\`javascript
// 图片懒加载
class LazyImageLoader {
  constructor() {
    this.observer = new IntersectionObserver(
      this.handleIntersection.bind(this),
      { rootMargin: '50px' }
    );
  }

  observe(img) {
    this.observer.observe(img);
  }

  handleIntersection(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        const src = img.dataset.src;

        if (src) {
          img.src = src;
          img.removeAttribute('data-src');
          this.observer.unobserve(img);
        }
      }
    });
  }
}
\`\`\`

## 监控和分析

### 1. 性能指标收集
\`\`\`javascript
// 性能监控
class PerformanceMonitor {
  constructor() {
    this.metrics = {
      responseTime: [],
      memoryUsage: [],
      errorRate: 0,
      requestCount: 0
    };
  }

  recordResponseTime(duration) {
    this.metrics.responseTime.push(duration);

    // 保持最近1000条记录
    if (this.metrics.responseTime.length > 1000) {
      this.metrics.responseTime.shift();
    }
  }

  getAverageResponseTime() {
    const times = this.metrics.responseTime;
    return times.length > 0
      ? times.reduce((sum, time) => sum + time, 0) / times.length
      : 0;
  }

  getPercentileResponseTime(percentile = 95) {
    const times = [...this.metrics.responseTime].sort((a, b) => a - b);
    const index = Math.ceil(times.length * percentile / 100) - 1;
    return times[index] || 0;
  }

  generateReport() {
    return {
      avgResponseTime: this.getAverageResponseTime(),
      p95ResponseTime: this.getPercentileResponseTime(95),
      p99ResponseTime: this.getPercentileResponseTime(99),
      errorRate: this.metrics.errorRate,
      totalRequests: this.metrics.requestCount
    };
  }
}
\`\`\`

### 2. 实时监控面板
\`\`\`javascript
// 实时监控面板
class MonitoringDashboard {
  constructor() {
    this.chart = null;
    this.initChart();
    this.startRealTimeUpdates();
  }

  initChart() {
    const ctx = document.getElementById('performance-chart').getContext('2d');
    this.chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: [],
        datasets: [{
          label: '响应时间 (ms)',
          data: [],
          borderColor: 'rgb(75, 192, 192)',
          tension: 0.1
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
  }

  startRealTimeUpdates() {
    setInterval(() => {
      const metrics = this.collectMetrics();
      this.updateChart(metrics);
    }, 5000); // 每5秒更新一次
  }

  collectMetrics() {
    return {
      timestamp: new Date(),
      responseTime: this.getCurrentResponseTime(),
      memoryUsage: this.getCurrentMemoryUsage(),
      activeConnections: this.getActiveConnections()
    };
  }

  updateChart(metrics) {
    const chart = this.chart;
    chart.data.labels.push(metrics.timestamp.toLocaleTimeString());
    chart.data.datasets[0].data.push(metrics.responseTime);

    // 保持最近30个数据点
    if (chart.data.labels.length > 30) {
      chart.data.labels.shift();
      chart.data.datasets[0].data.shift();
    }

    chart.update();
  }
}
\`\`\`

## 最佳实践

### 1. 代码优化
- 使用异步编程避免阻塞
- 避免不必要的DOM操作
- 合理使用缓存策略
- 及时清理资源

### 2. 架构设计
- 微服务架构提高可扩展性
- 消息队列处理高并发
- 负载均衡分散压力
- 监控系统及时发现问题

### 3. 用户体验
- 提供加载状态反馈
- 实现优雅降级
- 优化首屏加载时间
- 减少不必要的网络请求

### 4. 测试策略
- 进行性能基准测试
- 压力测试验证稳定性
- A/B测试优化用户体验
- 持续监控性能指标`
      }
    ]
  }
];

const DocumentationPage: React.FC = () => {
  const [selectedSection, setSelectedSection] = useState<DocumentationSection | null>(null);
  const [selectedArticle, setSelectedArticle] = useState<DocumentationArticle | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());

  // 搜索功能
  const searchArticles = useCallback((query: string) => {
    if (!query.trim()) return [];

    const results: DocumentationArticle[] = [];
    const lowerQuery = query.toLowerCase();

    DOCUMENTATION_SECTIONS.forEach(section => {
      section.articles.forEach(article => {
        if (
          article.title.toLowerCase().includes(lowerQuery) ||
          article.description.toLowerCase().includes(lowerQuery) ||
          article.content.toLowerCase().includes(lowerQuery) ||
          article.tags.some(tag => tag.toLowerCase().includes(lowerQuery))
        ) {
          results.push(article);
        }
      });
    });

    return results;
  }, []);

  const searchResults = searchQuery ? searchArticles(searchQuery) : [];

  // 切换章节展开状态
  const toggleSection = useCallback((sectionId: string) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sectionId)) {
        newSet.delete(sectionId);
      } else {
        newSet.add(sectionId);
      }
      return newSet;
    });
  }, []);

  // 选择文章
  const selectArticle = useCallback((article: DocumentationArticle) => {
    setSelectedArticle(article);
    setSelectedSection(null);
    logger.info(`查看文档: ${article.title}`, 'DocumentationPage');
  }, []);

  // 渲染Markdown内容
  const renderMarkdown = (content: string) => {
    // 简单的Markdown渲染（实际项目中应使用专业的Markdown库）
    return content
      .replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold mb-4">$1</h1>')
      .replace(/^## (.*$)/gm, '<h2 class="text-xl font-semibold mb-3 mt-6">$1</h2>')
      .replace(/^### (.*$)/gm, '<h3 class="text-lg font-medium mb-2 mt-4">$1</h3>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code class="bg-gray-100 dark:bg-gray-700 px-1 py-0.5 rounded text-sm">$1</code>')
      .replace(/```(.*?)```/gs, '<pre class="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg overflow-x-auto"><code>$1</code></pre>')
      .replace(/^\- (.*$)/gm, '<li class="ml-4">• $1</li>')
      .replace(/^\d+\. (.*$)/gm, '<li class="ml-4">$1</li>')
      .replace(/\n\n/g, '</p><p class="mb-4">')
      .replace(/^\d+\. (.*$)/gm, '<li class="ml-4 list-decimal">$1</li>')
      .replace(/^\* (.*$)/gm, '<li class="ml-4 list-disc">$1</li>');
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 页面标题 */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            帮助文档
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            AI Partner完整的使用指南和技术文档
          </p>
        </div>

        {/* 搜索栏 */}
        <div className="mb-8">
          <div className="max-w-2xl mx-auto">
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="搜索文档..."
                className="w-full px-4 py-3 pl-10 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <div className="absolute left-3 top-3.5 text-gray-400">
                🔍
              </div>
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-3.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  ✕
                </button>
              )}
            </div>
          </div>
        </div>

        {/* 搜索结果 */}
        {searchQuery && searchResults.length > 0 && (
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              搜索结果 ({searchResults.length})
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {searchResults.map((article) => (
                <div
                  key={article.id}
                  onClick={() => selectArticle(article)}
                  className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 hover:shadow-lg transition-shadow cursor-pointer"
                >
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                    {article.title}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                    {article.description}
                  </p>
                  <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                    <span>{article.category}</span>
                    <span>{article.readTime}</span>
                  </div>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {article.tags.map((tag) => (
                      <span
                        key={tag}
                        className="px-2 py-1 text-xs bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 rounded"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {!searchQuery && (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            {/* 侧边栏 */}
            <div className="lg:col-span-1">
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  文档目录
                </h2>
                <div className="space-y-2">
                  {DOCUMENTATION_SECTIONS.map((section) => (
                    <div key={section.id}>
                      <button
                        onClick={() => toggleSection(section.id)}
                        className="w-full flex items-center justify-between p-3 text-left hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors"
                      >
                        <div className="flex items-center space-x-2">
                          <span className="text-lg">{section.icon}</span>
                          <span className="font-medium text-gray-900 dark:text-white">
                            {section.title}
                          </span>
                        </div>
                        <span className="text-gray-400">
                          {expandedSections.has(section.id) ? '▼' : '▶'}
                        </span>
                      </button>

                      {expandedSections.has(section.id) && (
                        <div className="ml-8 mt-2 space-y-1">
                          {section.articles.map((article) => (
                            <button
                              key={article.id}
                              onClick={() => selectArticle(article)}
                              className="w-full text-left p-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-700 rounded transition-colors"
                            >
                              {article.title}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* 主内容区 */}
            <div className="lg:col-span-3">
              {!selectedArticle && !selectedSection && (
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8">
                  <div className="text-center">
                    <div className="text-6xl mb-4">📚</div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                      欢迎使用AI Partner文档
                    </h2>
                    <p className="text-gray-600 dark:text-gray-400 mb-8">
                      选择左侧的文档章节开始阅读，或使用搜索功能快速找到所需内容
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {DOCUMENTATION_SECTIONS.slice(0, 3).map((section) => (
                        <button
                          key={section.id}
                          onClick={() => setSelectedSection(section)}
                          className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-md transition-shadow"
                        >
                          <div className="text-2xl mb-2">{section.icon}</div>
                          <div className="font-medium text-gray-900 dark:text-white">
                            {section.title}
                          </div>
                          <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                            {section.articles.length} 篇文章
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* 章节概览 */}
              {selectedSection && !selectedArticle && (
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8">
                  <button
                    onClick={() => setSelectedSection(null)}
                    className="mb-4 text-blue-600 dark:text-blue-400 hover:underline"
                  >
                    ← 返回文档目录
                  </button>
                  <div className="flex items-center space-x-3 mb-6">
                    <span className="text-3xl">{selectedSection.icon}</span>
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                        {selectedSection.title}
                      </h2>
                      <p className="text-gray-600 dark:text-gray-400">
                        {selectedSection.description}
                      </p>
                    </div>
                  </div>
                  <div className="space-y-4">
                    {selectedSection.articles.map((article) => (
                      <div
                        key={article.id}
                        onClick={() => selectArticle(article)}
                        className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-md transition-shadow cursor-pointer"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                              {article.title}
                            </h3>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                              {article.description}
                            </p>
                            <div className="flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
                              <span>{article.category}</span>
                              <span>{article.readTime}</span>
                              <span>{article.lastUpdated}</span>
                            </div>
                            <div className="flex flex-wrap gap-1 mt-2">
                              {article.tags.map((tag) => (
                                <span
                                  key={tag}
                                  className="px-2 py-1 text-xs bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 rounded"
                                >
                                  {tag}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 文章内容 */}
              {selectedArticle && (
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
                  <div className="p-8">
                    <button
                      onClick={() => setSelectedArticle(null)}
                      className="mb-4 text-blue-600 dark:text-blue-400 hover:underline"
                    >
                      ← 返回
                    </button>
                    <div className="mb-6">
                      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
                        {selectedArticle.title}
                      </h1>
                      <p className="text-gray-600 dark:text-gray-400 mb-4">
                        {selectedArticle.description}
                      </p>
                      <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                        <span>{selectedArticle.category}</span>
                        <span>{selectedArticle.readTime}</span>
                        <span>最后更新: {selectedArticle.lastUpdated}</span>
                      </div>
                      <div className="flex flex-wrap gap-1 mt-2">
                        {selectedArticle.tags.map((tag) => (
                          <span
                            key={tag}
                            className="px-2 py-1 text-xs bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 rounded"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div
                      className="prose prose-gray dark:prose-invert max-w-none"
                      dangerouslySetInnerHTML={{
                        __html: renderMarkdown(selectedArticle.content)
                      }}
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentationPage;