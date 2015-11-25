# -*- coding:utf-8 -*-
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application

__author__ = 'george'



class IndexHandler(RequestHandler):
    def post(self, *args, **kwargs):
        print self.request.body


if __name__=="__main__":
    app=Application([
        (r'/message',IndexHandler)
    ])
    app.listen(11000)
    print 'listen to 11000'
    IOLoop.current().start()
