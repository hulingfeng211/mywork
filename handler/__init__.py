# -*- coding:utf-8 -*-

# 定义url模板
from core.common import MongoBaseHandler

routes=[
    (r'/servers',MongoBaseHandler,{'cname':'servers'}),
    (r'/servers/(.+)',MongoBaseHandler,{'cname':'servers'}),

    (r'/events',MongoBaseHandler,{'cname':'events'}),
    (r'/events/(.+)',MongoBaseHandler,{'cname':'events'}),

    (r'/tasks',MongoBaseHandler,{'cname':'tasks'}),
    (r'/tasks/(.+)',MongoBaseHandler,{'cname':'tasks'}),

    (r'/projects',MongoBaseHandler,{'cname':'projects'}),
    (r'/projects/(.+)',MongoBaseHandler,{'cname':'projects'}),

    (r'/labels',MongoBaseHandler,{'cname':'labels'}),
    (r'/labels/(.+)',MongoBaseHandler,{'cname':'labels'}),

]

