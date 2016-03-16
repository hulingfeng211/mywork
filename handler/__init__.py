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
import pymongo
import tornadoredis
from tornado.gen import coroutine, Task, Return

import config
import constant
from core import make_password, settings
from core.common import MongoBaseHandler, NUIMongoHandler, NUITreeHandler, BaseHandler, NUIBaseHandler
from core.utils import utc_to_local, format_datetime, create_class
from handler.service import URLService, TimeoutService, LoginRolesService
from nui import LoginHandler,LogoutHandler, IndexHandler


class MD5Handler(NUIBaseHandler):

    def get(self, *args, **kwargs):
        key=self.get_argument('key',None)
        md5=make_password(key if key else '111111')
        self.send_message(md5)

#@coroutine
def get_handlers():
    client=pymongo.MongoClient(config.MONGO_URI)
    db=client[config.DB_NAME]
    cursor=db.urls.find()
    handlers=[]
    urls=list(cursor)
    if not list(urls):
        # 登录页
        handlers.append((r'/page/login',LoginHandler))
        # 登出服务
        handlers.append((r'/page/logout',LoginHandler))
        # 会话超时的服务
        handlers.append((r'/s/sessiontimeout', TimeoutService))
        # 系统首页
        handlers.append((r'/app/', IndexHandler))
        # 系统首页
        handlers.append((r'/', IndexHandler))
        # 登录时的角色服务
        handlers.append((r'/s/login/roles', LoginRolesService))
        # 系统首页
        handlers.append((r'/app$', IndexHandler))
        # url管理页面
        handlers.append((r'/s/app/urls', URLService,{'role_map':{'post':'root'}}))
        # url管理服务
        # URL管理
        handlers.append((r'/s/urls', NUIMongoHandler, {'cname': 'urls'}))
        handlers.append((r'/s/urls/(.+)', NUIMongoHandler, {'cname': 'urls'}))
        handlers.append((r'/page/url', NUIBaseHandler, {'template': 'nui/url.mgt.html', 'title': 'URL管理'}))
        return handlers

    for url in urls:
        role_map={}
        perm_map={}
        url_pattern=url.get('url_pattern',None)
        template_path=url.get('template',None)
        title=url.get('title',None)
        cname=url.get('cname',None)

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

        handlers.append((r'%s'%url_pattern,cls,{'cname':cname,'template':template_path,'title':title,'role_map':role_map,'perm_map':perm_map}))
    return handlers

class OnlineUserHandler(NUIBaseHandler):
    """从缓存服务器上获取当前登陆的所有用户"""
    def initialize(self, *args, **kwargs):

        """"""""
        #self.client=tornadoredis.Client(connection_pool=self.settings[constant.CONNECTION_POOL],selected_db=self.settings[constant.SESSION_DB])
        self.client = tornadoredis.Client(selected_db=self.settings[constant.SESSION_DB], host=self.settings[constant.REDIS_HOST], port=self.settings[constant.REDIS_PORT])
        self.client.connect()
        super(OnlineUserHandler,self).initialize( *args, **kwargs)


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

    # 员工管理
    (r'/s/employees', NUIMongoHandler, {'cname': 'employees'}),
    (r'/s/employees/(.+)', NUIMongoHandler, {'cname': 'employees'}),

    # 用户管理
    (r'/s/users', NUIMongoHandler, {'cname': 'users'}),
    (r'/s/users/(.+)', NUIMongoHandler, {'cname': 'users'}),

    # 角色管理
    (r'/s/roles', NUITreeHandler, {'cname': 'roles'}),

    # 菜单管理
    (r'/s/menus', NUITreeHandler, {'cname': 'menus'}),

    # 组织管理
    (r'/s/orgns', NUITreeHandler, {'cname': 'orgns'}),

    # 权限管理
    (r'/s/perms', NUIMongoHandler, {'cname': 'perms'}),
    # URL管理
    (r'/s/urls', NUIMongoHandler, {'cname': 'urls'}),
    (r'/s/urls/(.+)', NUIMongoHandler, {'cname': 'urls'}),

    # 在线用户
    (r'/s/onlineuser',OnlineUserHandler),

]

