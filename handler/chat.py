# -*- coding:utf-8 -*-
"""==========================================================
|
|
|       creater:george
|       email:15921315347@163.com
|       description:tornado聊天室程序
|
|
|
============================================================="""
import uuid
import time
from tornado.concurrent import Future
from tornado.escape import json_encode
from tornado.gen import coroutine, Task, engine
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, asynchronous
import tornadoredis
import constant

__author__ = 'george'


class LongPollingHandler(RequestHandler):

    def initialize(self, *args, **kwargs):
        # self.client=tornadoredis.Client(connection_pool=self.settings[constant.CONNECTION_POOL],selected_db=self.settings[constant.REDIS][constant.SELECTED_DB])
        self.client = tornadoredis.Client(selected_db=5, host='localhost', port=6379)
        self.client.connect()
        self.channel_name = kwargs.get('channel_name', None)

    @asynchronous
    def get(self, *args, **kwargs):
        self.get_data()

    @asynchronous
    def post(self, *args, **kwargs):
        self.get_data()

    @engine
    def subscribe(self):
        yield Task(self.client.subscribe, self.channel_name)
        self.client.listen(self.on_message)

    # @coroutine
    def get_data(self):
        if self.request.connection.stream.closed():
            return
        self.subscribe()
        num = 90  # 设置超时时间,

        IOLoop.current().add_timeout(time.time() + num, lambda: self.on_timeout(num))

    def on_timeout(self, num):
        self.send_data(json_encode({'name': '', 'msg': ''}))
        if self.client.connection.connected():
            self.client.disconnect()

    def send_data(self, body):
        if self._finished:
            # if self.request.connection.stream.closed():
            return
        self.set_header('Content-Type', 'application/json;charset=UTF-8')
        self.write(body)
        self.finish()

    def on_message(self, msg):
        if msg.kind == 'message':
            self.send_data(str(msg.body))
        elif msg.kind == 'unsubscribe':
            self.client.disconnect()

    def on_finish(self):
        if self.client.subscribed:
            self.client.unsubscribe(self.channel_name)
        super(LongPollingHandler, self).on_finish()

    def check_xsrf_cookie(self):
        pass


class PublisHandler(RequestHandler):
    def initialize(self, *args, **kwargs):
        # self.client=tornadoredis.Client(connection_pool=self.settings[constant.CONNECTION_POOL],selected_db=self.settings[constant.REDIS][constant.SELECTED_DB])
        self.client = tornadoredis.Client(selected_db=5, host='localhost', port=6379)
        self.client.connect()
        self.channel_name = kwargs.get('channel_name', None)

    def post(self, *args, **kwargs):
        self.client.publish(self.channel_name, self.request.body)

    def get(self, *args, **kwargs):
        self.render('chat/pubsub.html');

    def on_finish(self):
        self.client.disconnect()
        super(PublisHandler, self).on_finish()

    def check_xsrf_cookie(self):
        pass


class MessageBuffer(object):
    def __init__(self):
        self.waiters = set()
        self.cache = []
        self.cache_size = 200

    def wait_for_message(self, cursor=None):
        print cursor
        result_feture = Future()
        if cursor:
            new_count = 0
            for msg in reversed(self.cache):
                if msg['id'] == cursor:
                    break
                new_count += 1
            if new_count:
                result_feture.set_result(self.cache[-new_count:])
                return result_feture
        self.waiters.add(result_feture)
        return result_feture

    def cancel_wait(self, future):
        self.waiters.remove(future)
        future.set_result([])

    def new_message(self, messages):
        print 'send new message to %r listener' % len(self.waiters)
        for future in self.waiters:
            future.set_result(messages)

        self.waiters = set()
        self.cache.extend(messages)
        if len(self.cache) > self.cache_size:
            self.cache = self.cache[-self.cache_size:]


global_message_buffer = MessageBuffer()


class MainHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.render('chat/index.html', messages=global_message_buffer.cache)


class MessageNewHanlder(RequestHandler):
    def post(self, *args, **kwargs):
        message = {
            'id': str(uuid.uuid4()),
            'body': self.get_argument('body', '')
        }
        message['html'] = self.render_string('chat/message.html', message=message)
        if self.get_argument('next', None):
            self.redirect(self.get_argument('next'))
        else:
            self.write(message)
        print 'new message entry'
        global_message_buffer.new_message([message])


class MessageUpdatesHandler(RequestHandler):
    @coroutine
    def post(self, *args, **kwargs):
        print 'message updates calling....'
        print self.request.body
        cursor = self.get_argument('cursor', None)
        self.future = global_message_buffer.wait_for_message(cursor=cursor)
        messages = yield self.future
        if self.request.connection.stream.closed():
            return
        self.write(dict(messages=messages))


routes = [
    (r'/chat/', MainHandler),
    (r'/chat/a/message/new', MessageNewHanlder),
    (r'/chat/a/message/updates', MessageUpdatesHandler),
    (r'/polling', LongPollingHandler, dict(channel_name='msg_channel')),
    (r'/pushmsg', PublisHandler, dict(channel_name='msg_channel')),
]
