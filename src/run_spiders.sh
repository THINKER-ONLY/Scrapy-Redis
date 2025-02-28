#!/bin/bash
# 文件名：run_spiders.sh
# 描述：增强版分布式爬虫管理脚本
# 功能：依赖检查、服务管理、进程监控、日志分析
# 兼容性：支持Linux/macOS/Windows(WSL)

# ================= 配置区 =================
REDIS_PORT=6379
NUM_DOWNLOADERS=4                # 消费者进程数
JOBS_BASE_DIR="./jobs"           # 任务状态目录
LOG_DIR="./logs"                 # 日志目录
IMAGES_DIR="./images"            # 图片存储目录
PYTHON_VENV="./venv"             # Python虚拟环境路径
REQUIREMENTS="requirements.txt"  # 依赖文件

# Redis配置
REDIS_CONF="/etc/redis/redis.conf"  # Linux/macOS路径
# REDIS_CONF="C:\\Program Files\\Redis\\redis.conf"  # Windows路径

# ================= 函数定义 =================
init_environment() {
    # 创建必要目录
    mkdir -p "${JOBS_BASE_DIR}" "${LOG_DIR}" "${IMAGES_DIR}"
    
    # 检查Python虚拟环境
    if [ ! -d "${PYTHON_VENV}" ]; then
        echo "[初始化] 创建Python虚拟环境..."
        python3 -m venv "${PYTHON_VENV}"
        source "${PYTHON_VENV}/bin/activate"
        pip install -r "${REQUIREMENTS}"
        deactivate
    fi
}

check_dependencies() {
    # 检查系统依赖
    local missing=()
    
    # Redis检查
    if ! command -v redis-server &> /dev/null; then
        missing+=("redis-server")
    fi
    
    # Python检查
    if ! command -v python3 &> /dev/null; then
        missing+=("python3")
    fi

    if [ ${#missing[@]} -gt 0 ]; then
        echo "[错误] 缺少依赖: ${missing[*]}"
        exit 1
    fi
}

manage_redis() {
    case $1 in
        start)
            if ! pgrep -x "redis-server" > /dev/null; then
                echo "[Redis] 启动服务..."
                redis-server "${REDIS_CONF}" --port ${REDIS_PORT} --daemonize yes
                sleep 2
                if ! redis-cli -p ${REDIS_PORT} ping &> /dev/null; then
                    echo "[错误] Redis启动失败!"
                    exit 1
                fi
            fi
            ;;
        stop)
            echo "[Redis] 停止服务..."
            redis-cli -p ${REDIS_PORT} shutdown
            ;;
        status)
            if redis-cli -p ${REDIS_PORT} ping &> /dev/null; then
                echo "[Redis] 运行中 (端口: ${REDIS_PORT})"
            else
                echo "[Redis] 未运行"
            fi
            ;;
    esac
}

start_spiders() {
    # 激活虚拟环境
    source "${PYTHON_VENV}/bin/activate"
    
    # 启动生产者
    echo "[爬虫] 启动生产者..."
    nohup scrapy crawl link_collector \
        -s JOBDIR="${JOBS_BASE_DIR}/producer" \
        --logfile="${LOG_DIR}/producer.log" >> "${LOG_DIR}/producer_console.log" 2>&1 &

    # 启动消费者集群
    echo "[爬虫] 启动 ${NUM_DOWNLOADERS} 个消费者..."
    for ((i=1; i<=NUM_DOWNLOADERS; i++)); do
        nohup scrapy crawl image_downloader \
            -s JOBDIR="${JOBS_BASE_DIR}/consumer_${i}" \
            --logfile="${LOG_DIR}/consumer_${i}.log" >> "${LOG_DIR}/consumer_${i}_console.log" 2>&1 &
    done

    deactivate
}

inject_seed_url() {
    local url="https://www.bilibili.com"
    echo "[初始化] 注入种子URL: ${url}"
    redis-cli -p ${REDIS_PORT} lpush link_collector:start_urls "${url}" > /dev/null
}

monitor_dashboard() {
    while true; do
        clear
        echo "=============== 爬虫监控面板 ==============="
        # Redis队列状态
        local producer_queue=$(redis-cli -p ${REDIS_PORT} llen link_collector:start_urls)
        local consumer_queue=$(redis-cli -p ${REDIS_PORT} llen image_pages:start_urls)
        
        # 图片下载统计
        local image_count=$(find "${IMAGES_DIR}" -type f | wc -l)
        
        # 进程状态
        local producer_pid=$(pgrep -f "crawl link_collector")
        local consumer_pids=($(pgrep -f "crawl image_downloader"))
        
        printf "%-18s %-10s\n" "生产队列:" "${producer_queue}"
        printf "%-18s %-10s\n" "消费队列:" "${consumer_queue}"
        printf "%-18s %-10s\n" "已下载图片:" "${image_count}"
        printf "%-18s %-10s\n" "生产者PID:" "${producer_pid:-未运行}"
        printf "%-18s %-10s\n" "消费者PIDs:" "${consumer_pids[*]:-无}"
        echo "============================================"
        sleep 5
    done
}

# ================= 主流程 =================
case $1 in
    start)
        check_dependencies
        init_environment
        manage_redis start
        start_spiders
        inject_seed_url
        monitor_dashboard
        ;;
    stop)
        manage_redis stop
        pkill -f "scrapy crawl"
        echo "[系统] 已停止所有爬虫进程"
        ;;
    status)
        manage_redis status
        ps -ef | grep "scrapy crawl" | grep -v grep
        ;;
    *)
        echo "用法: $0 {start|stop|status}"
        exit 1
        ;;
esac