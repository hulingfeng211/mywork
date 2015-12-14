# -*- coding:utf-8 -*-

# 定义url模板
from core.common import MongoBaseHandler

routes=[
    (r'/servers',MongoBaseHandler,{'cname':'servers'}),
    (r'/servers/(.+)',MongoBaseHandler,{'cname':'servers'}),
    (r'/events',MongoBaseHandler,{'cname':'events'}),
    (r'/events/(.+)',MongoBaseHandler,{'cname':'events'})

]

