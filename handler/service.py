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
from bson import ObjectId
from tornado import escape
from tornado.escape import json_decode
from tornado.gen import coroutine
from tornado.web import RequestHandler
from core import clone_dict, bson_encode
from core.common import MINIUIBaseHandler
from core.treeutils import to_list

__author__ = 'george'

class UserPermService(MINIUIBaseHandler):
    """用户权限服务"""

    @coroutine
    def get(self, *args, **kwargs):
        key = self.get_argument('key',None)
        if key:
            db = self.settings['db']
            result=yield db.users.find({'id':ObjectId(key)},{'perms':1}).to_list(length=None)
            self.send_message(result)
        else:
            pass

    @coroutine
    def post(self, *args, **kwargs):
        print self.request.body
        pass

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
]

