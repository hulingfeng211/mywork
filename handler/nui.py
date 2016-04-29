# -*- coding:utf-8 -*-
import time

import datetime

from bson import ObjectId
from tornado import gen
from tornado.gen import coroutine
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, url

import constant
from core import make_password
from core.common import NUIBaseHandler, authenticated

__author__ = 'george'

skins=["default","blue",'gray','olive2003','blue2003','blue2010','bootstrap',
       'metro','metro-green','metro-orange','jqueryui-uilightness','jqueryui-humanity',
       'jqueryui-excitebike','jqueryui-cupertino']

class IndexHandler(NUIBaseHandler):

    @coroutine
    def get(self, *args, **kwargs):

        cookie_role=self.get_cookie('role',None)
        db=self.settings['db']
        if not cookie_role:
            cookie_role=self.current_user.get('role')
        else:
            self.current_user['role']=cookie_role
            role=yield db.roles.find_one({'code':cookie_role})
            user_perm_ids=[ObjectId(id) for id in role.get('perms',[])]
            perms=yield db.perms.find({"_id":{"$in":user_perm_ids}},{'_id':0,'name':1}).to_list(length=None)
            self.current_user['perms']=[item['name'] for item in perms]

        current_skin=self.get_cookie('miniuiSkin','default')

        username=self.current_user.get('username')
        user = yield db.users.find_one({"$or":[{"email":username},{"loginname":username}]})
        roles=user.get('roles',[])
        roles=roles.split(',') if isinstance(roles,str) or isinstance(roles,unicode) else roles
        roles=yield db.roles.find({"code":{"$in":roles}},{'_id':0,'code':1,'name':1}).to_list(length=None)
        self.render('nui/index.html',
                    site_name=self.settings['site_name'],
                    roles=roles,
                    current_role=cookie_role,
                    skins=skins,
                    current_skin=current_skin
                    )



class LogoutHandler(NUIBaseHandler):
    @authenticated
    def prepare(self):
        pass

    @coroutine
    def get(self, *args, **kwargs):
        skin=self.get_cookie('miniuiSkin')
        # 保存用户设置
        db=self.settings['db']
        yield db.user.profile.save({'_id':self.current_user.get('userid'),'skin':skin})
        self.session.delete('user')
        #self.redirect('/app')
        self.send_message("成功登出")



class LoginHandler(NUIBaseHandler):

    def prepare(self):
        """skip login valid"""
        pass

    def get(self, *args, **kwargs):
        self.render('nui/login.html',site_name=self.settings['site_name'],title="用户登录")

    @coroutine
    def post(self, *args, **kwargs):
        #gen.sleep(10);
        username = self.get_argument('username',None)
        pwd = self.get_argument('pwd',None)
        db = self.settings['db']
        role_code=self.get_argument('role',None)

        user = yield db.users.find_one({"$or":[{"email":username},{"loginname":username}]})

        if user and pwd:
            if make_password(pwd) == user.get('pwd'):
                if user.get('nologin')==1:
                    self.send_message('用户被禁止登录，请联系管理员!',status_code=1)
                    return
                # self.send_error(status_code=500,reason='用户名和密码不能违空')
                # 验证通过后，获取用户的权限列表信息并保存到用户会话中
                role=yield db.roles.find_one({'code':role_code})

                if role['code'] not in user.get('roles',[]):
                    self.send_message('选择的角色与用户角色不匹配，请重新选择!',status_code=1)
                    return

                user_perm_ids=[ObjectId(id) for id in role.get('perms',[])]
                perms=yield db.perms.find({"_id":{"$in":user_perm_ids}},{'_id':0,'name':1}).to_list(length=None)

                #user_role_ids=[ObjectId(id) for id in user.get('roles',[])]
                #roles=yield db.roles.find({"_id":{"$in":user_role_ids}}).to_list(length=None)


                self.session.set('user',{'username':username,
                                         'role':role_code,
                                         'userid':str(user['_id']),
                                         'perms':[item['name'] for item in perms],
                                         'remote_ip':self.request.remote_ip,
                                         'login_time':datetime.datetime.now()})
                self.set_cookie('role',role_code)
                self.set_cookie('userid',str(user['_id']))
                user_profile=yield db.user.profile.find_one({'_id':str(user['_id'])})
                skin=user_profile.get('skin','default') if user_profile else 'default'
                self.set_cookie('miniuiSkin',skin)
                self.send_message("登录成功")
            else:
                self.send_message("密码错误",status_code=1)
        else:
            self.send_message("用户不存在或密码为空",status_code=1)

routes = [
    url(r'/app/', IndexHandler,name='home_app'),
    url(r'/', IndexHandler,name='home'),
    url(r'/$', IndexHandler,name='home'),
    url(r'$', IndexHandler,name='home_2'),
    url(r'/page/home', NUIBaseHandler, {'template': 'nui/home.html', 'title': '首页'},name='page.home'),
    url(r'/page/menu', NUIBaseHandler, {'template': 'nui/menu.mgt.html',
                                       'title':'菜单管理',
                                       'role_map':{
                                           'get':'ptyh','post':'ptyh'
                                       }},name='page.menu'),
    url(r'/page/orgn', NUIBaseHandler, {'template': 'nui/orgn.mgt.html', 'title': '组织管理'},name='page.orgn'),
    url(r'/page/employee', NUIBaseHandler, {'template': 'nui/employee.mgt.html', 'title': '员工管理'},name='page.employee'),
    url(r'/page/user', NUIBaseHandler, {'template': 'nui/user.mgt.html', 'title': '用户管理'},name="page.user"),
    url(r'/page/login', LoginHandler,name='page.login'),
    url(r'/page/logout', LogoutHandler,name='page.logout'),
    url(r'/page/perms', NUIBaseHandler, {'template': 'nui/perm.mgt.html', 'title': '权限管理'},name='page.perms'),

    # 仅root角色的用户可以访问此url
    url(r'/page/onlineuser', NUIBaseHandler, {'template': 'nui/onlineuser.mgt.html',
                                             'title':'在线用户管理',
                                           #'role_map':{'post':['root','ptyh']},
                                             'perm_map':{'post':['onlineuser:logout'],
                                                           'get':['onlineuser:logout']}},name='page.onlineuser'),

    #(r'/page/onlineuser', MINIUIBaseHandler,{'template':'miniui/onlineuser.mgt.html','title':'在线用户管理'}),
    url(r'/page/choice_perms', NUIBaseHandler, {'template': 'nui/perm.choice.html', 'title': '选择权限'},name='page.choice_perms'),
    url(r'/page/choice_menus', NUIBaseHandler, {'template': 'nui/menu.choice.html', 'title': '选择菜单'},name='page.choice_menus'),
    url(r'/page/choice_users', NUIBaseHandler, {'template': 'nui/user.choice.html', 'title': '选择用户'},name='page.choice_users'),
    url(r'/page/choice_urls', NUIBaseHandler, {'template': 'nui/url.choice.html', 'title': '选择URL'},name='page.choice_urls'),

    url(r'/page/role/menu', NUIBaseHandler, {'template': 'nui/role.menu.html', 'title': '角色菜单'},name='page.role.menu'),
    url(r'/page/role/user', NUIBaseHandler, {'template': 'nui/role.user.html', 'title': '角色用户'},name='page.role.user'),
    url(r'/page/userprofile', NUIBaseHandler, {'template': 'nui/user.profile.html', 'title': '用户配置'},name='page.userprofile'),
    url(r'/page/role', NUIBaseHandler, {'template': 'nui/role.mgt.html', 'title': '角色管理'},name='page.role'),
    url(r'/page/url', NUIBaseHandler, {'template': 'nui/url.mgt.html', 'title': 'URL管理'},name='page.url'),
    url(r'/page/files', NUIBaseHandler, {'template': 'nui/file.mgt.html', 'title': '文件管理'},name='page.files'),
    url(r'/page/role/edit', NUIBaseHandler, {'template': 'nui/edit.role.html', 'title': '编辑角色'},name='page.role.edit'),

    url(r'/page/servers', NUIBaseHandler, {'template': 'nui/server/server.mgt.html', 'title': '服务器管理'},name='page.servers'),
]

