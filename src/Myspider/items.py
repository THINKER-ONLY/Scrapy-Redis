# 具体定义参考：
# http://doc.scrapy.org/topics/items.html

"""
#和管道很像,items.py文件也是一个定义类的文件,只不过这个类是用来定义数据结构的。
#在这个类中,我们定义了一个Item类,这个类继承自scrapy的Item类,然后定义了一些字段,这些字段就是我们要爬取的数据的字段。
#这个类中还定义了一个ItemLoader类,这个类继承自scrapy的ItemLoader类,这个类是用来加载Item的,我们可以在这个类中定义一些数据处理的方法,比如数据清洗,数据格式化等等。

"""
from scrapy.item import Field, Item
from scrapy.loader import ItemLoader
from itemloaders.processors import Join, MapCompose, TakeFirst
from w3lib.html import remove_tags

class PageLinkItem(Item):
    url = Field(output_processor=TakeFirst())     # 网页链接
    crawled = Field(output_processor=TakeFirst()) # 爬取时间
    spider = Field(output_processor=TakeFirst())  # 爬虫名称

class ImageItem(Item):
    image_urls = Field(
        input_processor=MapCompose(remove_tags, str.strip)
    )
    images = Field()
    page_url = Field(output_processor=TakeFirst())

class CustomItemLoader(ItemLoader):
    default_input_processor = MapCompose(str.strip)
    default_output_processor = TakeFirst()
    description_out = Join()