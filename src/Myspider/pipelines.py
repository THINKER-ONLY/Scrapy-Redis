"""

 定义管道类，用于处理爬虫爬取到的数据
 该类必须实现 process_item 方法，该方法接收一个 Item 对象和一个 Spider 对象作为参数，
 该方法用于处理爬取到的数据，比如去重、存储到数据库等。
 可以定义多个管道类，每个管道类都会依次处理 Item 对象，管道类的执行顺序是按照它们在配置文件中的顺序执行的。
 
"""

# 具体的配置项请参考官方文档
# See: http://doc.scrapy.org/topics/item-pipeline.html
import redis
import scrapy
import os
import re
import logging
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from itemadapter import ItemAdapter

logger = logging.getLogger(__name__)

class LinkPipeline:
    def __init__(self, redis_conn):
        self.redis_conn = redis_conn
        self.queue_key = "image_pages:start_urls"
        
    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    @classmethod
    def from_settings(cls, settings):
        redis_conn = redis.Redis(
            host=settings.get("REDIS_HOST", "localhost"),
            port=settings.get("REDIS_PORT", 6379),
            db=settings.get("REDIS_DB", 0),
            decode_responses=True
        )
        return cls(redis_conn)

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if url := adapter.get("url"):
            self.redis_conn.lpush(self.queue_key, url)
            logger.debug(f"Redis队列插入: {url}")
        else:
            raise DropItem("缺失URL字段")
        return item

class ImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for image_url in item.get("image_urls", []):
            yield scrapy.Request(image_url, meta={"item": item})

    def file_path(self, request, response=None, info=None, *, item=None):
        page_url = request.meta["item"]["page_url"]
        safe_page_url = re.sub(r'[\\/:*?"<>|]', '_', page_url)
        image_name = request.url.split("/")[-1].split("?")[0]
        return os.path.join(safe_page_url, image_name)

    def item_completed(self, results, item, info):
        image_paths = [x["path"] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("无有效图片")
        item["images"] = image_paths
        return item