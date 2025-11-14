## 路由总览与初步判定
- 系统：`/`、`/health`、`/api/health` → 可用端点，返回静态健康信息与环境概览（app/main.py:162–195）。
- WebSocket：`/ws` → 明确使用模拟回应（app/main.py:295–316）。
- Chat：`/api/chat/*`（app/api/chat.py）
  - `POST /api/chat/` → 计划走真实 AIPartner 服务，失败则回退模拟（chat.py:69–107，返回真实或模拟）。真实调用路径：`AIPartnerService.chat`（app/utils/ai_partner.py:109–147）；回退模拟：`MockAIPartner.chat`（app/utils/ai_partner.py:220–258）。
  - `GET /api/chat/state/{session_id}`、`GET /api/chat/history`、`GET/DELETE /api/chat/sessions*` → 本地会话持久化（真实本地功能），不依赖外部 LLM（chat.py:142–552）。
  - `POST /api/chat/search` → 真实（agent.vector_store）或模拟回退（chat.py:312–340；真实路径 ai_partner.py:196–208）。
  - `POST /api/chat/tools/execute` → 明确模拟（TODO 占位）（chat.py:388–416）。
- Persona：`/api/persona/*` → 明确模拟数据（app/api/persona.py:33–71、88–117、138–163、179–205、215–248、266–312、329–388）。
- Memory：`/api/memory/*` → 明确模拟数据与本地结构（app/api/memory.py:72–88、110–144、164–199、225–248、266–285、304–325、350–407、427–455）。
- Knowledge：`/api/knowledge/*` → 明确模拟数据（app/api/knowledge.py:73–89、105–142、165–203、219–245、267–313、331–350、368–390、413–429、439–465）。
- Settings：`/api/settings/*` → 配置读取/写入真实（env 与 settings），模型校验会尝试真实远端，失败回退列表（app/api/settings.py:14–22、73–109、110–128、130–153、154–170）。
- 配置与切换依据：env `ZHIPU_API_KEY`、`ZHIPU_BASE_URL`、`ZHIPU_MODEL` 已加载（start 日志），AIPartnerAgent 存在（agents/partner_agent.py）。`AIPartnerService` 初始化成功则走真实（ai_partner.py:80–88、347–353）。

## 判定规则
- 真实调用判据：
  - `POST /api/chat/` 返回体 `data.metadata.agent_type == "real"`（ai_partner.py:137–147）。
  - `POST /api/chat/search` 返回来源不含 `mock_database`（ai_partner.py:196–205）；如为模拟，`metadata.source == mock_database`（ai_partner.py:283–291）。
  - `POST /api/settings/validate` 返回 `valid: true` 且模型列表来自远端（settings.py:154–170）。
- 模拟判据：
  - 明确 TODO/模拟分支的端点（Persona/Memory/Knowledge/Tools）。
  - WebSocket 文本拼接回应（main.py:302–316）。
- 本地真实功能：
  - 会话管理/历史等使用 `session_persistence`（不依赖外部 LLM）。

## 执行验证步骤
1. 系统健康：`GET /api/health`，记录状态与时间戳。
2. Chat 对话：`POST /api/chat/` 用样例消息（含/不含关键词），检查 `metadata.agent_type` 与响应内容。
3. Chat 语义搜索：`POST /api/chat/search`，检查结果是否来自真实向量库或模拟。
4. 会话接口：创建、列出、删除，验证真实本地持久化行为与分页。
5. Persona 全量：调用 context/user/ai/analysis/templates/validate/export，确认均为模拟。
6. Memory 全量：调用 stats/sessions/turns/search/delete/cleanup/network/export，确认模拟与数据形态。
7. Knowledge 全量：调用 stats/search/documents/detail/upload/delete/rebuild/similar/tags，确认模拟与参数约束。
8. Settings：`GET /api/settings/config` 检查 env/source；`POST /api/settings/validate` 校验远端有效性；`PUT /api/settings/model|config` 验证写入（仅在您确认后执行）。
9. WebSocket：建立连接，发送 `message/ping`，确认模拟回应与心跳（仅在您确认后执行）。
10. 汇总报告：生成每个端点的“真实/模拟/本地真实”结论与证据（返回样例、日志要点、代码引用）。

## 交付内容
- API 清单与分类矩阵（端点 → 真实/模拟/本地真实）。
- 样例请求与响应摘录（含关键字段/判据）。
- 发现的问题与改进建议（如 `is_available()` 与 `AIPartnerService` 的接口一致性）。
- 后续可选：逐步将 Knowledge/Memory/Persona 从模拟替换为真实实现的路线图。