#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""==========================================================
+FileName:config.py
+Author: george
+mail:hulingfeng211@163.com
+Created Time:2015年07月22日 星期三 10时48分55秒
+Description:应用程序配置文件
+============================================================"""
import  os


# 开启程序的debug模式
DEBUG=True

# 指定静态文件的路经
STATIC_PATH=os.path.join(os.path.dirname(__file__),"static")

# 指定模版文件的路经
TEMPLATE_PATH=os.path.join(os.path.dirname(__file__),'templates')
# TEMPLATE_PATH=os.path.join(os.path.dirname(__file__),'front')

# session相关的配置
SESSION= {
    'driver':'redis',
    'driver_settings':dict(
        host = 'localhost',
        port = 6379,
        db = 4,
        max_connections = 1024
    )
}