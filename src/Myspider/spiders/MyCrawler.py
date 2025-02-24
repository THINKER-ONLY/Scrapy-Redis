# 爬虫文件，继承自RedisCrawlSpider，实现了一个简单的爬虫类，用于爬取网页的标题和链接
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from scrapy_redis.spiders import RedisCrawlSpider
from Myspider.items import Item, ItemLoader

class MyCrawler(RedisCrawlSpider):
    # 爬虫名称
    name = "mycrawler_redis"
    redis_key = "mycrawler:start_urls"
    # 允许爬取的域名
    allowed_domains = ["bilibili.com"]

    """ 爬取规则 """
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
        """解析页面, 提取标题、URL 和描述信息"""
        
        # 使用 ItemLoader 规范化数据处理
        loader = ItemLoader(item=Item(), response=response)
        
        # 提取字段（自动应用 processors）
        loader.add_css("name", "h1::text")          # 从 CSS 选择器提取标题
        loader.add_value("channel-link", response.url)          # 直接添加当前 URL
        loader.add_css(
            "description", 
            "meta[name='description']::attr(content)", # 提取 meta 描述
            default="暂无描述"                          # 默认值（避免空字段）
        )
        
        return loader.load_item()
