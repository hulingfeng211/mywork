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
import logging
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

    @coroutine
    def post(self, *args, **kwargs):
        """
        如果有传阅编号则进行传阅的确认，没有传阅编号则是进行新传阅的新增
        """
        msgserid=args[0] if len(args)>0 else None
        content=json_decode(self.request.body)
        if msgserid and content.get('content',None): #confirm ciruclation
            url=constant.CONFIRM_MESSAGE_URL%msgserid
            res=yield self.send_request(url=url,method='POST',body=json_encode({
                'confirmContent':content.get('content')
            }))
            self.write(res)


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

    @coroutine
    def post(self, *args, **kwargs):
        """
        添加讨论
        """
        messageid=args[0] if len(args)>0 else 0
        comment_dict=json_decode(self.request.body)
        comment=comment_dict.get('comment',None)
        if comment and messageid>0:
            # post to oa db
            url=constant.ADD_COMMENT_URL%messageid
            res=yield self.send_request(url,method='POST',body=json_encode({
                'comment':comment
            }))
            self.write(res)

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
            response=yield  self.send_request(url=constant.VIEW_FILE_ONLINE_URL,method='POST',body=json_encode(data),request_timeout=180*1000)
            result=urllib.unquote(response)[1:-1]
            self.write(result)

    @coroutine
    def get(self, *args, **kwargs):
        file_path=self.get_query_argument('filePath',None)
        if  file_path:
            url=constant.ATTACH_FILE_URL%file_path
            #file =yield  self.send_request(url)
            self.write(url)


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
