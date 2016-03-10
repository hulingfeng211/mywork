# -*- coding:utf-8 -*-
import time

import datetime

from bson import ObjectId
from tornado import gen
from tornado.gen import coroutine
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler

import constant
from core import make_password
from core.common import MINIUIBaseHandler

__author__ = 'george'

skins=["default","blue",'gray','olive2003','blue2003','blue2010','bootstrap',
       'metro','metro-green','metro-orange','jqueryui-uilightness','jqueryui-humanity',
       'jqueryui-excitebike','jqueryui-cupertino','nui']

class IndexHandler(MINIUIBaseHandler):

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
        roles=yield db.roles.find({"code":{"$in":user.get('roles')}},{'_id':0,'code':1,'name':1}).to_list(length=None)
        self.render('miniui/index.html',
                    site_name=self.settings['site_name'],
                    roles=roles,
                    current_role=cookie_role,
                    skins=skins,
                    current_skin=current_skin
                    )



class LogoutHandler(MINIUIBaseHandler):
    def prepare(self):
        pass

    @coroutine
    def get(self, *args, **kwargs):
        skin=self.get_cookie('miniuiSkin')
        # 保存用户设置
        db=self.settings['db']
        yield db.user.profile.save({'_id':self.current_user.get('username'),'skin':skin})
        self.session.delete('user')
        self.redirect('/app')

class LoginHandler(MINIUIBaseHandler):

    def prepare(self):
        """skip login valid"""
        pass

    def get(self, *args, **kwargs):
        self.render('miniui/login.html',site_name=self.settings['site_name'],title="用户登录",home_url=self.settings[constant.HOME_URL])

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
                                         'perms':[item['name'] for item in perms],
                                         'remote_ip':self.request.remote_ip,
                                         'login_time':datetime.datetime.now()})
                self.set_cookie('role',role_code)
                user_profile=yield db.user.profile.find_one({'_id':username})
                skin=user_profile.get('skin','default') if user_profile else 'default'
                self.set_cookie('miniuiSkin',skin)
                self.send_message("登录成功")
            else:
                self.send_message("密码错误",status_code=1)
        else:
            self.send_message("用户不存在或密码为空",status_code=1)

routes = [
    (r'/app/', IndexHandler),
    (r'/app$', IndexHandler),
    (r'/page/home', MINIUIBaseHandler,{'template':'miniui/home.html','title':'首页'}),
    (r'/page/menu', MINIUIBaseHandler,{'template':'miniui/menu.mgt.html',
                                       'title':'菜单管理',
                                       'role_map':{
                                           'get':'ptyh','post':'ptyh'
                                       }}),
    (r'/page/orgn', MINIUIBaseHandler,{'template':'miniui/orgn.mgt.html','title':'组织管理'}),
    (r'/page/employee', MINIUIBaseHandler,{'template':'miniui/employee.mgt.html','title':'员工管理'}),
    (r'/page/user', MINIUIBaseHandler,{'template':'miniui/user.mgt.html','title':'用户管理'}),
    (r'/page/login', LoginHandler),
    (r'/page/logout', LogoutHandler),
    (r'/page/perms', MINIUIBaseHandler,{'template':'miniui/perms.mgt.html','title':'权限管理'}),

    # 仅root角色的用户可以访问此url
    (r'/page/onlineuser', MINIUIBaseHandler,{'template':'miniui/onlineuser.mgt.html',
                                             'title':'在线用户管理',
                                             #'role_map':{'post':['root','ptyh']},
                                             'perm_map':{'post':['onlineuser:logout'],
                                                           'get':['onlineuser:logout']}}),

    #(r'/page/onlineuser', MINIUIBaseHandler,{'template':'miniui/onlineuser.mgt.html','title':'在线用户管理'}),
    (r'/page/choice_perms', MINIUIBaseHandler,{'template':'miniui/perms.choice.html','title':'选择权限'}),
    (r'/page/choice_menus', MINIUIBaseHandler,{'template':'miniui/menu.choice.html','title':'选择菜单'}),
    (r'/page/choice_users', MINIUIBaseHandler,{'template':'miniui/user.choice.html','title':'选择用户'}),
    (r'/page/role/menu', MINIUIBaseHandler,{'template':'miniui/role.menu.html','title':'角色菜单'}),
    (r'/page/role/user', MINIUIBaseHandler,{'template':'miniui/role.user.html','title':'角色用户'}),
    (r'/page/userprofile', MINIUIBaseHandler,{'template':'miniui/user.profile.html','title':'用户配置'}),
    (r'/page/role', MINIUIBaseHandler,{'template':'miniui/role.mgt.html','title':'角色管理'}),
]

