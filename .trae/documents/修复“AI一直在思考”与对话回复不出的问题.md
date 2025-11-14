## 问题综述
- 前端在聊天页发送消息后，指示“正在思考”卡住，实际回复不出。
- 关键根因是“协议/实现不匹配”：前端对 HTTP 要求 SSE 流式解析，但后端 `POST /api/chat/` 返回普通 JSON；此外前端流式解析代码使用了 Node 流 API，不适用于浏览器环境。
- WebSocket 正常路径会收到 `message_response` 并结束“思考”，但在连接失败或被降级时前端转到 HTTP 流式分支，导致 Promise 不结束，UI 一直处于“思考”。

## 关键证据（代码定位）
- 后端 WebSocket：收到 `type: "message"` 会回 `type: "message_response"`（backend/app/main.py:295–314）。
- 后端 Chat API：`POST /api/chat/` 返回普通 JSON，无 SSE（backend/app/api/chat.py:37–51, 69–101, 126–134）。
- 前端聊天页：WebSocket 成功走 `message_response`，否则走 HTTP 流式（frontend/src/pages/ChatPage.tsx:227–271；思考状态设置与清理在175–190, 284–289）。
- 前端 HTTP 流式实现：基于 Axios `responseType: 'stream'` 和 `stream.on('data')`，这是 Node 写法，浏览器不可用（frontend/src/services/api.ts:90–171）。
- 降级通道：Fallback 发送 `chat_message` 并仅发 `message_update`，聊天页只监听 `message_response`（frontend/src/utils/websocketFallback.ts:159–166, 217–224；frontend/src/pages/ChatPage.tsx:98–125）。
- 类型不一致：TS 端 `ChatResponse` 期待 `message/usage` 等；后端模型为 `response/metadata`（frontend/src/types/index.ts:51–68 vs backend/app/models/chat.py:29–39）。

## 可能原因清单
- HTTP/SSE 协议不匹配：前端期望 SSE 事件 `message/complete`，后端没有实现 SSE；Promise 不结束，UI 卡在“思考”。
- 流式解析方式错误：浏览器环境下用 Axios+Node 流 `.on('data')` 不可用，导致无法触发 `onChunk/end`。
- WebSocket 降级路径事件不匹配：Fallback 发 `message_update` 而不是 `message_response`，聊天页因此不落地回复。
- 消息类型不一致：文档/降级示例用 `chat_message`，真实通道使用 `message`；混用时后端不回响应或前端不处理。
- 类型结构不一致：后端 `ChatResponse.response`，前端期望 `message/usage`；即便非流式走 JSON，也无法按预期渲染元数据。
- 环境/路由：`VITE_API_BASE_URL` 默认 `/api`；代理正常，但若使用非 3000 源或未匹配 CORS，HTTP 可能失败，前端转流式分支后卡住（backend/app/core/config.py:21）。
- 心跳与连接质量：WebSocket 心跳 `ping/pong`（backend/app/main.py:271, 286–293, 381–404）；若客户端未按预期回 `pong` 或连接质量差，可能频繁降级到 HTTP 流式分支。

## 修复方案（分阶段）
### 阶段1：快速止血（保证能出回复）
1. 前端聊天页改为：
   - 连接成功时始终走 WebSocket；失败时走 HTTP 非流式（普通 JSON）。
   - 仅在确认 SSE 可用时才开启流式；否则用一次性 JSON 并直接把 `response/ai_response` 写入 AI 消息内容。
2. 聊天页监听事件扩展为同时处理 `message_response` 与 `message_update`（兼容 Fallback）。
3. 在 HTTP 非流式分支，使用返回的正文字段（后端当前为 `response`）更新 AI 消息内容，并落地“思考”关闭。

### 阶段2：协议对齐（消除根因）
1. 后端 `/api/chat/` 增加 SSE/StreamingResponse：
   - 事件：`event: message`（含 `{type:'stream', content:'...'}`）、`event: complete`（含最终汇总）。
   - 保持现有 JSON 路径以兼容非流式客户端。
2. 前端 `apiService.sendMessage` 改为浏览器友好的流式实现：
   - 用 `EventSource` 或 `fetchReadableStream` 解析 SSE/ReadableStream；移除 Node 流 API。
3. 统一消息类型：
   - 全面采用 `type: 'message'`；弃用 `chat_message`。
   - Fallback 发 `message_response`（或前端统一兼容两者）。
4. 对齐响应模型：
   - TS `ChatResponse` 增加 `response/metadata` 兼容；或在 `apiService` 做字段映射到 `message/usage`。

### 阶段3：验证与稳健性
1. 打通本地端到端：
   - 打开聊天页，观察 WebSocket 正常收到 `message_response`；断网或关 WS 验证 HTTP 非流式仍能回复。
2. 前端加空值保护：
   - `usage/metadata` 缺失时不影响 UI；避免 `undefined` 访问。
3. 后端加日志与状态接口校验：
   - 通过 `/api/chat/state/{session_id}` 验证会话活跃与组件连接状态（backend/app/api/chat.py:142–198）。
4. 测试与脚本：
   - 运行现有 `test_websocket.html` 验证 WS；`test_api.py`/`test_websocket.py` 验证接口与稳态。

## 交付内容
- 前端：修正聊天页发送/接收逻辑、流式实现替换、事件兼容、类型映射。
- 后端：为 `/api/chat/` 增加可选 SSE 流式响应，保持 JSON 兼容；统一 WS 消息类型与订阅占位实现。
- 验证报告：包含关键路径日志、网络面板抓包、接口返回示例与失败回退验证。

请确认以上方案，确认后我将开始实施并逐步验证。