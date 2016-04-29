#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""==========================================================
+FileName:config.py
+Author: george
+mail:hulingfeng211@163.com
+Created Time:2015年07月22日 星期三 10时48分55秒
+Description:应用程序配置文件,所有大写的属性将会被传递给RequestHandler的settings,可通过settings['name']进行获取
+============================================================"""
import os
from tornadoredis import ConnectionPool

# 开启程序的debug模式
DEBUG = True

# 指定静态文件的路经
STATIC_PATH = os.path.join(os.path.dirname(__file__), "static")
# 静态资源的url前缀，默认是/static/
STATIC_URL_PREFIX="/mywork/static/"
# 站点的URL前缀，增加前缀后需要修改菜单中的URL与此进行前缀进行匹配
# 增加此选项的目的是为了在部署时可以使用二级或多级目录的方式部署
SITE_URL_PREFIX = "/mywork"

# 指定模版文件的路经
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'templates')
# TEMPLATE_PATH=os.path.join(os.path.dirname(__file__),'front')

# REDIS Server相关配置
REDIS_HOST = '192.168.2.14'
REDIS_PORT = 6379
MAX_CONNECTIONS = 1024
REDIS_DB = 5
SESSION_DB= 4



CONNECTION_POOL=ConnectionPool(wait_for_available=True,**dict(
    host=REDIS_HOST,
    port=REDIS_PORT
))
# session相关的配置
# redis as session store
SESSION = {
     'driver': 'redis',#memory/redis
     'force_persistence': True,
     'driver_settings': dict(
         host=REDIS_HOST,
         port=REDIS_PORT,
         db=SESSION_DB,
         #connection_pool=CONNECTION_POOL
         max_connections=MAX_CONNECTIONS
     )
 }

# 生成方法 core/utils/generate_cookie_secret
COOKIE_SECRET = '0jVZzvkPTLi8d7UN5twSrTIb247XcEwklP2O3hiLAoM='

# 用户登录的URL
LOGIN_URL = SITE_URL_PREFIX +"/page/login"


# 开启跨站点的请求伪造保护
XSRF_COOKIES = True

# MONGODB设置
MONGO_URI = "mongodb://192.168.2.14:27017/"
DB_NAME = 'mywork'

#短信中心的数据库名词
SMSCENTER_DB_NAME='smscenter'

# 站点设置
SITE_NAME = "XXX管理系统"

# 超级管理员的角色编码
ROOT_ROLE_CODE = 'root'

# 访客用户的角色编码
GUEST_ROLE_CODE = 'guest'

# 最大的轮询超时时间
MAX_POLLING_TIMEOUT = 20

# 网络代理设置
NETWORK_PROXY={'https':'https://192.168.2.7:3128',
               'http':'http://192.168.2.7:3128'}



