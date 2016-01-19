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
from core.common import MongoBaseHandler, MINIUIMongoHandler

# 公共的路由
routes=[

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
    (r'/s/menus',MongoBaseHandler,{'cname':'menus'}),
    (r'/s/menus/(.+)',MongoBaseHandler,{'cname':'menus'}),
    # 用户管理
    (r'/s/users',MINIUIMongoHandler,{'cname':'users'}),
    (r'/s/users/(.+)',MINIUIMongoHandler,{'cname':'users'}),

]

