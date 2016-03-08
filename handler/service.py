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
from core.common import MINIUIBaseHandler, BaseHandler

__author__ = 'george'

class TimeoutService(BaseHandler):

    def prepare(self):
        """当当前用户为None的时候客户端页面自动切换到登陆"""
        current_user=self.get_current_user()
        if not current_user:
            self.write('1')
            self.finish()

    def initialize(self, *args, **kwargs):
        self.client=tornadoredis.Client(connection_pool=self.settings[constant.CONNECTION_POOL],selected_db=self.settings[constant.SESSION_DB])
        #self.client = tornadoredis.Client(selected_db=4, host='192.168.2.14', port=6379)
        self.client.connect()

    @asynchronous
    def get(self, *args, **kwargs):
        channel_name='__keyevent@%s__:expired'%self.settings[constant.SESSION_DB]#self.get_argument('channel_name',None)
        if channel_name:
            self.channel_name=channel_name
            self.get_data(channel_name)
    @engine
    def subscribe(self,channel_name):
        yield Task(self.client.psubscribe, channel_name)
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
        if msg.kind == 'pmessage':
            if self.session.id==msg.body:
                self.send_data("1")
        elif msg.kind == 'unsubscribe':
            self.client.disconnect()

    @coroutine
    def on_finish(self):
        if hasattr(self,'channel_name'):
            if self.client.subscribed:
                self.client.unsubscribe(self.channel_name)
            if self.client.connection.connected():
                yield Task(self.client.disconnect)

        # 不需要进行session的expire的刷新
        #super(TimeoutService, self).on_finish()

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

class UserMenusService(MINIUIBaseHandler):

    @coroutine
    def get(self, *args, **kwargs):
        db=self.settings['db']
        role=self.session.get('user')['role']
        role_info=yield db.roles.find_one({'code':role})
        if role_info:
            all_menus=yield db.menus.find().to_list(length=None)
            if role==self.settings[constant.ROOT_ROLE_CODE]:
                self.send_message(all_menus)
                self.finish()
                return
            role_menus=yield db.role_menus.find_one({'role_id':str(role_info.get('_id'))})
            role_menus=role_menus.get('menus')
            result= []
            for m in all_menus:
                result.append(m)
                if str(m.get('_id')) not in role_menus and  m.get('url',None):
                    result.remove(m)
            self.send_message(result)


class RoleMenusService(MINIUIBaseHandler):

    @coroutine
    def get(self, *args, **kwargs):
        role_id = self.get_argument('role_id')
        if role_id:
            db=self.settings['db']
            result=yield db.role_menus.find_one({'role_id':role_id},{'_id':0,'menus':1})
            menus=result.get('menus',[]) if result else None
            if menus:
                object_ids=[ObjectId(id) for id in menus]
                menus=yield db.menus.find({'_id':{"$in":object_ids}}).to_list(length=None)
                self.send_message(menus)


    @coroutine
    def post(self, *args, **kwargs):
        body=escape.json_decode(self.request.body)
        role_id=body.get('role_id',None)
        menus=body.get('menus',[])
        if role_id and menus:
            db=self.settings['db']
            check_exist=yield db.role_menus.find_one({'role_id':role_id})
            if not check_exist:
                yield db.role_menus.insert({'role_id':role_id,'menus': [m['id'] for m in  menus]})
            else:
                for item in menus:
                    if item['_state']=='removed':
                        yield db.role_menus.update({'role_id':role_id},{'$pull':{'menus':item['id']}})
                    else:
                        yield db.role_menus.update({'role_id':role_id},{'$push':{'menus':item['id']}})

routes=[
    #(r'/s/menu',MenuService),
    #(r'/s/orgn',OrgnService),
    (r'/s/userperms',UserPermService),
    (r'/s/sessiontimeout',TimeoutService),
    (r'/s/role/menus',RoleMenusService),
    (r'/s/user/menus',UserMenusService),
]

