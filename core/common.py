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
import json
import logging
from bson import ObjectId
from tornado import gen
from tornado.escape import json_decode
from tornado.gen import coroutine
from tornado.web import authenticated
from tornado.httpclient import HTTPRequest, HTTPError, AsyncHTTPClient
from datetime import datetime
from torndsession.sessionhandler import SessionBaseHandler
from core import bson_encode, is_json_request, clone_dict_without_id
from core.utils import format_datetime
import ast

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

    def on_finish(self):
        #todo update session expire when client call service.
        super(SessionBaseHandler, self).on_finish()

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

    def send_message(self,obj):
        self.write(bson_encode(obj))

class MongoBaseHandler(BaseHandler):
    """通用的mongodb的Handler，封装简单的CRUD的操作"""
    def initialize(self, *args, **kwargs):
        # cname 为对应的mongodb的集合的名字
        if kwargs:
            for key, val in kwargs.items():
                if not hasattr(self, key):
                    setattr(self, key, val)
        super(MongoBaseHandler,self).initialize()

    @coroutine
    def get(self, *args, **kwargs):

        id = args[0] if len(args) > 0 else None
        if id:
            db = self.settings['db']
            obj = yield db[self.cname].find_one({"_id": ObjectId(id)})
            self.write(bson_encode(obj))
            return

        def get_query_args(self):
            other = {}
            q = {}  # 查询的规则 {'name':'aaa'}
            p = {}  # 文档字段的选择规则 如：只选取id {id:1},不选取id为 {id:0}
            s = {}  # 排序的规则
            try:
                for k, v in self.request.query_arguments.items():
                    if k == '_v':
                        continue
                    if k == 'q':  # 带查询参数
                        q = ast.literal_eval(v[0])
                        continue
                        pass
                    if k == 'p':  # 列投影
                        p = ast.literal_eval(v[0])
                        continue
                        pass
                    if k == 's':  # 排序
                        s = ast.literal_eval(v[0])
                        continue
                    if len(v) > 1:
                        other[k] = {"$in", v}
                    else:
                        other[k] = v[0]
            except ValueError, e:
                logging.error(e)
            return dict(q,**other), p, s

        q, p, s  = get_query_args(self)
        db = self.settings['db']

        if not p:
            cursor=db[self.cname].find(q )
            if not s:
                objs=yield cursor.to_list(length=None)
            else:
                objs=yield cursor.sort(s).to_list(length=None)
        else:
            cursor=db[self.cname].find(q ,p)
            if not s:
                objs=yield cursor.to_list(length=None)
            else:
                objs=yield cursor.sort(s).to_list(length=None)
        self.write(bson_encode(objs))

    @coroutine
    def put(self, *args, **kwargs):
        """接受用户的请求对文档进行更新
        :param args url路径的参数 """
        if is_json_request(self.request):
            body = json.loads(self.request.body)
        else:
            self.send_error(reason="仅支持Content-type:application/json")

        db = self.settings['db']
        if body.get('_id', None):  # update
            body['update_time']=format_datetime(datetime.now())
            body['update_user']=self.current_user.get('userCd','')
            yield db[self.cname].update({"_id": ObjectId(body.get('_id'))}, {
                "$set": clone_dict_without_id(body)
            })
        self.send_message("保存成功")

    @coroutine
    def delete(self, *args, **kwargs):
        id = args[0] if len(args) > 0 else None
        if id:
            db = self.settings['db']
            yield db[self.cname].remove({"_id": ObjectId(id)})

    @coroutine
    def post(self, *args, **kwargs):
        if is_json_request(self.request):
            body = json.loads(self.request.body)
        else:
            self.send_error(reason="仅支持Content-type:application/json")

        db = self.settings['db']
        if body.get('_id', None):  # update
            body['update_time']=format_datetime(datetime.now())
            body['update_user']=self.current_user.get('userCd','')
            yield db[self.cname].update({"_id": ObjectId(body.get('_id'))}, {
                "$set": clone_dict_without_id(body)
            })

        else:
            obj=clone_dict_without_id(body)
            obj['create_time']=format_datetime(datetime.now())
            obj['create_user']=self.current_user.get('userCd','')
            yield db[self.cname].insert(obj)
        #self.write(generate_response(message="保存成功"))
        self.send_message("保存成功")

if __name__=="__main__":
    from tornado.gen import IOLoop,coroutine
    import motor

    client=motor.MotorClient()
    db=client['test']
    @coroutine
    def f():
        yield db['servers'].insert({'a':'b'})
    ioloop=IOLoop.current()
    ioloop.run_sync(f)
