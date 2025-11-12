## 概述

* 后端位于 `f:\person\3-数字化集锦\LangGraph\demo\web_interface\backend`

* 前端位于 `f:\person\3-数字化集锦\LangGraph\demo\web_interface\frontend`

* 开发模式：后端 `8000` 端口，前端 `3000` 端口，前端通过代理转发到后端。

## 后端启动

* 激活虚拟环境（项目已存在 venv）：

  * `f:\person\3-数字化集锦\LangGraph\venv\Scripts\activate`

* 进入后端目录：

  * `cd f:\person\3-数字化集锦\LangGraph\demo\web_interface\backend`

* 配置环境变量文件 `.env`（必须包含 `ZHIPU_API_KEY`）：

  * 若存在示例，复制并编辑：`copy .env.example .env`

  * 必填键值参考 `app/core/config.py`（见 `demo/web_interface/backend/app/core/config.py:27`）

* 安装依赖（如已安装可跳过）：

  * `pip install -r requirements.txt`

* 启动开发服务（二选一）：

  * 使用统一脚本：`python run.py dev`

  * 或直接启动：`python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

* 说明：后端根路由与健康检查见 `demo/web_interface/backend/app/main.py:158` 与 `demo/web_interface/backend/app/main.py:172`；默认端口与文档输出见 `demo/web_interface/backend/app/main.py:237`。

## 前端启动

* 进入前端目录：

  * `cd f:\person\3-数字化集锦\LangGraph\demo\web_interface\frontend`

* 安装依赖：

  * `npm install`

* 启动开发服务：

  * `npm run dev`

* 前端代理配置：`/api -> http://localhost:8000`（见 `demo/web_interface/frontend/vite.config.ts:23` 与 `demo/web_interface/frontend/vite.config.ts:24`）

* API 基址默认为 `/api`（见 `demo/web_interface/frontend/src/services/api.ts:21`），无需额外配置即可调用后端。

## 验证

* 打开前端：`http://localhost:3000`

* 检查后端健康：`http://localhost:8000/health`（见 `demo/web_interface/backend/app/main.py:172`）

* 查看 API 文档（开发模式开启时）：`http://localhost:8000/docs`（见 `demo/web_interface/backend/app/main.py:66` 与 `demo/web_interface/backend/app/main.py:235`）

* 在前端页面执行一次对话，观察网络请求是否命中 `/api/chat/`。

## 常见问题

* 缺少 `OPENAI_API_KEY`：后端会报错，按后端目录下 `.env` 填写后重启。

* 依赖缺失：确保在激活虚拟环境后执行 `pip install -r requirements.txt`。

* 端口占用：若 `8000` 或 `3000` 已被占用，分别改为 `--port 8001` 或在 `vite.config.ts` 修改 `server.port`。

* 跨域问题：后端默认允许 `localhost:3000`（见 `demo/web_interface/backend/app/core/config.py:21`）。如需不同来源，在 `.env` 设置 `CORS_ORIGINS`。

## 下一步（可选）

* 使用 `python run.py test` 运行后端测试（目录 `backend/tests`）。

* 如需生产模式，使用 `python run.py prod` 并在反向代理或同域部署下提供前端构建产物（`npm run build` 后的 `dist/`）。

