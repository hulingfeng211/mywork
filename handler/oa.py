# -*- coding:utf-8 -*-
"""==========================================================
|
|
|       creater:george
|       email:15921315347@163.com
|       description:与OA系统相关的调用
|
|
|
============================================================="""
from requests.auth import HTTPDigestAuth
from tornado.escape import json_encode, json_decode
from tornado.gen import coroutine
from tornado.httpclient import HTTPRequest, AsyncHTTPClient, HTTPError
import constant
from core.common import BaseHandler
import  urllib
import requests
import datetime

__author__ = 'george'

class CirculationHandler(BaseHandler):

    @coroutine
    def get(self, *args, **kwargs):
        message_id = args[0] if len(args)>0 else None
        if message_id:
            url=constant.MESSAGE_DEATIL_URL%message_id
        else:
            status=self.get_query_argument('status',0)
            now=datetime.datetime.now()
            now_str=now.strftime('%Y-%m-%d %H:%M:%S')
            lastDate=self.get_query_argument('last',now_str)
            url=constant.MESSAGE_LIST_URL%(status,lastDate)
        try:
            result=yield  self.send_request(url)
            self.write(result)
        except HTTPError,e:
            #raise HTTPError(code=401,message='lllll')
            #raise  e
            pass



class CirculationCommentHandler(BaseHandler):

    @coroutine
    def get(self, *args, **kwargs):
        """
        获取传阅的讨论
        """
        messageid=args[0] if len(args)>0 else 0
        url=constant.COMMENT_URL%messageid
        result=yield self.send_request(url)
        self.write(result)

class CirculationFileHandler(BaseHandler):
    """
    附件浏览的服务
    """

    @coroutine
    def post(self, *args, **kwargs):
        body=json_decode(self.request.body)
        if body and body.get('fileName',None) and body.get('filePath',None):
            data={
                "path":body.get('filePath',None),
                "fileEnternalName":body.get('fileName',None)
            }
            response=yield  self.send_request(url=constant.VIEW_FILE_ONLINE_URL,method='POST',body=json_encode(data),headers={
                'content-type':'application/json'
            },request_timeout=180*1000)
            result=urllib.unquote(response)[1:-1]
            self.write(result)


class CirculationUserHandler(BaseHandler):

    @coroutine
    def get(self, *args, **kwargs):
        """获取传阅人员"""
        messageid=args[0] if len(args)>0 else 0
        url=constant.RECIVER_LIST_URL%messageid
        result=yield self.send_request(url)
        self.write(result)

routes= [
    (r'/circulations',CirculationHandler),
    (r'/circulations/(.+)',CirculationHandler),
    (r'/circulation/comments/(.+)',CirculationCommentHandler),
    (r'/circulation/(.+)/user',CirculationUserHandler),
    (r'/circulation/attachfile',CirculationFileHandler),
]
