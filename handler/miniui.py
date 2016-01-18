# -*- coding:utf-8 -*-
from tornado.web import RequestHandler

__author__ = 'george'


class HelloHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.render('miniui/index.html')


class HomeHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.render('miniui/home.html')


class MenuHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.render('miniui/menu.mgt.html')

class OrgnHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.render('miniui/orgn.mgt.html')

routes = [
    (r'/app/', HelloHandler),
    (r'/app$', HelloHandler),
    (r'/app/home', HomeHandler),
    (r'/page/menu', MenuHandler),
    (r'/page/orgn', OrgnHandler),
]
