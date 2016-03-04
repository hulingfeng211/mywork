# -*- coding:utf-8 -*-
"""==========================================================
|
|
|       creater:george
|       create-time:2016-1-12 14:32:02
|       email:15921315347@163.com
|       description:RESTFul服务
|
|
============================================================="""
import time

import tornadoredis
from bson import ObjectId
from tornado import escape
from tornado.gen import coroutine, engine, Task
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, asynchronous
from torndsession.sessionhandler import SessionBaseHandler

import constant
from core.common import MINIUIBaseHandler, create_redis_client

__author__ = 'george'

class TimeoutService(SessionBaseHandler):

    def initialize(self, *args, **kwargs):
        self.client=tornadoredis.Client(connection_pool=self.settings[constant.CONNECTION_POOL],selected_db=self.settings[constant.REDIS_DB])
        #self.client = tornadoredis.Client(selected_db=5, host='192.168.2.14', port=6379)
        self.client.connect()

    @asynchronous
    def get(self, *args, **kwargs):
        channel_name=self.get_argument('channel_name',None)
        if channel_name:
            self.channel_name=channel_name
            self.get_data(channel_name)
    @engine
    def subscribe(self,channel_name):
        yield Task(self.client.subscribe, channel_name)
        self.client.listen(self.on_message)

    # @coroutine
    def get_data(self,channel_name):
        if self.request.connection.stream.closed():
            return
        self.subscribe(channel_name)
        num = 90  # 设置超时时间,

        IOLoop.current().add_timeout(time.time() + num, lambda: self.on_timeout(num))

    def on_timeout(self, num):
        self.send_data('0')
        if self.client.connection.connected():
            self.client.disconnect()

    def send_data(self, body):
        if self._finished:
            # if self.request.connection.stream.closed():
            return
        self.set_header('Content-Type', 'application/json;charset=UTF-8')
        self.write(body)
        self.finish()

    def on_message(self, msg):
        if msg.kind == 'message':
            self.send_data(str(msg.body))
        elif msg.kind == 'unsubscribe':
            self.client.disconnect()

    def on_finish(self):
        if hasattr(self,'channel_name'):
            if self.client.subscribed:
                self.client.unsubscribe(self.channel_name)
        super(TimeoutService, self).on_finish()

class UserPermService(MINIUIBaseHandler):
    """用户权限服务"""

    @coroutine
    def get(self, *args, **kwargs):
        key = self.get_argument('key',None)
        if key:
            db = self.settings['db']
            result=yield db.users.find_one({'_id':ObjectId(key)},{'perms':1,"_id":0})
            ids=[ObjectId(id) for id in result.get('perms',[])]
            result=yield db.perms.find({'_id':{'$in':ids}}).to_list(length=None)
            self.send_message(result)
        else:
            pass

    @coroutine
    def post(self, *args, **kwargs):
        body=escape.json_decode(self.request.body)
        userid=body.get('uid',None)
        perms=body.get('perms',[])
        if userid and perms:
            db = self.settings['db']
            for p in perms:
                yield db.users.update({'_id':ObjectId(userid)},{'$addToSet':{"perms":p['id']}})

# class OrgnService(RequestHandler):
#     """
#     组织服务
#     """
#     @coroutine
#     def get(self, *args, **kwargs):
#         result = yield self.settings['db'].orgns.find().to_list(length=None)
#
#         #print result
#         self.write(bson_encode(result))
#
#     @coroutine
#     def post(self, *args, **kwargs):
#         if 'application/json' in self.request.headers['content-Type']:
#             body=json_decode(self.request.body)
#             if body:
#                 data=body.get('data',None)
#                 remove_data=body.get('removed',None)
#         else:
#             data=self.get_argument('data',None)
#             remove_data = self.get_argument('removed', None)
#
#         if data:
#             print 'data:',data
#             data_json= escape.json_decode(data) if type(data)==unicode else data
#             list = to_list(data_json,"-1","children","id","pid")
#             print list
#             print 'len(list):',len(list)
#             for i,item in enumerate(list):
#                 yield self.settings['db'].orgns.save(item)
#
#         if remove_data:
#             data_json = escape.json_decode(remove_data)
#             list = to_list(data_json,"-1","children","id","pid")
#             for item in list:
#                 yield self.settings['db'].orgns.remove({"_id":item['id']})
#
#
#
# class MenuService(RequestHandler):
#     """
#     菜单服务
#     """
#
#     @coroutine
#     def get(self, *args, **kwargs):
#         result = yield self.settings['db'].menus.find().to_list(length=None)
#         #print result
#         self.write(bson_encode(result))
#
#     def check_xsrf_cookie(self):
#         """skip xsrf check"""
#         pass
#
#     @coroutine
#     def post(self, *args, **kwargs):
#         if 'application/json' in self.request.headers['content-Type']:
#             body=json_decode(self.request.body)
#             if body:
#                 data=body.get('data',None)
#                 remove_data=body.get('removed',None)
#         else:
#             data=self.get_argument('data',None)
#             remove_data = self.get_argument('removed', None)
#
#         if data:
#             print 'data:',data
#             data_json= escape.json_decode(data) if type(data)==unicode else data
#             list = to_list(data_json,"-1","children","id","pid")
#             print list
#             print 'len(list):',len(list)
#             for i,item in enumerate(list):
#                 yield self.settings['db'].menus.save(item)
#
#         if remove_data:
#             data_json = escape.json_decode(remove_data)
#             list = to_list(data_json,"-1","children","id","pid")
#             for item in list:
#                 yield self.settings['db'].menus.remove({"_id":item['id']})

routes=[
    #(r'/s/menu',MenuService),
    #(r'/s/orgn',OrgnService),
    (r'/s/userperms',UserPermService),
    (r'/s/sessiontimeout',TimeoutService),
]

