# AI Partner Frontend

基于React 18和TypeScript的现代化前端应用，用于展示AI Partner智能体的核心功能。

## 🚀 技术栈

- **React 18** - 用户界面框架
- **TypeScript** - 类型安全的JavaScript
- **Vite** - 快速构建工具
- **Tailwind CSS** - 现代化样式框架
- **Zustand** - 轻量级状态管理
- **React Query** - 服务端状态管理
- **React Router** - 客户端路由
- **D3.js** - 数据可视化
- **Recharts** - 图表库

## 📦 依赖安装

```bash
# 使用npm
npm install

# 使用yarn
yarn install

# 使用pnpm
pnpm install
```

## 🛠️ 开发环境

```bash
# 启动开发服务器
npm run dev

# 类型检查
npm run type-check

# 代码检查
npm run lint
```

## 🏗️ 构建部署

```bash
# 构建生产版本
npm run build

# 预览构建结果
npm run preview
```

## 📁 项目结构

```
src/
├── components/          # 可复用组件
│   ├── Layout/         # 布局组件
│   ├── Chat/           # 对话相关组件
│   ├── Visualization/  # 可视化组件
│   └── ...            # 其他组件
├── pages/              # 页面组件
├── hooks/              # 自定义hooks
├── services/           # API服务
├── stores/             # Zustand状态管理
├── utils/              # 工具函数
├── types/              # TypeScript类型定义
└── styles/             # 样式文件
```

## 🎨 样式系统

- 使用Tailwind CSS进行样式开发
- 支持明暗主题切换
- 响应式设计，适配移动端和桌面端
- 自定义设计系统和组件库

## 🔧 环境配置

复制`.env.example`为`.env`并配置相关环境变量：

```bash
cp .env.example .env
```

主要配置项：

- `VITE_API_BASE_URL` - 后端API地址
- `VITE_WS_URL` - WebSocket连接地址
- `VITE_ENABLE_ANALYTICS` - 是否启用数据分析
- `VITE_SHOW_DEVTOOLS` - 是否显示开发工具

## 🌐 功能特性

### 核心功能

- **个性化对话** - 基于用户画像的智能对话体验
- **实时可视化** - LangGraph状态流程实时展示
- **记忆网络** - 对话历史和知识关联可视化
- **对比分析** - 技术对比和性能分析
- **演示指南** - 引导式功能演示

### 技术特性

- **TypeScript支持** - 完整的类型安全
- **状态管理** - Zustand + React Query
- **实时通信** - WebSocket连接
- **错误处理** - 全局错误边界和重试机制
- **性能优化** - 代码分割和懒加载

## 📱 页面路由

- `/` - 首页概览
- `/demo` - 功能演示
- `/chat` - 智能对话
- `/visualization` - 数据可视化
- `/comparison` - 对比分析
- `/settings` - 系统设置

## 🔌 API集成

项目集成了完整的API服务层：

- **对话API** - 消息发送和状态获取
- **画像API** - 用户画像管理
- **记忆API** - 记忆网络数据
- **知识API** - 知识检索和搜索
- **分析API** - 对比分析和性能数据

## 🎯 开发指南

### 添加新页面

1. 在`src/pages/`创建页面组件
2. 在`App.tsx`中添加路由
3. 在`Header.tsx`中添加导航项

### 添加新组件

1. 在`src/components/`对应目录创建组件
2. 使用TypeScript定义Props类型
3. 遵循项目设计规范
4. 添加Storybook文档（如需要）

### 状态管理

- 使用Zustand管理客户端状态
- 使用React Query管理服务端状态
- 遵循单一数据源原则

### 样式规范

- 使用Tailwind CSS类名
- 遵循响应式设计原则
- 支持明暗主题
- 使用组件变体系统

## 🧪 测试

```bash
# 运行单元测试
npm test

# 运行集成测试
npm run test:integration

# 生成测试覆盖率报告
npm run test:coverage
```

## 📦 部署

### Docker部署

```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 环境变量

生产环境需要配置以下环境变量：

```bash
VITE_API_BASE_URL=https://api.aipartner.com/api
VITE_WS_URL=wss://api.aipartner.com/ws
VITE_ENABLE_ANALYTICS=true
VITE_SHOW_DEVTOOLS=false
```

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 支持

- 📧 邮箱: support@aipartner.com
- 📖 文档: https://docs.aipartner.com
- 💬 讨论: https://github.com/aipartner/discussions

---

Made with ❤️ by AI Partner Team