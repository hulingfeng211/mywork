# 项目介绍
>tornado

# mongodb 

### 连接数据库
> #数据库连接字符串格式  
> mongodb://[username:password@]host1[:port1][,host2[:port2],...[,hostN[:portN]]][/[database][?options]]

>demo 1. mongodb://db1.example.net,db2.example.net:2500/?replicaSet=test

>demo 2. mongodb://db1.example.net,db2.example.net:2500/?replicaSet=test&connectTimeoutMS=300000


### 项目结构说明

- docs:  
    文档目录
    
### redis 过期事件通知
---

> redis自身支持事件通知机制，默认情况下是不开启的需要修改配置文件后重启，在`2.8`以上才支持.默认的配置文件在`/etc/redis/6379.conf`  
    `notify-keyspace-events Ex`   #大概818行
    开启后重启`redis`服务
    `sudo /etc/init.d/redis_6379 restart`
    
---

> 使用psubcribe进行订阅，通道名字为`'__keyevent@0__:expired'`
    在终端中通过`expire key timeout`设置`key`的超时时间
    
---
    
> 调整`redis.conf`中的`timeout`参数使得服务器关闭空闲的连接。暂定设置为20秒


### multi-mechanize压力测试
    



