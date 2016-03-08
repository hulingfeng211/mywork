# -*- coding:utf-8 -*-
"""==========================================================
|
|
|       creater:george
|       create-time:2016-1-12 14:32:02
|       email:15921315347@163.com
|       description:模块入口
|
|
============================================================="""
# 定义url模板
import pickle
#import  pytz
import tornadoredis
from tornado.gen import coroutine, Task

import constant
from core import make_password
from core.common import MongoBaseHandler, MINIUIMongoHandler, MINIUITreeHandler, BaseHandler, MINIUIBaseHandler
from core.utils import utc_to_local, format_datetime

class MD5Handler(BaseHandler):

    def get(self, *args, **kwargs):
        key=self.get_argument('key',None)
        md5=make_password(key if key else '111111')
        self.send_message(md5)

class OnlineUserHandler(MINIUIBaseHandler):
    """从缓存服务器上获取当前登陆的所有用户"""
    def initialize(self):
        """"""""
        #self.client=tornadoredis.Client(connection_pool=self.settings[constant.CONNECTION_POOL],selected_db=self.settings[constant.SESSION_DB])
        self.client = tornadoredis.Client(selected_db=self.settings[constant.SESSION_DB], host=self.settings[constant.REDIS_HOST], port=self.settings[constant.REDIS_PORT])
        self.client.connect()


    @coroutine
    def get(self, *args, **kwargs):

        keys = yield Task(self.client.keys)
        result = []
        for key in keys:
            tmp_user=yield Task(self.client.get,key)
            # china
            user=pickle.loads(tmp_user)
            if not user.get('user',None):
                continue
            expirestime=user['__expires__']
            result.append({
                "id":key,
                "loginname":user['user']['username'],
                "remoteip":user['user']['remote_ip'],
                "logintime":format_datetime(user['user']['login_time']),
                "lastaccesstime":format_datetime(user['last_access_time']) ,
                "expiretime":format_datetime(utc_to_local(expirestime)) ,

            })

        self.send_message(result)
    @coroutine
    def on_finish(self):
        if hasattr(self,'client') and self.client.connection.connected():
            yield Task(self.client.disconnect)
        super(OnlineUserHandler,self).on_finish()


# 公共的路由
routes = [

    # md5加密
    (r'/s/md5',MD5Handler),

    # 服务器管理
    (r'/servers',MongoBaseHandler,{'cname':'servers'}),
    (r'/servers/(.+)',MongoBaseHandler,{'cname':'servers'}),

    # event管理
    (r'/events',MongoBaseHandler,{'cname':'events'}),
    (r'/events/(.+)',MongoBaseHandler,{'cname':'events'}),

    # 任务管理
    (r'/tasks',MongoBaseHandler,{'cname':'tasks'}),
    (r'/tasks/(.+)',MongoBaseHandler,{'cname':'tasks'}),

    # 项目管理
    (r'/projects',MongoBaseHandler,{'cname':'projects'}),
    (r'/projects/(.+)',MongoBaseHandler,{'cname':'projects'}),

    # 标签管理
    (r'/labels',MongoBaseHandler,{'cname':'labels'}),
    (r'/labels/(.+)',MongoBaseHandler,{'cname':'labels'}),

    # 用户设置
    (r'/settings',MongoBaseHandler,{'cname':'settings'}),
    (r'/settings/(.+)',MongoBaseHandler,{'cname':'settings'}),

    # 菜单设置
    # (r'/s/menus',MongoBaseHandler,{'cname':'menus'}),
    # (r'/s/menus/(.+)',MongoBaseHandler,{'cname':'menus'}),

    # 员工管理
    (r'/s/employees',MINIUIMongoHandler,{'cname':'employees'}),
    (r'/s/employees/(.+)',MINIUIMongoHandler,{'cname':'employees'}),

    # 用户管理
    (r'/s/users',MINIUIMongoHandler,{'cname':'users'}),
    (r'/s/users/(.+)',MINIUIMongoHandler,{'cname':'users'}),

    # 角色管理
    (r'/s/roles',MINIUITreeHandler,{'cname':'roles'}),

    # 菜单管理
    (r'/s/menus',MINIUITreeHandler,{'cname':'menus'}),

    # 组织管理
    (r'/s/orgns',MINIUITreeHandler,{'cname':'orgns'}),

    # 权限管理
    (r'/s/perms',MINIUIMongoHandler,{'cname':'perms'}),

    # 在线用户
    (r'/s/onlineuser',OnlineUserHandler),

]

