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
from tornado.web import url

import config
import constant
from core import make_password, settings
from core.common import  NUIMongoHandler, NUITreeHandler, BaseHandler, NUIBaseHandler
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
        handlers.append(url(r'/page/login',LoginHandler,name='page.login'))
        # 登出服务
        handlers.append(url(r'/page/logout',LoginHandler,name='page.logout'))
        # 会话超时的服务
        handlers.append(url(r'/s/sessiontimeout', TimeoutService,name='s.sessiontimeout'))
        # 系统首页
        handlers.append(url(r'/app/', IndexHandler,name='home.app'))
        # 系统首页
        handlers.append(url(r'/', IndexHandler,name='home'))
        handlers.append(url(r'$', IndexHandler,name='home2'))

        # 登录时的角色服务
        handlers.append(url(r'/s/login/roles', LoginRolesService,name='s.login.roles'))
        # url管理页面
        handlers.append(url(r'/s/app/urls', URLService,{'role_map':{'post':'root'}},name='s.app.urls'))
        # url管理服务
        # URL管理
        handlers.append(url(r'/s/urls', NUIMongoHandler, {'cname': 'urls'},name='s.urls'))
        handlers.append(url(r'/s/urls/(.+)', NUIMongoHandler, {'cname': 'urls'},name='s.urls.item'))
        handlers.append(url(r'/page/url', NUIBaseHandler, {'template': 'nui/url.mgt.html', 'title': 'URL管理'},name='page.url'))
        return handlers

    for item in urls:
        role_map={}
        perm_map={}
        url_pattern=item.get('url_pattern',None)
        template_path=item.get('template',None)
        title=item.get('title',None)
        cname=item.get('cname',None)
        name=item.get('name',None)

        role_map['get']=item.get('role_get').split(',') if item.get('role_get','') else []
        role_map['put']=item.get('role_put').split(',') if item.get('role_put','') else []
        role_map['post']=item.get('role_post').split(',') if item.get('role_post','') else []
        role_map['delete']=item.get('role_delete').split(',') if item.get('role_delete','') else []

        perm_map['get']=item.get('perm_get').split(',') if item.get('perm_get','') else []
        perm_map['put']=item.get('perm_put').split(',') if item.get('perm_put','') else []
        perm_map['post']=item.get('perm_post').split(',') if item.get('perm_post','') else []
        perm_map['delete']=item.get('perm_delete').split(',') if item.get('perm_delete','') else []


        full_class_str=item.get('handler_class')
        full_class_str_split=full_class_str.split('.')
        module_name='.'.join(full_class_str_split[:-1])
        class_name=full_class_str_split[-1]
        cls=create_class(module_name,class_name)

        handlers.append(url(r'%s'%url_pattern,cls,
                            {'cname':cname,
                             'template':template_path,
                             'title':title,
                             'role_map':role_map,
                             'perm_map':perm_map},
                            name=name))
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
    url(r'/s/md5',MD5Handler,name='s.md5'),

    # 员工管理
    url(r'/s/employees', NUIMongoHandler, {'cname': 'employees'},name='s.employees'),
    url(r'/s/employees/(.+)', NUIMongoHandler, {'cname': 'employees'},name='s.employees.item'),

    # 用户管理
    url(r'/s/users', NUIMongoHandler, {'cname': 'users'},name='s.users'),
    url(r'/s/users/(.+)', NUIMongoHandler, {'cname': 'users'},name='s.users.item'),

    # 角色管理
    url(r'/s/roles', NUITreeHandler, {'cname': 'roles'},name='s.roles'),

    # 菜单管理
    url(r'/s/menus', NUITreeHandler, {'cname': 'menus'},name='s.menus'),

    # 组织管理
    url(r'/s/orgns', NUITreeHandler, {'cname': 'orgns'},name='s.orgns'),

    # 文件目录
    url(r'/s/file/catalogs', NUITreeHandler, {'cname': 'file.catalogs'},name='s.file.catalogs'),

    # 权限管理
    url(r'/s/perms', NUIMongoHandler, {'cname': 'perms'},name='s.perms'),
    # URL管理
    url(r'/s/urls', NUIMongoHandler, {'cname': 'urls'},name='s.urls'),
    url(r'/s/urls/(.+)', NUIMongoHandler, {'cname': 'urls'},name='s.urls.item'),

    # 在线用户
    url(r'/s/onlineuser',OnlineUserHandler,name='s.onlineuser'),

    # 文件查询
    url(r'/s/catalog/files', NUIMongoHandler, {'cname': 'fs.files'},name='s.catalog.files'),

    url(r'/s/servers', NUIMongoHandler, {'cname': 'servers'},name='s.servers'),
    url(r'/s/servers/(.+)', NUIMongoHandler, {'cname': 'servers'},name='s.servers.item'),

]

