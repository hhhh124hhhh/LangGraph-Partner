#!/bin/bash

# AI Partner API 启动脚本
# 提供便捷的服务启动和管理功能

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Python环境
check_python() {
    log_info "检查Python环境..."

    if ! command -v python3 &> /dev/null; then
        log_error "Python3未安装"
        exit 1
    fi

    python_version=$(python3 --version | cut -d' ' -f2)
    log_success "Python版本: $python_version"
}

# 检查虚拟环境
check_venv() {
    log_info "检查虚拟环境..."

    if [[ "$VIRTUAL_ENV" == "" ]]; then
        log_warning "未检测到虚拟环境，建议使用虚拟环境"

        if [[ ! -d "venv" ]]; then
            log_info "创建虚拟环境..."
            python3 -m venv venv
        fi

        log_info "激活虚拟环境..."
        source venv/bin/activate
    else
        log_success "虚拟环境已激活: $VIRTUAL_ENV"
    fi
}

# 安装依赖
install_dependencies() {
    log_info "安装Python依赖..."

    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
        log_success "依赖安装完成"
    else
        log_error "requirements.txt文件不存在"
        exit 1
    fi
}

# 检查环境配置
check_env() {
    log_info "检查环境配置..."

    if [[ ! -f ".env" ]]; then
        if [[ -f ".env.example" ]]; then
            log_warning ".env文件不存在，从.env.example复制"
            cp .env.example .env
            log_warning "请编辑.env文件设置必要的环境变量"
        else
            log_error "未找到.env.example文件"
            exit 1
        fi
    fi

    # 检查关键环境变量
    if [[ -z "${OPENAI_API_KEY}" ]]; then
        log_error "未设置OPENAI_API_KEY环境变量"
        exit 1
    fi

    log_success "环境配置检查通过"
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."

    mkdir -p vector_db memory config logs
    log_success "目录创建完成"
}

# 启动开发服务器
start_dev() {
    log_info "启动开发服务器..."

    export API_DEBUG=true
    export API_RELOAD=true

    python -m uvicorn app.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --reload \
        --log-level info
}

# 启动生产服务器
start_prod() {
    log_info "启动生产服务器..."

    # 检查gunicorn
    if ! command -v gunicorn &> /dev/null; then
        log_info "安装gunicorn..."
        pip install gunicorn
    fi

    gunicorn app.main:app \
        -w 4 \
        -k uvicorn.workers.UvicornWorker \
        --bind 0.0.0.0:8000 \
        --log-level info \
        --timeout 120 \
        --access-logfile - \
        --error-logfile -
}

# 运行测试
run_tests() {
    log_info "运行测试..."

    # 检查pytest
    if ! command -v pytest &> /dev/null; then
        log_info "安装pytest..."
        pip install pytest pytest-asyncio pytest-cov
    fi

    pytest tests/ -v --cov=app --cov-report=term-missing
}

# 健康检查
health_check() {
    log_info "执行健康检查..."

    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "服务运行正常"
        curl -s http://localhost:8000/health | python -m json.tool
    else
        log_error "服务无法访问"
        exit 1
    fi
}

# 构建Docker镜像
build_docker() {
    log_info "构建Docker镜像..."

    if command -v docker &> /dev/null; then
        docker build -t ai-partner-api .
        log_success "Docker镜像构建完成"
    else
        log_error "Docker未安装"
        exit 1
    fi
}

# 运行Docker容器
run_docker() {
    log_info "运行Docker容器..."

    if [[ ! -f ".env" ]]; then
        log_error "请先创建.env文件"
        exit 1
    fi

    docker run -d \
        --name ai-partner-api \
        -p 8000:8000 \
        --env-file .env \
        -v $(pwd)/data:/app/data \
        ai-partner-api

    log_success "Docker容器已启动"
}

# 显示帮助信息
show_help() {
    echo "AI Partner API 启动脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  dev     启动开发服务器"
    echo "  prod    启动生产服务器"
    echo "  test    运行测试"
    echo "  health  健康检查"
    echo "  setup   初始化项目环境"
    echo "  docker  构建并运行Docker"
    echo "  help    显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 setup     # 初始化项目"
    echo "  $0 dev       # 启动开发服务器"
    echo "  $0 test      # 运行测试"
}

# 主函数
main() {
    case "${1:-help}" in
        "setup")
            check_python
            check_venv
            install_dependencies
            check_env
            create_directories
            log_success "项目初始化完成"
            ;;
        "dev")
            check_env
            start_dev
            ;;
        "prod")
            check_env
            start_prod
            ;;
        "test")
            check_env
            run_tests
            ;;
        "health")
            health_check
            ;;
        "docker")
            build_docker
            run_docker
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# 捕获中断信号
trap 'log_info "服务已停止"; exit 0' INT TERM

# 执行主函数
main "$@"