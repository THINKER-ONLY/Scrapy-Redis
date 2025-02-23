"""

 定义管道类，用于处理爬虫爬取到的数据
 该类必须实现 process_item 方法，该方法接收一个 Item 对象和一个 Spider 对象作为参数，
 该方法用于处理爬取到的数据，比如去重、存储到数据库等。
 可以定义多个管道类，每个管道类都会依次处理 Item 对象，管道类的执行顺序是按照它们在配置文件中的顺序执行的。
 
"""

# 具体的配置项请参考官方文档
# See: http://doc.scrapy.org/topics/item-pipeline.html
from datetime import datetime

# 定义一个管道类，用于处理爬虫爬取到的数据，为每个 Item 对象添加 crawled 和 spider 两个字段
# crawled 字段表示爬取时间，spider 字段表示爬虫名称
class Pipeline:
    def process_item(self, item, spider):
        item["crawled"] = datetime.utcnow()
        item["spider"] = spider.name
        return item
