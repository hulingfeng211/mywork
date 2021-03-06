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

import functools
from copy import copy
from urllib import urlencode

import redis
import tornadoredis
from bson import ObjectId
import re
from tornado import gen
from tornado.escape import json_decode
from tornado.log import gen_log
from tornado.web import escape, HTTPError, urlparse
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from datetime import datetime
from torndsession.sessionhandler import SessionBaseHandler

import config
import constant
from core import bson_encode, is_json_request, clone_dict_without_id, clone_dict
from core.treeutils import to_list
from core.utils import format_datetime
from tornado.gen import coroutine
import ast

__author__ = 'george'

DEFAULT_HEADERS = {
    'content-type': 'application/json'
}


def get_query_args(request):
    """
    dept_id=569ca74805b6057d184b4f4c&pageIndex=0&pageSize=10&sortField=&sortOrder=&_=1453162105840
    """
    other = {}
    q = {}  # 查询表达式 {'name':'aaa'} 参见mongodb的查询规范
    p = {}  # 文档选取的字段{field1:1,field2:1,field3:0}等
    s = {}  # 排序规则
    except_key = ['pageIndex', 'pageSize', 'sortField', 'sortOrder', '_']
    try:
        for k, v in request.query_arguments.items():
            if k == '_v':
                continue
            if k == 'q':  # ?????
                # q = ast.literal_eval(v[0])
                q = json.loads(v[0])
                continue
                pass
            if k == 'p':  # ???
                # p = ast.literal_eval(v[0])
                p = json.loads(v[0])
                continue
                pass
            if k == 's':  # ??
                # s = ast.literal_eval(v[0])
                s = json.loads(v[0])
                continue
            if k in except_key:
                continue

            if len(v) > 1:
                other[k] = {"$in": v}
            else:
                other[k] = v[0]
    except ValueError, e:
        gen_log.error(e)
    #
    # return dict(q,**other), p, s
    return dict(q, **other), p, s


def authenticated(method):
    """Decorate methods with this to require that the user be logged in.

    If the user is not logged in, they will be redirected to the configured
    `login url <RequestHandler.get_login_url>`.

    If you configure a login url with a query parameter, Tornado will
    assume you know what you're doing and use it as-is.  If not, it
    will add a `next` parameter so the login page knows where to send
    you once you're logged in.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            # 如果是ajax的请求，不使用302的重定向
            is_ajax=self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'

            if self.request.method in ("GET", "HEAD") and not is_ajax:
                url = self.get_login_url()
                if "?" not in url:
                    if urlparse.urlsplit(url).scheme:
                        # if login url is absolute, make next absolute too
                        next_url = self.request.full_url()
                    else:
                        next_url = self.request.uri
                    url += "?" + urlencode(dict(next=next_url))
                self.redirect(url)
                return
            self.send_error(status_code=403,reason="未经认证或认证过期，请重新登录进行认证.")
            #raise HTTPError(403,reason="未经认证或认证过期，请重新登录进行认证.")
        return method(self, *args, **kwargs)
    return wrapper

class BaseHandler(SessionBaseHandler):

    # def initialize(self):
    #     self.redis_client=tornadoredis.Client(connection_pool=self.settings[constant.CONNECTION_POOL],selected_db=self.settings[constant.REDIS_DB])
    #     self.redis_client.connect()

    @coroutine
    def prepare(self):
        current_user = self.current_user
        if not current_user:
            # self.redirect('/f/index.html',permanent=False)
            # self.set_status(status_code=401,reason='用户未授权')
            self.send_error(status_code=403, reason='用户未登录')
            # self.redirect('/f/index.html',permanent=False)
            # raise HTTPError(code=401,message='未授权')
            # self.finish()

    #@coroutine
    def get_current_user(self):
        sid = self.session.id
        current_user= self.session.get('user', None)
        return current_user
        # if not current_user:
        #     #self.client.publish(self.channel_name, self.request.body)
        #     channel_name='session_time_out_%s'%sid
        #     self.redis_client.publish(channel_name,1)
        #     # 当前登录用户为空的时候给用户5秒的请求延时
        #
        #     #yield gen.sleep(5)
        #     pass
        # else:
        #     #channel_name='session_time_out_%s'%sid
        #     #self.redis_client.publish(channel_name,0)
        #     return current_user

    def on_finish(self):
        # todo update session expire when client call service.
        # SessionBaseHandler.on_finish()

        # if hasattr(self,'redis_client') and self.redis_client.connection.connected():
        #     self.redis_client.disconnect()
        self.session.set('last_access_time', datetime.now())
        super(BaseHandler, self).on_finish()

    @coroutine
    def send_request(self, url, body=None, method='GET', headers=DEFAULT_HEADERS, *args, **kwargs):
        """
        发送HTTP请求，并返回请求后的结果
        """
        url = url.replace(' ', '%20')

        userCd = self.current_user.get('userCd', None)
        pwd = self.current_user.get('pwd', None)
        request = HTTPRequest(url=url, method=method, body=body, auth_username=userCd,
                              auth_password=pwd, auth_mode='digest', validate_cert=False, headers=headers, **kwargs)
        response = yield AsyncHTTPClient().fetch(request)
        if response and response.code == 200:
            raise gen.Return(response.body)
        else:
            raise gen.Return(None)

    def send_message(self, obj, status_code=0,total=None):
        """
        发送消息到客户端
        :param obj 带发送到客户端的对象一个字典对象
        :param status_code 状态码
        """
        # todo
        # if isinstance(obj,dict):
        self.set_header("content-type", "application/json")
        if  not total :
            data={"data": obj, "status_code": status_code,"total":len(obj) if type(obj)==list else 0}
            self.write(bson_encode(data))
        else:
            self.write(bson_encode({"data": obj, "status_code": status_code,"total":total }))


class NUIBaseHandler(BaseHandler):
    @authenticated
    def prepare(self):
        """1.检查用户的角色(role)和权限(perms),从redis中获取
           2.获取前端url中传入的查询参数
        """
        # 检查用户的角色和权限，从redis中获取
        self.page_index=int(self.get_query_argument('pageIndex',0))
        self.page_size=int(self.get_query_argument('pageSize',20))
        self.sort_field=self.get_query_argument('sortField','')
        self.sort_order=self.get_query_argument('sortOrder','desc')

        method=self.request.method.lower()
        default_guest_role_code=self.settings[constant.GUEST_ROLE_CODE]
        default_root_role_code=self.settings[constant.ROOT_ROLE_CODE]

        # 超级管理员可以做任何操作
        if self.current_user.get('role')==default_root_role_code:
            return

        def can_pass():
            """请求是否能通过"""
            role_map=self.role_map.get(method,{}) if hasattr(self,'role_map') else {}
            perm_map=self.perm_map.get(method,{}) if hasattr(self,'perm_map') else {}
            result=True
            # 没有进行配置表示只要登录的用户即可进行访问
            if not role_map and not perm_map:
                return result

            if role_map and self.current_user.get('role',None)  in self.role_map.get(method):
                pass
            elif perm_map and [item for item in self.perm_map.get(method)  if item in self.current_user.get('perms',None)]:
                pass
            else:
                result = False
            return result

        if not can_pass():
            self.send_error(status_code=401,reason="用户没有权限")


    def initialize(self, *args, **kwargs):
        if kwargs:
            for key, val in kwargs.items():
                if not hasattr(self, key):
                    setattr(self, key, val)
        super(NUIBaseHandler, self).initialize()

    def get(self, *args, **kwargs):
        """提供默认的get方法的实现,如果template属性存在则进行页面模板的绘制后输出
        需要在定义url模板的时候指定template和title

        (r'/s/perms',MINIUIBaseHandler,{'template':'miniui/perm.mgt.html','title':'权限管理'}),

        """
        if hasattr(self,'template') and hasattr(self,'title'):
            self.render(self.template, title=self.title,has_perm=self.has_perm,has_role=self.has_role)
        else:
            raise HTTPError(405)

    def has_perm(self,perm):
        """判断用户有没有某权限"""
        user_perms=self.current_user.get('perms',None)
        return perm in user_perms if user_perms else False

    def has_role(self,role):
        user_role=self.current_user.get('role',[])
        return role in user_role if user_role else False

    @coroutine
    def write_page(self,cursor,*args,**kwargs):
        """向浏览器输出一页数据
        :param cursor mongodb的数据库游标
        :param pageIndex 浏览器传入的当前页码
        :param pageSize 当前页显示的行数"""
        total=yield cursor.count()
        s={}
        if self.sort_field:
           s[self.sort_field]=1 if self.sort_order =='desc' else -1
        if s:
            data=yield cursor.skip(self.page_index*self.page_size).limit(self.page_size).sort(s.items()).to_list(length=None)
        else:
            data=yield cursor.skip(self.page_index*self.page_size).limit(self.page_size).to_list(length=None)
        self.set_header('Content-Type', 'application/json;charset=UTF-8')
        self.write(bson_encode({'data':data,'total':total}))

    def write_error(self, status_code=500, **kwargs):
        self.finish('%s:%s'%(status_code,self._reason))


class NUITreeHandler(NUIBaseHandler):
    """
    组织服务
    """

    def initialize(self, *args, **kwargs):
        # cname 为对应的mongodb的集合的名字
        if kwargs:
            for key, val in kwargs.items():
                if not hasattr(self, key):
                    setattr(self, key, val)
        super(NUIBaseHandler, self).initialize()

    @coroutine
    def get(self, *args, **kwargs):


        q, p, s = get_query_args(self.request)
        db = self.settings['mongo_client'][self.db]

        if p:
            cursor = db[self.cname].find(q,p)
        else:
            cursor=db[self.cname].find(q)

        result = yield cursor.to_list(length=None)
        # print result
        self.write(bson_encode(result))

    @coroutine
    def post(self, *args, **kwargs):
        db = self.settings['mongo_client'][self.db]
        if 'application/json' in self.request.headers['content-Type']:
            body = json_decode(self.request.body)
            if body:
                data = body.get('data', None)
                remove_data = body.get('removed', None)
        else:
            data = self.get_argument('data', None)
            remove_data = self.get_argument('removed', None)

        if data:
            data_json = escape.json_decode(data) if type(data) == unicode else data
            list = to_list(data_json, "-1", "children", "id", "pid",self.current_user.get('userid'))
            for i, item in enumerate(list):
                yield db[self.cname].save(item)

        if remove_data:
            data_json = escape.json_decode(remove_data)
            list = to_list(data_json, "-1", "children", "id", "pid",self.current_user.get('userid'))
            for item in list:
                yield db[self.cname].remove({"_id": item['id']})


class NUIMongoHandler(NUIBaseHandler):
    """通用的mongodb的Handler，封装简单的CRUD的操作"""

    def is_object_id(self, id_str):
        """判断字符串是不是objectid的str"""
        pattern = '[a-f\d]{24}'
        return len(re.findall(pattern, str(id_str))) > 0

        pass

    def initialize(self, *args, **kwargs):
        # cname 为对应的mongodb的集合的名字
        if kwargs:
            for key, val in kwargs.items():
                if not hasattr(self, key):
                    setattr(self, key, val)
        super(NUIMongoHandler, self).initialize()

    @coroutine
    def get(self, *args, **kwargs):

        id = args[0] if len(args) > 0 else None
        if id:
            #db = self.settings['db']
            db = self.settings['mongo_client'][self.db]
            obj = yield db[self.cname].find_one({"_id": ObjectId(id) if self.is_object_id(id) else id})
            self.write(bson_encode(obj))
            return

        q, p, s = get_query_args(self.request)

        pageIndex = int(self.get_query_argument('pageIndex', 0))
        pageSize = int(self.get_query_argument('pageSize', 10))

        if self.sort_field:
            s[self.sort_field]=1 if self.sort_order=='desc' else -1

        db = self.settings['mongo_client'][self.db]
        cursor = db[self.cname].find(q)
        if not p:
            if not s:
                objs = yield cursor.skip(pageIndex * pageSize).limit(pageSize).to_list(length=None)
            else:
                objs = yield cursor.skip(pageIndex * pageSize).limit(pageSize).sort(s.items()).to_list(length=None)

        else:
            cursor = db[self.cname].find(q, p)
            if not s:
                objs = yield cursor.skip(pageIndex * pageSize).limit(pageSize).to_list(length=None)
            else:
                objs = yield cursor.skip(pageIndex * pageSize).limit(pageSize).sort(s.items()).to_list(length=None)

        total = yield cursor.count()
        result = {
            'total': total,
            'data': objs
        }
        self.write(bson_encode(result))

    @coroutine
    def put(self, *args, **kwargs):
        """接受用户的请求对文档进行更新
        :param args url路径的参数 """
        if is_json_request(self.request):
            body = json.loads(self.request.body)
        else:
            self.send_error(reason="仅支持Content-type:application/json")

        db = self.settings['mongo_client'][self.db]
        id = body.get('_id', None)
        if id :  # update
            body['update_time'] = format_datetime(datetime.now())
            body['update_user'] = self.current_user.get('userid', '')

            yield db[self.cname].update({"_id": ObjectId(id) if self.is_object_id(id) else id}, {
                "$set": clone_dict(body)
            })
        self.send_message("保存成功")

    @coroutine
    def delete(self, *args, **kwargs):
        id = args[0] if len(args) > 0 else None
        if id:
            yield self.db[self.cname].remove({"_id": ObjectId(id) if self.is_object_id(id) else id})

    @coroutine
    def post(self, *args, **kwargs):
        if is_json_request(self.request):
            body = json.loads(self.request.body)
            body = body.get('data', None)
        else:
            body = self.get_argument('data', None)
            body = escape.json_decode(body) if body else {}
            # self.send_error(reason="仅支持Content-type:application/json")
            # return

        db = self.settings['mongo_client'][self.db]
        for row in body:
            id = row.get('id', None)
            if row.get('_state', None) == 'removed':
                if self.is_object_id(id):
                    yield db[self.cname].remove({"_id": ObjectId(id)})

            if id and self.is_object_id(id):  # update
                row['update_time'] = format_datetime(datetime.now())
                row['update_user'] = self.current_user.get('userid', '')
                yield db[self.cname].update({"_id": ObjectId(id) if self.is_object_id(id) else id}, {
                    "$set": clone_dict(row, without=[])
                })

            else:
                obj = clone_dict(row)
                obj['id'] = ObjectId()
                obj['_id'] = obj['id']

                obj['create_time'] = format_datetime(datetime.now())
                obj['create_user'] = self.current_user.get('userid', '')
                yield db[self.cname].insert(obj)
        # self.write(generate_response(message="保存成功"))
        self.send_message("保存成功")


if __name__ == "__main__":
    from tornado.gen import IOLoop, coroutine
    import motor

    client = motor.MotorClient()
    db = client['test']


    @coroutine
    def f():
        yield db['servers'].insert({'a': 'b'})


    ioloop = IOLoop.current()
    ioloop.run_sync(f)
