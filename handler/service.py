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
from tornado import escape
from tornado.web import RequestHandler

__author__ = 'george'


class MenuService(RequestHandler):
    """
    菜单服务
    """
    def get(self, *args, **kwargs):
        pass

    def post(self, *args, **kwargs):
        data=self.get_argument('data',None)
        remove_data=self.get_argument('remove',None)
        def iter_menu(menu):
            if menu.get('children',None):
               childrens=menu.get('children',None)

               for child_menu in childrens:
                   iter_menu(child_menu)
            else:
                yield self.settings['db'].menus.save(menu)
        if data:
            data_json=escape.json_decode(data)
            print data_json
            for menu in data_json:
                if menu.get('children'): #not leaf
                    pass

        if remove_data:
            #deal with remove_data
            pass
        print 'remove_data=',remove_data

routes=[
    (r'/s/menu',MenuService)
]

