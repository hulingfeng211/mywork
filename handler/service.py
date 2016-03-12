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
from datetime import datetime

import tornadoredis
from bson import ObjectId
from tornado import escape
from tornado.gen import coroutine, engine, Task
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, asynchronous
from torndsession.sessionhandler import SessionBaseHandler

import constant
from core import clone_dict
from core.common import MINIUIBaseHandler, BaseHandler
from core.utils import format_datetime, create_class

__author__ = 'george'


class TimeoutService(BaseHandler):
    def prepare(self):
        """当当前用户为None的时候客户端页面自动切换到登陆"""
        current_user = self.get_current_user()
        if not current_user:
            self.write('1')
            self.finish()

    def initialize(self, *args, **kwargs):
        self.client = tornadoredis.Client(connection_pool=self.settings[constant.CONNECTION_POOL],
                                          selected_db=self.settings[constant.SESSION_DB])
        # self.client = tornadoredis.Client(selected_db=4, host='192.168.2.14', port=6379)
        self.client.connect()

    @asynchronous
    def get(self, *args, **kwargs):
        channel_name = '__keyevent@%s__:expired' % self.settings[
            constant.SESSION_DB]  # self.get_argument('channel_name',None)
        if channel_name:
            self.channel_name = channel_name
            self.get_data(channel_name)

    @engine
    def subscribe(self, channel_name):
        yield Task(self.client.psubscribe, channel_name)
        self.client.listen(self.on_message)

    # @coroutine
    def get_data(self, channel_name):
        if self.request.connection.stream.closed():
            return
        self.subscribe(channel_name)
        num = int(self.settings[constant.MAX_POLLING_TIMEOUT])  # 设置超时时间,

        IOLoop.current().add_timeout(time.time() + num, lambda: self.on_timeout(num))

    def on_timeout(self, num):
        self.send_data('0')
        # if self.client.connection.connected():
        #    self.client.disconnect()

    def send_data(self, body):
        if self._finished:
            # if self.request.connection.stream.closed():
            return
        self.set_header('Content-Type', 'application/json;charset=UTF-8')
        self.write(body)
        self.finish()

    def on_message(self, msg):
        if msg.kind == 'pmessage':
            if self.session.id == msg.body:
                self.send_data("1")
        elif msg.kind == 'unsubscribe':
            self.client.disconnect()

    @coroutine
    def on_finish(self):
        if hasattr(self, 'channel_name'):
            if self.client.subscribed:
                self.client.unsubscribe(self.channel_name)
                # if self.client.connection.connected():
                #    yield Task(self.client.disconnect)

                # 不需要进行session的expire的刷新
                # super(TimeoutService, self).on_finish()


class UserPermService(MINIUIBaseHandler):
    """用户权限服务"""

    @coroutine
    def get(self, *args, **kwargs):
        key = self.get_argument('key', None)
        if key:
            db = self.settings['db']
            result = yield db.users.find_one({'_id': ObjectId(key)}, {'perms': 1, "_id": 0})
            ids = [ObjectId(id) for id in result.get('perms', [])]
            result = yield db.perms.find({'_id': {'$in': ids}}).to_list(length=None)
            self.send_message(result)
        else:
            pass

    @coroutine
    def post(self, *args, **kwargs):
        body = escape.json_decode(self.request.body)
        userid = body.get('uid', None)
        perms = body.get('perms', [])
        if userid and perms:
            db = self.settings['db']
            for p in perms:
                yield db.users.update({'_id': ObjectId(userid)}, {'$addToSet': {"perms": p['id']}})


class UserMenusService(MINIUIBaseHandler):
    @coroutine
    def get(self, *args, **kwargs):
        db = self.settings['db']
        role = self.session.get('user')['role']
        role_info = yield db.roles.find_one({'code': role})
        if role_info:

            all_menus = yield db.menus.find().to_list(length=None)
            if role == self.settings[constant.ROOT_ROLE_CODE]:
                self.send_message(all_menus)
                self.finish()
                return
            #role_menus = yield db.role_menus.find_one({'role_id': str(role_info.get('_id'))})
            role_menus = role_info.get('menus')
            result = []
            for m in all_menus:
                result.append(m)
                if str(m.get('_id')) not in role_menus and m.get('url', None):
                    result.remove(m)
            self.send_message(result)


class RoleMenusService(MINIUIBaseHandler):
    @coroutine
    def get(self, *args, **kwargs):
        role_id = self.get_argument('role_id', None)
        pageIndex = int(self.get_query_argument('pageIndex', 0))
        pageSize = int(self.get_query_argument('pageSize', 20))
        if role_id:
            db = self.settings['db']
            role = yield db.roles.find_one({'_id': ObjectId(role_id)})
            menu_ids = [ObjectId(id) for id in role.get('menus', [])]
            cursor = db.menus.find({"_id": {"$in": menu_ids}}) #
            yield self.write_page(cursor,pageIndex=pageIndex,pageSize=pageSize)
            # .to_list(length=None)
            #self.send_message(menus)

    @coroutine
    def post(self, *args, **kwargs):
        body = escape.json_decode(self.request.body)
        role_id = body.get('role_id', None)
        menus = body.get('menus', [])
        if role_id and menus:
            db = self.settings['db']
            for item in menus:
                if item['_state'] == 'removed':
                    yield db.roles.update({'_id': ObjectId(role_id)}, {'$pull': {'menus': item['id']}})
                else:
                    yield db.roles.update({'_id': ObjectId(role_id)}, {'$push': {'menus': item['id']}})


class RolePermsService(MINIUIBaseHandler):
    @coroutine
    def get(self, *args, **kwargs):
        role_id = self.get_argument('role_id', None)
        pageIndex = int(self.get_query_argument('pageIndex', 0))
        pageSize = int(self.get_query_argument('pageSize', 20))
        if role_id:
            db = self.settings['db']
            role = yield db.roles.find_one({'_id': ObjectId(role_id)})
            perm_ids = [ObjectId(id) for id in role.get('perms', [])]
            perms = yield db.perms.find({"_id": {"$in": perm_ids}}).to_list(length=None)
            cursor = db.perms.find({"_id": {"$in": perm_ids}})
            yield self.write_page(cursor,pageIndex=pageIndex,pageSize=pageSize)
            #self.send_message(perms)


    @coroutine
    def post(self, *args, **kwargs):
        body = escape.json_decode(self.request.body)
        role_id = body.get('role_id', None)
        perms = body.get('perms', [])
        if role_id and perms:
            db = self.settings['db']
            for item in perms:
                if item['_state'] == 'removed':
                    yield db.roles.update({'_id': ObjectId(role_id)}, {'$pull': {'perms': item['id']}})
                else:
                    yield db.roles.update({'_id': ObjectId(role_id)}, {'$push': {'perms': item['id']}})


class RoleUsersService(MINIUIBaseHandler):
    @coroutine
    def get(self, *args, **kwargs):
        role_id = self.get_argument('role_id', None)
        page_index = int(self.get_query_argument('pageIndex', 0))
        page_size = int(self.get_query_argument('pageSize', 10))

        if role_id:
            db = self.settings['db']
            role = yield db.roles.find_one({'_id': ObjectId(role_id)})
            cursor = db.users.find({"roles": {"$all": [role['code']]}})
            yield self.write_page(cursor)
            #total = yield cursor.count()
            #users = yield cursor.skip(page_index * page_size).limit(page_size).to_list(length=None)
            #self.send_message(users, total=total)

    @coroutine
    def post(self, *args, **kwargs):
        body = escape.json_decode(self.request.body)
        role_id = body.get('role_id', None)
        users = body.get('users', [])
        if role_id and users:
            db = self.settings['db']
            role = yield db.roles.find_one({'_id': ObjectId(role_id)})
            for item in users:
                if item['_state'] == 'removed':
                    yield db.users.update({'_id': ObjectId(item['id'])}, {'$pull': {'roles': role['code']}, "$set": {
                        "update_time": format_datetime(datetime.now()),
                        "update_user": self.current_user.get('username', '')}})
                elif item['_state'] == 'added' and not item.get('id',None):
                    user = clone_dict(item)
                    if hasattr(user, 'roles'):
                        user['roles'].append(role['code'])
                    else:
                        user['roles'] = [role['code']]
                    user['id'] = ObjectId()
                    user['_id'] = user['id']

                    user['create_time'] = format_datetime(datetime.now())
                    user['create_user'] = self.current_user.get('username', '')
                    yield db.users.insert(user)
                else:
                    user = clone_dict(item)
                    user['update_time'] = format_datetime(datetime.now())
                    user['update_user'] = self.current_user.get('username', '')
                    del user['roles']
                    yield db.users.update({'_id': ObjectId(item['id'])}, {"$push":{"roles":role['code']},"$set": user})


class RolesMenusService(RequestHandler):
    @coroutine
    def get(self, *args, **kwargs):
        db = self.settings['db']
        roles = yield db.roles.find({}, {"_id": 0, "code": 1, "name": 1}).to_list(length=None)
        self.set_header('content-type', 'application/json');
        self.write(escape.json_encode(roles))

    def check_xsrf_cookie(self):
        pass

class LogoutService(MINIUIBaseHandler):
    """管理员注销其他用户"""
    @coroutine
    def post(self, *args, **kwargs):
        # todo

        pass

class URLService(MINIUIBaseHandler):
    """URL服务，获取所有系统的url"""

    @coroutine
    def get(self, *args, **kwargs):

        def exception_url(url_pattern):
            exception=['static','robots','favicon']
            for item in exception:
                if item in url_pattern:
                    return True
            return False

        url_list=self.application.handlers[0][1]
        result=[]
        for s in url_list:
            tmp={}
            if exception_url(s._path):
                continue
            tmp['url_pattern']=s._path.replace('%s','(.*)')
            tmp['handler_class']='%s.%s'%(s.handler_class.__module__,s.handler_class.__name__)
            for k,v in s.kwargs.iteritems():
                if k=='role_map':
                    for rk,rv in v.iteritems():
                        tmp['role_%s'%rk]=rv
                elif k=='perm_map':
                    for pk,pv in v.iteritems():
                        tmp['perm_%s'%pk]=reduce(lambda x,y:x+','+y,pv)
                    pass
                else:
                    tmp[k]=v
            result.append(tmp)
        self.send_message(result)

    @coroutine
    def post(self, *args, **kwargs):
        """重新创建URL列表"""
        db=self.settings['db']
        urls=yield db.urls.find().to_list(length=None)
        handlers=[]

        for url in urls:
            role_map={}
            perm_map={}
            url_pattern=url.get('url_pattern')
            template_path=url.get('template') if hasattr(url,'template') else None
            title=url.get('title') if hasattr(url,'title') else None

            role_map['get']=url.get('role_get').split(',') if url.get('role_get','') else []
            role_map['put']=url.get('role_put').split(',') if url.get('role_put','') else []
            role_map['post']=url.get('role_post').split(',') if url.get('role_post','') else []
            role_map['delete']=url.get('role_delete').split(',') if url.get('role_delete','') else []

            perm_map['get']=url.get('perm_get').split(',') if url.get('perm_get','') else []
            perm_map['put']=url.get('perm_put').split(',') if url.get('perm_put','') else []
            perm_map['post']=url.get('perm_post').split(',') if url.get('perm_post','') else []
            perm_map['delete']=url.get('perm_delete').split(',') if url.get('perm_delete','') else []


            full_class_str=url.get('handler_class')
            full_class_str_split=full_class_str.split('.')
            module_name='.'.join(full_class_str_split[:-1])
            class_name=full_class_str_split[-1]
            cls=create_class(module_name,class_name)

            #self.application.add_handler()
            if template_path and title:
                handlers.append((r'%s'%url_pattern,cls,{'template':template_path,'title':title}))
            elif cls==MINIUIBaseHandler:
                handlers.append((r'%s'%url_pattern,cls,{'role_map':role_map,'perm_map':perm_map}))
            else:
                handlers.append((r'%s'%url_pattern,cls))

        self.application.add_handlers(".*$", handlers)
        self.send_message('ok')

routes = [
    # (r'/s/menu',MenuService),
    # (r'/s/orgn',OrgnService),
    (r'/s/userperms', UserPermService),
    (r'/s/sessiontimeout', TimeoutService),
    (r'/s/role/menus', RoleMenusService),
    (r'/s/role/perms', RolePermsService),
    (r'/s/role/users', RoleUsersService),
    (r'/s/user/menus', UserMenusService),
    (r'/s/login/roles', RolesMenusService),
    (r'/s/app/urls', URLService),
]
