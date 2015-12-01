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
from tornado.concurrent import Future
from tornado.gen import coroutine
from tornado.web import RequestHandler

__author__ = 'george'


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
        self.render('chat/index.html',messages=global_message_buffer.cache)


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

routes  = [
    (r'/chat/',MainHandler),
    (r'/chat/a/message/new',MessageNewHanlder),
    (r'/chat/a/message/updates',MessageUpdatesHandler)
]
