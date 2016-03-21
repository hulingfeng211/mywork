 ## 数据库备份
 
> ` /usr/local/mongodb-3.2/bin/mongodump -d mywork  /home/george/PycharmProjects/mywork/data/`
 
 ## 数据库还原
 
> `/usr/local/mongodb-3.2/bin/mongorestore -d mywork2 -directoryperdb mywork`

## 复制集(Replica Set)

> 在生产环境下建议将每个节点部署在不同的机器上，如果使用的是虚拟化也需要将节点部署在不同的`HOST`上避免单点故障

### 环境检查N

- 确保每一个成员之间的网路是畅通的，每两个节点之间都需要能够访问
- 确保每一个成员之间可以通过`DNS`或`hostname`进行访问
- 确保防火墙设置开发了成员端口

### 过程N
- 给复制集取一个唯一的名字
> ` /usr/local/mongodb-3.2/bin/mongod --port 27018 --dbpath /home/george/rs0-0 --replSet rs0 --smallfiles --oplogSize 128`
> ` /usr/local/mongodb-3.2/bin/mongod --port 27019 --dbpath /home/george/rs0-1 --replSet rs0 --smallfiles --oplogSize 128`
> ` /usr/local/mongodb-3.2/bin/mongod --port 27020 --dbpath /home/george/rs0-2 --replSet rs0 --smallfiles --oplogSize 128`
> `mongo --port 27018`
> `rs.initiate()`
> `rs.add('george-pc:27019')` # add to replset members
> `rs.add('george-pc:27020')` # add to replset members
> `rs.remove('george-pc:27019')` # remove from replset members

# 系统管理A

## 认证（Authentication）

- SCRAM-SHA-1
-  MONGODB-CR
- x.509 Certificate Authentication

### 添加用户
> 非授权模式下启动`mongod`进程
> `use admin`　　　
> `db.createUser({user:"admin123",pwd:"dev123456",roles:[{role:"userAdminAnyDatabase",db:"admin"}]})`

### 重启`mongod`服务
> `george@george-pc:~/桌面$ /usr/local/mongodb-3.2/bin/mongod --syslog --fork --dbpath=/home/george/data --auth  `
> `about to fork child process, waiting until server is ready for connections.`  
> `forked process: 9912`
> `child process started successfully, parent exiting`

>  


