# -*- coding:utf-8 -*-
"""==========================================================
|
|
|       creater:george
|       email:15921315347@163.com
|       description:系统的公共模块
|
|
|
============================================================="""
from tornado import gen
from tornado.escape import json_decode
from tornado.gen import coroutine
from tornado.web import authenticated
from tornado.httpclient import HTTPRequest, HTTPError, AsyncHTTPClient
from torndsession.sessionhandler import SessionBaseHandler

__author__ = 'george'

DEFAULT_HEADERS={
    'content-type':'application/json'
}

class BaseHandler(SessionBaseHandler):

    @coroutine
    def prepare(self):
        current_user = self.current_user
        if not current_user:
            #self.redirect('/f/index.html',permanent=False)
            #self.set_status(status_code=401,reason='用户未授权')
            self.send_error(status_code=401,reason='用户未授权')
            #self.redirect('/f/index.html',permanent=False)
            #raise HTTPError(code=401,message='未授权')
            #self.finish()

    def get_current_user(self):
        return self.session.get('user', None)

    @coroutine
    def send_request(self, url, body=None, method='GET',headers=DEFAULT_HEADERS,*args, **kwargs):
        """
        发送HTTP请求，并返回请求后的结果
        """
        url = url.replace(' ', '%20')

        userCd = self.current_user.get('userCd', None)
        pwd = self.current_user.get('pwd', None)
        request = HTTPRequest(url=url, method=method, body=body, auth_username=userCd,
                              auth_password=pwd, auth_mode='digest', validate_cert=False,headers=headers, **kwargs)
        response = yield AsyncHTTPClient().fetch(request)
        if response and response.code==200:
            raise gen.Return(response.body)
        else:
            raise gen.Return(None)
