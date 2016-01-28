# -*- coding:utf-8 -*-
"""==========================================================
|
|
|       creater:george
|       create-time:2015-11-19 11:32:02
|       email:15921315347@163.com
|       description:系统常量
|
|
============================================================="""
__author__ = 'george'

# 登录CP的URL
LOGIN_URL = "http://fd.chinasws.com/CPServiceRelease/Service/Imp/ExternalService/MobileAppLogicService.svc/rest/login"

# 获取传阅明细的URL模板
MESSAGE_DEATIL_URL="https://fd.chinasws.com/MobileOA/MessageService.svc/message/%s"

# 获取传阅列表的URL模板
MESSAGE_LIST_URL="https://fd.chinasws.com/MobileOA/MessageService.svc/message?status=%s&lastDate=%s"

# 获取传阅评论的URL模板
COMMENT_URL="https://fd.chinasws.com/MobileOA/MessageService.svc/message/comments/%s"

# 在线浏览文档的URL模板
VIEW_FILE_ONLINE_URL='https://fd.chinasws.com/ReadAttachFile2/Service.svc/GetOnlineUrl'

# 获取传阅人员的URL模板
RECIVER_LIST_URL='https://fd.chinasws.com/MobileOA/MessageService.svc/message/user/%s'

# 添加评论
ADD_COMMENT_URL='https://fd.chinasws.com/MobileOA/MessageService.svc/message/comment/%s'

# 传阅确认
CONFIRM_MESSAGE_URL='https://fd.chinasws.com/MobileOA/MessageService.svc/message/%s'

# OA附件URL
ATTACH_FILE_URL='http://169.24.1.100/%s'

# Mongodb Uri
MONGO_URI="mongo_uri"
DB_NAME="db_name"

# redis配置
REDIS='redis'
HOST='host'
PORT='port'
SELECTED_DB='selected_db'
MAX_CONNECTIONS='max_connections'
CONNECTION_POOL='connection_pool'

