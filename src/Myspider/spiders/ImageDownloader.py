from scrapy_redis.spiders import RedisSpider
from urllib.parse import urljoin
from Myspider.items import ImageItem, CustomItemLoader

class ImageDownloader(RedisSpider):
    name = "image_downloader"
    redis_key = "image_pages:start_urls"
    allowed_domains = ["www.bilibili.com"]

    def parse(self, response):
        loader = CustomItemLoader(item=ImageItem(), response=response)
        loader.add_value("page_url", response.url)
        
        # 提取图片URL（根据实际页面结构调整选择器）
        loader.add_css(
            "image_urls",
            "img[src]::attr(src)"
        )
        
        # 处理相对路径
        raw_urls = loader.get_collected_values("image_urls")
        absolute_urls = [urljoin(response.url, url) for url in raw_urls]
        loader.replace_value("image_urls", absolute_urls)
        
        yield loader.load_item()