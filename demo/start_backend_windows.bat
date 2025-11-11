@echo off
chcp 65001 >nul
echo ========================================
echo AI Partner 后端启动脚本
echo ========================================

echo 正在切换到项目根目录...
cd ..\..

echo 正在激活虚拟环境...
call venv\Scripts\activate.bat

echo 当前工作目录: %CD%
echo Python路径:
where python

echo.
echo 检查AI Partner依赖...
python -c "import langgraph; print('LangGraph版本:', langgraph.__version__)" 2>nul
if %ERRORLEVEL% neq 0 (
    echo LangGraph未安装，正在安装...
    pip install langgraph langchain-core
)

echo.
echo 检查AI Partner智能体...
python -c "from agents.partner_agent import AIPartnerAgent; print('AI Partner智能体加载成功!')" 2>nul
if %ERRORLEVEL% neq 0 (
    echo AI Partner智能体加载失败，但继续启动...
)

echo.
echo 启动后端服务...
cd demo\web_interface\backend
python run.py dev

pause