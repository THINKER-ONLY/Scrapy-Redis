# 具体的配置项请参考官方文档
#     http://doc.scrapy.org/topics/settings.html

# 爬虫队列
SPIDER_MODULES = ["Myspider.spiders"]
NEWSPIDER_MODULE = "Myspider.spiders"

# 伪装成浏览器访问
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0"

# 添加 Redis 连接配置
REDIS_HOST = "localhost"
REDIS_PORT = 6379

# 使用scrapy-redis的调度器
# 指定使用scrapy-redis的去重类和调度器
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
SCHEDULER_PERSIST = True

# 可选的队列模式
SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderPriorityQueue"
# SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderQueue"
# SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderStack"

# 优先级队列
ITEM_PIPELINES = {
    "Myspider.pipelines.Pipeline": 300,
    "scrapy_redis.pipelines.RedisPipeline": 400,
}

# 日志级别
LOG_LEVEL = "DEBUG"

# Introduce an artifical delay to make use of parallelism. to speed up the
# crawl.
DOWNLOAD_DELAY = 1
