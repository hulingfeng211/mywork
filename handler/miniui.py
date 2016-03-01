# -*- coding:utf-8 -*-
import time

import datetime
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
        self.render('miniui/login.html',site_name=self.settings['site_name'],title="用户登录")

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
                self.session.set('user',{'username':username,'remote_ip':self.request.remote_ip,'login_time':datetime.datetime.now()})
                self.send_message("登录成功")
            else:
                self.send_message("密码错误",status_code=1)
        else:
            self.send_message("用户不存在或密码为空",status_code=1)

routes = [
    (r'/app/', IndexHandler),
    (r'/app$', IndexHandler),
    (r'/page/home', MINIUIBaseHandler,{'template':'miniui/home.html','title':'首页'}),
    (r'/page/menu', MINIUIBaseHandler,{'template':'miniui/menu.mgt.html','title':'菜单管理'}),
    (r'/page/orgn', MINIUIBaseHandler,{'template':'miniui/orgn.mgt.html','title':'组织管理'}),
    (r'/page/employee', MINIUIBaseHandler,{'template':'miniui/employee.mgt.html','title':'员工管理'}),
    (r'/page/user', MINIUIBaseHandler,{'template':'miniui/user.mgt.html','title':'用户管理'}),
    (r'/page/login', LoginHandler),
    (r'/page/logout', LogoutHandler),
    (r'/page/perms', MINIUIBaseHandler,{'template':'miniui/perms.mgt.html','title':'权限管理'}),
    (r'/page/onlineuser', MINIUIBaseHandler,{'template':'miniui/onlineuser.mgt.html','title':'在线用户管理'}),
    (r'/page/choice_perms', MINIUIBaseHandler,{'template':'miniui/perms.choice.html','title':'选择权限'}),
]

