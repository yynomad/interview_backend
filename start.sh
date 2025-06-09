#!/bin/bash

# ===========================================
# 面试助手后端服务启动脚本
# ===========================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    echo -e "${2}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

print_success() {
    print_message "$1" "$GREEN"
}

print_error() {
    print_message "$1" "$RED"
}

print_warning() {
    print_message "$1" "$YELLOW"
}

print_info() {
    print_message "$1" "$BLUE"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 未安装，请先安装 $1"
        exit 1
    fi
}

# 检查配置文件
check_config() {
    if [ ! -f ".env" ]; then
        print_warning ".env 文件不存在"
        print_info "请按照以下步骤配置："
        print_info "1. 复制配置文件: cp .env.example .env"
        print_info "2. 编辑 .env 文件，填入你的 Gemini API Key"
        print_info "3. 重新运行此脚本"
        echo ""
        print_info "获取 API Key: https://makersuite.google.com/app/apikey"
        exit 1
    fi

    # 检查 API Key 配置
    if grep -q "your_gemini_api_key_here" .env 2>/dev/null; then
        print_warning "需要配置 Gemini API Key"
        print_info "请编辑 .env 文件，将 GEMINI_API_KEY 设置为你的实际 API Key"
        print_info "获取 API Key: https://makersuite.google.com/app/apikey"
        echo ""
        print_warning "继续运行将以测试模式启动（AI 功能不可用）"
        echo ""
    fi

    # 检查 SECRET_KEY 配置
    if grep -q "your_secret_key_here" .env 2>/dev/null; then
        print_warning "建议配置 SECRET_KEY"
        print_info "生成密钥: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
        echo ""
    fi
}

# 启动服务
start_service() {
    print_info "启动面试助手后端服务..."

    # 检查 Python
    check_command python3
    check_command pip3

    # 检查配置文件
    check_config

    # 检查虚拟环境
    if [ ! -d "venv" ]; then
        print_info "创建虚拟环境..."
        python3 -m venv venv
    fi

    # 激活虚拟环境
    print_info "激活虚拟环境..."
    source venv/bin/activate

    # 安装依赖
    print_info "安装依赖..."
    pip install -r requirements.txt

    # 启动服务
    print_success "启动面试助手后端服务..."
    python app.py
}



# 健康检查
health_check() {
    print_info "正在进行健康检查..."
    sleep 5  # 等待服务启动

    if curl -s http://localhost:5001/health > /dev/null; then
        print_success "服务健康检查通过！"
        print_info "服务地址: http://localhost:5001"
        print_info "健康检查: http://localhost:5001/health"
        print_info "API文档: 请查看 README.md"
    else
        print_error "服务健康检查失败，请检查日志"
    fi
}

# 显示帮助信息
show_help() {
    echo "面试助手后端服务启动脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  start               启动服务 (默认)"
    echo "  stop                停止服务"
    echo "  restart             重启服务"
    echo "  health              健康检查"
    echo "  help                显示此帮助信息"
    echo ""
    echo "首次使用："
    echo "  1. cp .env.example .env"
    echo "  2. 编辑 .env 文件，配置 GEMINI_API_KEY"
    echo "  3. $0 start"
    echo ""
    echo "示例:"
    echo "  $0                  # 启动服务"
    echo "  $0 start            # 启动服务"
    echo "  $0 stop             # 停止服务"
    echo "  $0 health           # 健康检查"
}

# 停止服务
stop_services() {
    print_info "停止服务..."

    # 停止直接运行的进程
    if pgrep -f "python.*app.py" > /dev/null; then
        pkill -f "python.*app.py"
        print_success "服务已停止"
    else
        print_warning "没有找到运行中的服务"
    fi
}

# 重启服务
restart_services() {
    print_info "重启服务..."
    stop_services
    sleep 2
    start_service
}

# 主函数
main() {
    print_info "面试助手后端服务启动脚本"
    print_info "==============================="

    case "${1:-start}" in
        "start"|"")
            start_service
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services
            ;;
        "health")
            health_check
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
