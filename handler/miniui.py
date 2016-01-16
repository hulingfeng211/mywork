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
        self.render('miniui/menu.add.html')

    def post(self, *args, **kwargs):
        pass


routes = [
    (r'/miniui/', HelloHandler),
    (r'/miniui$', HelloHandler),
    (r'/miniui/home', HomeHandler),
    (r'/miniui/menu', MenuHandler),
]
