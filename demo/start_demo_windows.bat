@echo off
chcp 65001 >nul
echo ========================================
echo AI Partner Demo 启动脚本 (Windows)
echo ========================================

echo 正在激活虚拟环境...
call ..\venv\Scripts\activate.bat

echo 虚拟环境已激活
echo.

echo 当前Python路径:
where python

echo.
echo 检查AI Partner智能体...
python -c "from agents.partner_agent import AIPartnerAgent; print('AI Partner智能体加载成功!')"

if %ERRORLEVEL% neq 0 (
    echo AI Partner智能体加载失败，正在尝试安装依赖...
    pip install langchain langchain-core
)

echo.
echo 启动后端服务...
cd web_interface\backend
python run.py dev

pause