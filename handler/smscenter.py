# -*- coding:utf-8 -*-
"""==========================================================
|
|
|       creater:george
|       email:15921315347@163.com
|       description:短信中心的相关内容
|
|
|
============================================================="""

# 公共的路由
from tornado.web import url

import config
from core.common import NUIMongoHandler, NUIBaseHandler

routes = [

    # 员工管理
    url(r'/s/message/list', NUIMongoHandler, {'cname': 'sendrecord','db':config.SMSCENTER_DB_NAME},name='s.message.list'),
    url(r'/s/error/list', NUIMongoHandler, {'cname': 'smslog','db':config.SMSCENTER_DB_NAME},name='s.error.list'),
    url(r'/s/recieve/list', NUIMongoHandler, {'cname': 'recv_sms','db':config.SMSCENTER_DB_NAME},name='s.recieve.list'),
    url(r'/page/message/list', NUIBaseHandler, {'template': 'nui/smscenter/smsmessage.mgt.html', 'title': '短信发送记录'},
        name='page.message.list'),
    url(r'/page/error/list', NUIBaseHandler, {'template': 'nui/smscenter/smslog.mgt.html', 'title': '错误日志记录'},
        name='page.error.list'),
    ]