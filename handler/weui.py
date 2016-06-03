# -*- coding:utf-8 -*-
from tornado.web import url

from core.common import BaseHandler

class WEUIHandler(BaseHandler):
    def get_current_user(self):
        return {'username':'george'}

class IndexHandler(WEUIHandler):

    def get(self, *args, **kwargs):
        self.render('weui/index.html',title='WEUI')



routes= [
    url(r'/weui/',IndexHandler,name='weui.home')

]