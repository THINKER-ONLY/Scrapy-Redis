#!/bin/bash
# 文件名：run_spiders.sh
# 描述：自动化启动Redis服务及分布式爬虫集群
# 权限：需chmod +x run_spiders.sh

REDIS_PORT=6379
NUM_DOWNLOADERS=4  # 设置图片下载爬虫实例数量
JOBS_BASE_DIR="./jobs"  # 任务状态存储目录
LOG_DIR="./logs"        # 日志目录

# 创建必要目录
mkdir -p ${JOBS_BASE_DIR} ${LOG_DIR} ./images

# 状态检查函数
check_redis() {
    if ! redis-cli.exe -p ${REDIS_PORT} ping &> /dev/null; then
        echo "[ERROR] Redis服务未运行！正在尝试自动启动..."
        redis-server --port ${REDIS_PORT} --daemonize yes
        sleep 2
        if redis-cli.exe -p ${REDIS_PORT} ping &> /dev/null; then
            echo "[OK] Redis已成功启动"
        else
            echo "[FATAL] Redis启动失败，请手动检查！"
            exit 1
        fi
    fi
}

# 启动生产者爬虫
start_producer() {
    echo "启动链接收集爬虫（生产者）..."
    nohup nohup scrapy crawl link_collector \
        -s JOBDIR=${JOBS_BASE_DIR}/producer \
        --logfile=${LOG_DIR}/producer.log >> ${LOG_DIR}/producer_console.log 2>&1 &
}

# 启动消费者集群
start_consumers() {
    echo "启动 ${NUM_DOWNLOADERS} 个图片下载爬虫（消费者）..."
    for ((i=1; i<=NUM_DOWNLOADERS; i++)); do
        nohup nohup scrapy crawl image_downloader \
            -s JOBDIR=${JOBS_BASE_DIR}/consumer_${i} \
            --logfile=${LOG_DIR}/consumer_${i}.log >> ${LOG_DIR}/consumer_${i}_console.log 2>&1 &
    done
}

# 注入初始URL
inject_seed() {
    echo "注入初始种子URL..."
    redis-cli -p ${REDIS_PORT} lpush link_collector:start_urls "https://www.bilibili.com" > /dev/null
}

# 监控面板
show_monitor() {
    clear
    echo "================ 爬虫监控面板 ================"
    echo "生产队列长度: $(redis-cli.exe -p ${REDIS_PORT} llen link_collector:start_urls)"
    echo "消费队列长度: $(redis-cli.exe -p ${REDIS_PORT} llen image_pages:start_urls)"
    echo "已下载图片数: $(find ./images -type f | wc -l)"
    echo "运行日志目录: ${LOG_DIR}"
    echo "=============================================="
}

# 主流程
main() {
    check_redis
    start_producer
    start_consumers
    inject_seed
    
    # 启动监控面板
    while true; do
        show_monitor
        sleep 5
    done
}

# 执行主程序
main