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

import xlrd


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


def create_class(module_name,class_name):
    """获取类实例
    :param module_name 模块名
    :param class_name 类名
    :return 返回对应的类

    ：：用法
        cls=get_class(module_name,class_name)
        instance=cls(**kwargs) # 创建实例
    """
    module=__import__(module_name,globals(),locals(),['object'])
    cls=getattr(module,class_name)
    return cls

def read_xls(file_path,sheet_name):
    """读取xls中的数据
    :param file_path 文件路径
    :param sheet_name sheet名
    :return header,rows

    """
    workbook = xlrd.open_workbook('成绩单.xls')
    for booksheet in workbook.sheets():
        print booksheet.name
        for row in xrange(booksheet.nrows):
            for col in xrange(booksheet.ncols):
                print xlrd.cellname(row, col)
                print booksheet.cell(row, col).value


if __name__=="__main__":
    print generate_cookie_secret()

