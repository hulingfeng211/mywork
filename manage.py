#!/usr/bin/env python
# -*- coding:utf-8 -*- 
"""========================================================== 
+FileName:manage.py
+Author: george
+mail:hulingfeng211@163.com
+Created Time:2015年07月22日 星期三 09时56分37秒
+Description:应用程序入口
+============================================================"""
import logging
from tornado.ioloop import IOLoop
from tornado.options import define, options, parse_command_line
from tornado.web import Application, RequestHandler,StaticFileHandler,RedirectHandler
from tornado.gen import coroutine
from tornado.httpclient import AsyncHTTPClient
import  os
from core import settings
from handler import auth,oa

define('port', default=10000, type=int, help="在此端口接收用户请求")

class IndexHandler(RequestHandler):
    @coroutine
    def get(self, *args, **kwargs):
        self.render('index.html',title='炎黄表单')
        #query_args=self.get_arguments()
        #self.write(self.request.body)

class IOfficeApplication(Application):
   def __init__(self):

       handlers=[
           (r'/',IndexHandler),

           #所有html静态文件都默认被StaticFileHandler处理
           (r'/tpl/(.*)',StaticFileHandler,{
               'path':os.path.join(os.path.dirname(__file__),'templates')
           }),
           #PC端网页
           (r'/f/',RedirectHandler,{'url':'/f/index.html'}),
           (r'/f/(.*)',StaticFileHandler,{
               'path':os.path.join(os.path.dirname(__file__),'front')
           }),
       ]
       handlers.extend(auth.routes)
       handlers.extend(oa.routes)
       Application.__init__(self,handlers=handlers,**settings)


if __name__ == "__main__":
    parse_command_line()
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    app = IOfficeApplication()
    logging.info('server at http://*:%s'%options.port)
    app.listen(options.port)
    ioloop=IOLoop.current()
    ioloop.start()
