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
from tornado.gen import coroutine
from tornado.web import RequestHandler
from core import clone_dict, bson_encode
from core.treeutils import to_list

__author__ = 'george'


class MenuService(RequestHandler):
    """
    菜单服务
    """

    @coroutine
    def get(self, *args, **kwargs):
        result = yield self.settings['db'].menus.find().to_list(length=None)
        #print result
        self.write(bson_encode(result))

    @coroutine
    def post(self, *args, **kwargs):
        data=self.get_argument('data',None)
        remove_data = self.get_argument('removed', None)

        if data:
            data_json=escape.json_decode(data)
            list = to_list(data_json,"-1","children","id","pid")
            print list
            print 'len(list):',len(list)
            for i,item in enumerate(list):
                yield self.settings['db'].menus.save(item)

        if remove_data:
            data_json = escape.json_decode(remove_data)
            list = to_list(data_json,"-1","children","id","pid")
            for item in list:
                yield self.settings['db'].menus.remove({"_id":item['id']})

routes=[
    (r'/s/menu',MenuService),
]

