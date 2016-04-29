#!/usr/bin/env python
# -*- coding:utf-8 -*- 
"""========================================================== 
|   FileName:manage.py
|   Author: george
|   mail:hulingfeng211@163.com
|   Created Time:2015年07月22日 星期三 09时56分37秒
|   Description:应用程序入口
+============================================================"""
import logging
from tornado import gen
from tornado.ioloop import IOLoop
from tornado.options import define, options, parse_command_line
from tornado.web import Application, RequestHandler, url
from tornado.gen import coroutine
from tornado.httpclient import AsyncHTTPClient
from tornado import  autoreload
import os

import constant
from core import settings
from handler import   routes,nui,service,get_handlers,stock,smscenter

define('port', default=10001, type=int, help="在此端口接收用户请求")

def add(a,b):
    return a+b


def addwatchfiles(*paths):
    for p in paths:
        autoreload.watch(os.path.abspath(p))


class WorkApplication(Application):
    def __init__(self):
        # handlers = [
        #      (r'/', IndexHandler),
        #
        #     # 所有html静态文件都默认被StaticFileHandler处理
        #      # (r'/tpl/(.*)', StaticFileHandler, {
        #      #     'path': os.path.join(os.path.dirname(__file__), 'templates')
        #      # }),
        #      # PC端网页
        #      # (r'/f/', RedirectHandler, {'url': '/f/index.html'}),
        #      # (r'/f/(.*)', StaticFileHandler, {
        #      #     'path': os.path.join(os.path.dirname(__file__), 'front')
        #      # }),
        #  ]
        handlers=[]
        #handlers.extend(auth.routes)
        #handlers.extend(oa.routes)
        #handlers.extend(chat.routes)
        handlers.extend(nui.routes)
        handlers.extend(service.routes)
        handlers.extend(stock.routes)
        handlers.extend(smscenter.routes)
        handlers.extend(routes)
        site_url_prefix=settings.get(constant.SITE_URL_PREFIX,"")
        if site_url_prefix:
            # 构建新的URL
            handlers=map(lambda x:url(site_url_prefix+x.regex.pattern,x.handler_class,x.kwargs,x.name),handlers)
        #handlers =  get_handlers()
        Application.__init__(self, handlers=handlers, **settings)


if __name__ == "__main__":
    parse_command_line()
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    addwatchfiles('restart.txt')
    app = WorkApplication()
    logging.info('server at http://*:%s' % options.port)
    app.listen(options.port,xheaders=True)
    ioloop=IOLoop.current()
    #ioloop.run_sync(session_time_out_check)
    ioloop.start()
