# -*- coding:utf-8 -*-
from tornado import gen
from tornado.gen import coroutine
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler

from core import make_password
from core.common import MINIUIBaseHandler

__author__ = 'george'


class IndexHandler(MINIUIBaseHandler):
    def get(self, *args, **kwargs):
        self.render('miniui/index.html',site_name=self.settings['site_name'])


class HomeHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.render('miniui/home.html')

class ResourceHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.render('miniui/resource.mgt.html')


class MenuHandler(MINIUIBaseHandler):
    def get(self, *args, **kwargs):
        self.render('miniui/menu.mgt.html')

class OrgnHandler(MINIUIBaseHandler):
    def get(self, *args, **kwargs):
        self.render('miniui/orgn.mgt.html')

class UserHandler(MINIUIBaseHandler):
    def get(self, *args, **kwargs):
        self.render('miniui/user.mgt.html')

class EmployeeHandler(MINIUIBaseHandler):
    def get(self, *args, **kwargs):
        self.render('miniui/employee.mgt.html')

class LogoutHandler(MINIUIBaseHandler):
    def prepare(self):
        pass

    def get(self, *args, **kwargs):
        self.session.delete('user')
        self.redirect('/app')

class LoginHandler(MINIUIBaseHandler):

    def prepare(self):
        """skip login valid"""
        pass

    def get(self, *args, **kwargs):
        self.render('miniui/login.html',site_name=self.settings['site_name'])

    @coroutine
    def post(self, *args, **kwargs):
        #gen.sleep(10);
        username = self.get_argument('username',None)
        pwd = self.get_argument('pwd',None)
        db = self.settings['db']
        user = yield db.users.find_one({"email":username})
        if user and pwd:
            if make_password(pwd) == user.get('pwd'):
                # self.send_error(status_code=500,reason='用户名和密码不能违空')
                self.session.set('user',{'username':username})
            else:
                self.send_error(status_code=500,reason="密码错误")
        else:
            self.send_error(status_code=500,reason='用户名和密码不能为空')


routes = [
    (r'/app/', IndexHandler),
    (r'/app$', IndexHandler),
    (r'/app/home', HomeHandler),
    (r'/page/menu', MenuHandler),
    (r'/page/orgn', OrgnHandler),
    (r'/page/employee', EmployeeHandler),
    (r'/page/user', UserHandler),
    (r'/page/login', LoginHandler),
    (r'/page/logout', LogoutHandler),
    (r'/page/resource', ResourceHandler),
]
