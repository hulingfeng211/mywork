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

import tornadoredis
from tornado.gen import coroutine, Task
from dateutil import tz

from core.common import MongoBaseHandler, MINIUIMongoHandler, MINIUITreeHandler, BaseHandler


class OnlineUserHandler(BaseHandler):
    """从缓存服务器上获取当前登陆的所有用户"""
    def initialize(self):
        """"""""
        cache_config = self.settings['session']['driver_settings']
        host = cache_config['host']
        port = cache_config['port']
        db = cache_config['db']
        self.client = tornadoredis.Client(selected_db=db, host=host, port=port)
        self.client.connect()

    @coroutine
    def get(self, *args, **kwargs):
        # todo
        keys = yield Task(self.client.keys)

        result = []
        for key in keys:
            tmp_user=yield Task(self.client.get,key)
            # china
            to_zone=tz.gettz('CST')

            user=pickle.loads(tmp_user)

            # china time
            expirestime=user['__expires__'].astimezone(to_zone)

            result.append({
                "loginname":user['user']['username'],
                "remoteip":user['user']['remote_ip'],
                "logintime":user['user']['login_time'].strftime('%Y-%m-%d %H:%M:%S'),
                "lastaccesstime":user['last_access_time'].strftime('%Y-%m-%d %H:%M:%S') ,
                "expiretime":expirestime.strftime('%Y-%m-%d %H:%M:%S') ,

            })

        self.send_message(result)

    def finish(self, chunk=None):
        self.client.disconnect()
        super(BaseHandler,self).finish()


# 公共的路由
routes = [

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
    (r'/s/resources',MINIUIMongoHandler,{'cname':'resources'}),

    # 在线用户
    (r'/s/onlineuser',OnlineUserHandler),

]

