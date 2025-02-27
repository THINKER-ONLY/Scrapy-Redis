# LinkCollector.py
from datetime import datetime
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from scrapy_redis.spiders import RedisCrawlSpider
from Myspider.items import PageLinkItem, CustomItemLoader

class LinkCollector(RedisCrawlSpider):
    name = "link_collector"
    redis_key = "link_collector:start_urls"
    allowed_domains = ["www.bilibili.com"]

    rules = (
        Rule(
            LinkExtractor(
                restrict_css=".channel-items__left .channel-link",
                allow=r"/anime|/movie|/guochuang|/tv|/variety|/documentary|/v"
            ),
            callback="parse_page",
            follow=True
        ),
    )

    def parse_page(self, response):
        loader = CustomItemLoader(item=PageLinkItem(), response=response)
        loader.add_value("url", response.url)
        loader.add_value("crawled", datetime.utcnow().isoformat())
        loader.add_value("spider", self.name)
        yield loader.load_item()