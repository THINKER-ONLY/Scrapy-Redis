# 具体的配置项请参考官方文档
#     http://doc.scrapy.org/topics/settings.html

SPIDER_MODULES = ["Myspider.spiders"]
NEWSPIDER_MODULE = "Myspider.spiders"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"

# Redis配置
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_PARAMS = {
    "socket_connect_timeout": 30,
    "socket_keepalive": True,
    "retry_on_timeout": True
}

# 分布式配置
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
SCHEDULER_PERSIST = True
SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderPriorityQueue"

# 管道配置
ITEM_PIPELINES = {
    "Myspider.pipelines.LinkPipeline": 350,
    "Myspider.pipelines.ImagePipeline": 400
}

# 图片配置
IMAGES_STORE = "./images"
IMAGES_MIN_HEIGHT = 100
IMAGES_MIN_WIDTH = 100
IMAGES_EXPIRES = 30

# 性能优化
CONCURRENT_REQUESTS = 32
DOWNLOAD_DELAY = 1
AUTOTHROTTLE_ENABLED = True
LOG_LEVEL = "INFO"