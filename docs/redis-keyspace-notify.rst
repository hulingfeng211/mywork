====================================
键空间通知（keyspace notification）
====================================
------------------------
副标题
------------------------
:Author: 胡佐治
:Version: v1.0
:Copyright: 公开

.. contents::


.. Note::  该功能在`redis`2.8上才得到支持，使用时要加以注意。默认情况下是不打开的需要在配置文件中进行修改并重启服务器后才能支持。

功能概览
=============
键空间通知使得客户端可以通过订阅频道或模式， 来接收那些以某种方式改动了 Redis 数据集的事件。

以下是一些键空间通知发送的事件的例子：

1. 所有修改键的命令。
2. 所有接收到 LPUSH 命令的键。
3. 0 号数据库中所有已过期的键。

事件的类型
=============


配置
=============

命令产生的通知
===================

过期通知的发送时间
===================



