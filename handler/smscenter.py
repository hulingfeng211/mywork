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
import tornadoredis
from tornado.gen import coroutine, Task
from tornado.web import url

import config
from core.common import NUIMongoHandler, NUIBaseHandler

class SendQueueHandler(NUIBaseHandler):
    """短信发送队列长度"""
    def initialize(self, *args, **kwargs):
        self.redis_client = tornadoredis.Client(host=config.REDIS_HOST, selected_db=config.SMSCENTER_REDIS_DB)
        self.redis_client.connect()
        pass

    @coroutine
    def get(self, *args, **kwargs):
        message_count=yield Task(self.redis_client.llen,config.SMSCENTER_MESSAGE_CHANNEL)
        backup_message_count=yield Task(self.redis_client.llen,config.SMSCENTER_BACKUP_MESSAGE_CHANNEL)
        self.write({
            'message_count':message_count,
            'backup_message_count':backup_message_count
        })
    def on_finish(self):
        if self.redis_client.connection.connected():
            self.redis_client.disconnect()
        super(SendQueueHandler,self).on_finish()

routes = [

    # 员工管理
    url(r'/s/message/list', NUIMongoHandler, {'cname': 'sendrecord','db':config.SMSCENTER_DB_NAME},name='s.message.list'),
    url(r'/s/error/list', NUIMongoHandler, {'cname': 'smslog','db':config.SMSCENTER_DB_NAME},name='s.error.list'),
    url(r'/s/recieve/list', NUIMongoHandler, {'cname': 'recv_sms','db':config.SMSCENTER_DB_NAME},name='s.recieve.list'),
    url(r'/page/message/list', NUIBaseHandler, {'template': 'nui/smscenter/smsmessage.mgt.html', 'title': '短信发送记录'},
        name='page.message.list'),
    url(r'/page/error/list', NUIBaseHandler, {'template': 'nui/smscenter/smslog.mgt.html', 'title': '错误日志记录'},
        name='page.error.list'),
    url(r'/portal/queue/count', NUIBaseHandler, {'template': 'nui/portal/portal.html', 'title': '短信队列portal'},
        name='portal.queue.count'),
    url(r'/s/message/queue/count',SendQueueHandler,name='s.message.queue.count')
    ]