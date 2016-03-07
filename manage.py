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
import motor
import pickle
import tornadoredis
from tornado import gen
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.options import define, options, parse_command_line
from tornado.web import Application, RequestHandler, StaticFileHandler, RedirectHandler
from tornado.gen import coroutine, Task
from tornado.httpclient import AsyncHTTPClient
import os
from tornadoredis import ConnectionPool

import config
from core import settings
from handler import auth, oa, chat, routes, miniui, service

define('port', default=10000, type=int, help="在此端口接收用户请求")

def add(a,b):
    return a+b

class IndexHandler(RequestHandler):
    @coroutine
    def get(self, *args, **kwargs):
        # ?BPMEngine=AWS&
        # sid=admin_1448843249906_169.24.2.22$b32c1025fcd18abd44890f97f302b4ffL{cn}LC{pc}C&
        # pid=%E8%BF%90%E8%A1%8C%E6%97%B6%E5%88%BB%E6%95%B0%E6%8D%AE&
        # tid=%E8%BF%90%E8%A1%8C%E6%97%B6%E5%88%BB%E6%95%B0%E6%8D%AE&
        # status=%E8%BF%90%E8%A1%8C%E6%97%B6%E5%88%BB%E6%95%B0%E6%8D%AE (169.24.2.22) 32.77ms
        pid = self.get_argument('pid', None)
        tid = self.get_argument('tid', None)
        status = self.get_argument('status', None)
        sid = self.get_argument('sid', None)

        self.render('index.html', title='炎黄表单', pid=pid, tid=tid, status=status, sid=sid,add=add)
        # query_args=self.get_arguments()
        # self.write(self.request.body)


class WorkApplication(Application):
    def __init__(self):
        handlers = [
            (r'/', IndexHandler),

            # 所有html静态文件都默认被StaticFileHandler处理
            (r'/tpl/(.*)', StaticFileHandler, {
                'path': os.path.join(os.path.dirname(__file__), 'templates')
            }),
            # PC端网页
            (r'/f/', RedirectHandler, {'url': '/f/index.html'}),
            (r'/f/(.*)', StaticFileHandler, {
                'path': os.path.join(os.path.dirname(__file__), 'front')
            }),
        ]
        handlers.extend(auth.routes)
        handlers.extend(oa.routes)
        handlers.extend(chat.routes)
        handlers.extend(miniui.routes)
        handlers.extend(service.routes)
        handlers.extend(routes)
        Application.__init__(self, handlers=handlers, **settings)


if __name__ == "__main__":
    parse_command_line()
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    app = WorkApplication()
    logging.info('server at http://*:%s' % options.port)
    app.listen(options.port)
    ioloop=IOLoop.current()
    #ioloop.run_sync(session_time_out_check)
    ioloop.start()
