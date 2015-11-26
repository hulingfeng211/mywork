# -*- coding:utf-8 -*-
import json
import constant
import logging
from tornado.escape import json_decode, json_encode
from tornado.gen import coroutine
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from tornado.web import RequestHandler, HTTPError
from core import is_json_request, make_password
from core.common import BaseHandler

__author__ = 'george'


class LoginHandler(BaseHandler):
    """用户登陆"""

    def prepare(self):
        pass

    @coroutine
    def post(self, *args, **kwargs):
        logging.info(self.request.body)
        user = {}
        if is_json_request(self.request):
            user = json_decode(self.request.body)
        logging.info('email:%s' % user.get('token')['principal'])
        logging.info('password:%s' % user.get('token')['credentials'])
        email = user.get('token')['principal']
        password = user.get('token')['credentials']
        login_url = constant.LOGIN_URL
        body = {
            "userCd": email,
            "password": make_password(password),
            "identifyNo": None
        }
        request = HTTPRequest(method="POST", url=login_url, body=json_encode(body), headers={
            "content-type": "application/json"
        })
        response=None
        try:

            response = yield AsyncHTTPClient().fetch(request)
        except Exception,e:

            logging.error(e)

        if response and response.body:
            data = json_decode(response.body)
            if data and data.get('userName', None):  #

                # 缓存用户信息到内存中
                self.session.set('user', data)
                logging.info(data)
                result = {
                    "info": {
                        "authc": {
                            "principal": {
                                "name": data.get('userName', ""),
                                "login": data.get('userName', ""),
                                "email": data.get('userCd', "")
                            },
                            "credentials": {
                                "name": data.get('userName', ""),
                                "login": data.get('userName', ""),
                                "email": data.get('userCd', "")
                            },
                        },
                        "authz": {
                            "roles": [],
                            "permissions": []
                        }
                    }
                }

                self.write(json_encode(result))
            else:
                self.write("密码输入错误")
                self.finish()

        else:
            self.write("当前登陆用户不存在")
            self.finish()


class LogoutHandler(BaseHandler):
    """用户登出"""

    @coroutine
    def prepare(self):
        # skip  BaseHandler prepare  method
        pass

    @coroutine
    def get(self, *args, **kwargs):
        logging.info(args)
        self.session.delete('user')
        self.write(json_encode({'status':'success'}))

class SignupHandler(RequestHandler):
    """用户注册"""

    @coroutine
    def post(self, *args, **kwargs):
        logging.info(self.request.body)
        if not is_json_request(self.request):
            raise HTTPError(status_code=500, log_message="目前仅支持application/json的请求")
        body = json.loads(self.request.body)
        db = self.settings['db']
        olduser = yield db.user.find({"name": body.get("name")}).to_list(length=None)
        if olduser and len(olduser) > 0:
            self.write("当前用户%s已经存在" % body.get("name"))
            self.finish()
        else:
            body['password'] = make_password(body.get('password'))
            yield db.user.insert(body)
            self.write(json_encode({"user": body}))


routes = [
    # 用户登陆
    (r'/auth/login', LoginHandler),
    # 用户注册
    (r'/auth/signup', SignupHandler),
    # 用户登出
    (r'/auth/logout', LogoutHandler)
]
