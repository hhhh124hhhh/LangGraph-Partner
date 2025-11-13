# AI Partner 后端启动脚本使用说明

## 功能说明

`start_ai_partner.py` 是一个统一的后端启动脚本，提供以下功能：

1. **自动虚拟环境管理**：自动检测、创建和使用虚拟环境
2. **依赖管理**：自动安装所需依赖包
3. **环境变量加载**：自动加载 `.env` 文件中的环境变量
4. **服务启动**：支持开发和生产环境的服务启动
5. **健康检查**：提供服务健康状态检查功能

## 使用方法

### 基本命令

```bash
# 启动开发环境
python start_ai_partner.py dev

# 启动生产环境
python start_ai_partner.py prod

# 仅安装依赖
python start_ai_partner.py install

# 执行健康检查
python start_ai_partner.py health

# 执行完整设置（创建虚拟环境、安装依赖）
python start_ai_partner.py setup
```

### 高级选项

```bash
# 指定虚拟环境路径
python start_ai_partner.py dev --venv-path ./my_venv

# 强制重新创建虚拟环境
python start_ai_partner.py dev --force-venv
```

## 测试结果

服务已成功启动并通过测试：
- ✅ 健康检查端点返回 200 OK
- ✅ WebSocket 连接成功
- ✅ 所有 API 路由注册完成

## 注意事项

1. 首次运行会自动创建虚拟环境并安装依赖，可能需要较长时间
2. 如果遇到依赖冲突，可尝试使用 `--force-venv` 选项重新创建虚拟环境
3. 开发环境默认启用热重载功能，生产环境禁用热重载
4. 服务默认监听 `0.0.0.0:8000`

## 故障排查

### 常见问题

1. **端口被占用**
   - 错误信息：`OSError: [Errno 98] Address already in use`
   - 解决方法：关闭占用端口的进程或修改配置文件中的端口

2. **依赖安装失败**
   - 错误信息：`ERROR: Could not find a version that satisfies the requirement X`
   - 解决方法：检查网络连接或使用 `--force-venv` 选项重新创建虚拟环境

3. **环境变量加载失败**
   - 错误信息：`Missing required environment variable: X`
   - 解决方法：确保 `.env` 文件存在且包含所有必要的环境变量