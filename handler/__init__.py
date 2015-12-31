# -*- coding:utf-8 -*-

# 定义url模板
from core.common import MongoBaseHandler

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

]

