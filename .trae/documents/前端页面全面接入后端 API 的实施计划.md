## 目标

- 以现有后端 API 为唯一数据源，完善并联通前端全部页面与状态管理。
- 统一网络层与响应解析，接入 WebSocket 实时更新，保证交互与可视化完整可用。
- 完成端到端联调与验证，确保主要用户路径稳定。

## 全局改造

- 网络层统一
- 在 `src/services/api.ts` 保持 `baseURL=/api`，所有请求返回均解析 `success` 与 `data`；对分页响应读取 `data` 与 `pagination`。
- 新增数据适配器：为分页类接口（记忆会话、知识文档列表）返回 `{items, pagination}`，避免页面散落解析。
- 错误处理与提示
- 使用 `react-hot-toast` 在 `api.ts` 的响应拦截器中对 `success=false` 或 HTTP 非 2xx 统一弹出错误提示；对 `401/429` 进行特定提示。
- 类型与数据对齐
- 在 `src/types/index.ts` 增加后端包装响应类型声明：`PaginatedResponse<T>`；为聊天、画像、记忆、知识、演示结果各自扩展补齐字段；页面通过类型收敛减少断言错误。
- WebSocket 实时更新
- 维持 `vite.config.ts` 的 `'/ws'` 代理；`websocket.ts` 默认拼接 `ws://<host>/ws`；将心跳、订阅、断线重连状态反馈到全局 Store。
- 全局 Store
- 用 `zustand` 的 `useAppStore` 提供全局 `loading` 与 `notifications`；`useChatStore` 维护聊天历史、当前会话 ID、上下文摘要、执行路径等。

## 页面接入细化

### ChatPage

- 目标：发起对话、查看状态、展示历史、工具调用、搜索结合可视化简述。
- 接口映射：
- 发送消息：`POST /api/chat/` → `apiService.sendMessage`
- 会话状态：`GET /api/chat/state/{session_id}` → `apiService.getChatState`
- 历史记录：`GET /api/chat/history?session_id=&limit=&offset=` → 新增 `apiService.get('/chat/history', params)`
- 工具调用：`POST /api/chat/tools/execute` → `apiService.post`
- 搜索：`POST /api/chat/search` → `apiService.searchKnowledge`
- 实时：WebSocket 订阅 `subscribe_session`，显示 `state_update/message_update/memory_update`
- UI：
- 输入框与发送按钮，LoadingSpinner 包裹；右侧状态卡片显示 `current_turn/active_tools/context_summary`
- 历史列表分页加载，支持 `next_offset`；错误提示统一 toast

### VisualizationPage

- 目标：展示记忆网络节点与边、中心主题与密度等。
- 接口映射：
- `GET /api/memory/network?session_id=&depth=` 与别名 `GET /api/memory/network/{session_id}` → `apiService.get('/memory/network', params)`
- UI：
- 使用 `d3` 或 `recharts` 绘制力导图/网络图；侧栏显示 `metadata.total_nodes/total_edges/network_density`
- 支持 sessionId 输入选择与深度切换；错误 toast

### DemoPage

- 目标：展示演示场景列表、详情与运行结果。
- 接口映射：
- 场景列表：`GET /api/demo/scenarios`
- 场景详情：`GET /api/demo/scenarios/{id}`
- 运行演示：`POST /api/demo/run/{id}`
- 额外：模板与示例数据：`GET /api/demo/templates`、`GET /api/demo/samples`
- UI：
- 列表卡片筛选（category/difficulty）；详情弹窗展示步骤与学习目标；运行按钮显示结果输出与生成文件列表

### ComparisonPage

- 目标：对比分析 LangGraph 与基线配置，显示差异与评分。
- 接口映射：
- `POST /api/comparison/analyze`（别名已添加）→ `apiService.analyzeComparison`
- UI：
- 表单收集 baseline/target/comparison_type/metrics；结果面板展示 `differences/similarities/performance_metrics/overall_score`
- 错误 toast 与表单校验

### SettingsPage

- 目标：画像管理与验证、导出。
- 接口映射：
- 获取画像上下文：`GET /api/persona/context`
- 更新画像：`POST /api/persona/update`
- 用户画像/AI画像：`GET /api/persona/user`、`GET /api/persona/ai`
- 验证画像：`POST /api/persona/validate?persona_type=user|ai`（Body 为画像字段）
- UI：
- 表单编辑画像属性（name/role/expertise_areas/...）；提交后显示更新字段与成功提示；验证结果显示 `completeness_score/missing_fields`
- 可选导出：调用 `/api/persona/export`（若页面需要）并生成下载链接

### HomePage

- 目标：总体健康与统计总览。
- 接口映射：
- 健康：`GET /api/health`
- 记忆统计：`GET /api/memory/stats`
- 知识库统计：`GET /api/knowledge/stats`
- UI：
- 仪表卡片显示各服务状态与概览；点击卡片跳转至相应页面（Visualization/Knowledge）

## 代码改动清单（前端）

- `src/services/api.ts`
- 添加 `getPaginated<T>(url, params)` 与数据适配器；为聊天历史与文档列表复用
- `src/hooks/useApiQuery.ts`
- 提供统一的 `useQuery` 包装，自动处理 `success=false`；支持分页参数与依赖键
- `src/hooks/useWebSocket.ts`
- 增加会话订阅入口与连接状态 UI 回调；默认 `autoConnect=false`，在 ChatPage 根据 `sessionId` 决定
- `src/stores/useChatStore.ts`
- 加入 `sessionId`, `history`, `state`, `sendMessage`, `loadHistory`，与 API 整合
- `src/pages/*.tsx`
- ChatPage/VisualizationPage/DemoPage/ComparisonPage/SettingsPage/HomePage 依次接入 API，完善 UI 与交互；所有请求以 `apiService` 为唯一入口

## 验证与联调

- 本地运行：启动后端 `:8000` 与前端 `:3000`；检查代理 `/api` 与 `/ws` 可用
- 冒烟用例：
- Chat：发送消息→状态更新→历史分页→工具执行→搜索→WebSocket 收到 `state_update`
- Visualization：输入 `sessionId` 加载网络图；切换 `depth`
- Demo：获取场景→查看详情→运行→查看结果列表
- Comparison：提交表单→显示差异与评分
- Settings：加载画像→编辑并更新→调用验证显示完整度
- Home：健康卡片与统计卡片均正确显示
- 自动化：保留页面内轻量 `vitest` 或组件测试（如列表渲染与错误提示）

## 交付物

- 前端页面完整联通后端，统一错误与加载状态；WebSocket 实时更新接入；数据类型与响应一致。
- 提供简要使用文档（README 段落或页面内引导）。

## 风险与回退

- 若某接口结构差异影响渲染，先在 `apiService` 适配数据后再考虑调整后端；避免破坏已有前端类型。
- WebSocket 在部分网络环境下断连重试，前端已指数退避；如仍异常，临时降级为轮询（在 `useWebSocket` 中开关）。

## 计划排期

- 第 1 阶段：网络层、类型与 Store（0.5 天）
- 第 2 阶段：Chat/Visualization 接入（0.5 天）
- 第 3 阶段：Demo/Comparison 接入（0.5 天）
- 第 4 阶段：Settings/Home 接入（0.5 天）
- 第 5 阶段：联调与修复（0.5 天）

请确认计划，确认后我将按上述步骤直接在前端代码中实现与联通。