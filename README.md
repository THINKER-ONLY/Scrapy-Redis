# Scrapy-Redis

## 配置开发环境（建议使用conda）
1. clone一下仓库
```bash
git clone https://github.com/THINKER-ONLY/Scrapy-Redis.git
```
2. 激活虚拟环境，然后进入Scrapy-Redis文件夹,安装必要的库
```
python setup.py install
```
3. 本地配置redis
参考教程:
[Window下Redis的安装和部署详细图文教程](https://blog.csdn.net/weixin_44893902/article/details/123087435)

## 运行脚本

```bash
scrapy crawl mycrawler_redis                                       # 启动爬虫
python process_items.py mycrawler:items --host localhost 
redis-cli lpush mycrawler:start_urls "http://example.com/news/1"   # 推送起始 URL 到 Redis                                    
```