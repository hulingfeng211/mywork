# -*- coding:utf-8 -*-
"""==========================================================
|
|
|       creater:george
|       email:15921315347@163.com
|       description:工具类方法
|
|
|
============================================================="""
import base64
import uuid


def format_datetime(dt,format='%Y-%m-%d %H:%M:%S'):
    """
    根据指定格式转换日期类型
    :param dt datetime对象实例
    :return format 格式

    """
    return dt.strftime(format)

def generate_cookie_secret():
    """
    生成cookie secret
    """
    return base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)

if __name__=="__main__":
    print generate_cookie_secret()

