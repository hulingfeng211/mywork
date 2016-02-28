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
from dateutil import  tz


def format_datetime(dt,format='%Y-%m-%d %H:%M:%S'):
    """
    根据指定格式转换日期类型
    :param dt datetime对象实例
    :param format 日期格式
    :return format 格式

    """
    return dt.strftime(format)


def generate_cookie_secret():
    """
    生成cookie secret
    """
    return base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)


def utc_to_local(utctime):
    """转换UTC时间到本地格式
    :param utctime UTC时区的日期
    :return 本地时区的时间对象"""
    from_zone=tz.tzutc()
    to_zone=tz.tzlocal()
    utc=utctime.replace(tzinfo=from_zone)
    return utc.astimezone(to_zone)

if __name__=="__main__":
    print generate_cookie_secret()

