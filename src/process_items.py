#!/usr/bin/env python

# -*- coding: utf-8 -*-
# 一个简单的从Redis队列中读取数据的脚本
# 用于处理爬虫爬取的数据

import argparse
import json
import logging
import pprint
import sys
import time
from scrapy_redis import get_redis

# 创建一个logger，用于记录日志
logger = logging.getLogger("process_items")


def process_items(r, keys, timeout, limit=0, log_every=1000, wait=0.1):
    """从Redis队列中持续消费并处理数据。

    Args:
        r (redis.Redis): Redis连接实例
        keys (list): 监听的Redis键列表(支持多队列)
        timeout (int): 阻塞弹出操作的超时时间(秒)
        limit (int): 最大处理条目数(0表示无限制)
        log_every (int): 每处理多少条目记录一次进度
        wait (float): 无数据时的休眠间隔(秒)

    """
    
    limit = limit or float("inf")
    processed = 0
    while processed < limit:
        # Change ``blpop`` to ``brpop`` to process as LIFO.
        ret = r.blpop(keys, timeout)
        # If data is found before the timeout then we consider we are done.
        if ret is None:
            time.sleep(wait)
            continue

        source, data = ret
        try:
            item = json.loads(data)
        except Exception:
            logger.exception("Failed to load item:\n%r", pprint.pformat(data))
            continue

        try:
            name = item.get("name") or item.get("title")
            url = item.get("url") or item.get("link")
            logger.debug("[%s] Processing item: %s <%s>", source, name, url)
        except KeyError:
            logger.exception(
                "[%s] Failed to process item:\n%r", source, pprint.pformat(item)
            )
            continue

        processed += 1
        if processed % log_every == 0:
            logger.info("Processed %s items", processed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    """必选参数"""
    parser.add_argument("key", help="Redis key where items are stored")  

    """可选参数"""
    parser.add_argument("--host", help="Redis服务器地址(默认: localhost)")
    parser.add_argument("--port", help="Redis服务器端口(默认: 6379)")
    parser.add_argument("--timeout", type=int, default=5, 
                       help="阻塞弹出超时时间(秒，默认: 5)")
    parser.add_argument("--limit", type=int, default=0,
                       help="最大处理条目数(0=无限制，默认: 0)")
    parser.add_argument("--progress-every", type=int, default=1000,
                       help="进度汇报频率(默认: 1000条)")
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="启用详细日志(DEBUG级别)")

    args = parser.parse_args()

    # 配置日志级别
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s - %(levelname)s - %(message)s")

    # 创建Redis连接
    redis_params = {}
    if args.host:
        redis_params["host"] = args.host
    if args.port:
        redis_params["port"] = args.port

    # 显示连接信息
    r = get_redis(**redis_params)
    conn_ifo = r.connection_pool.get_connection("info")
    logger.info("Waiting for items in '%s' (server: %s)", 
                args.key, conn_ifo.host,conn_ifo.port)
    
    # 处理数据
    kwargs = {
        "keys": [args.key],
        "timeout": args.timeout,
        "limit": args.limit,
        "log_every": args.progress_every,
    }
    try:
        process_items(r, **kwargs)
        retcode = 0
    except KeyboardInterrupt:
        logger.info("用户中断操作")
        retcode = 0 
    except Exception as e:
        logger.exception("致命错误: %s", str(e), exc_info=True)
        retcode = 2

    return retcode


if __name__ == "__main__":
    sys.exit(main())
