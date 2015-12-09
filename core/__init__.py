# -*- coding:utf-8 -*-
import hashlib
from bson import ObjectId
import motor
import config
import constant

__author__ = 'george'
import json
from json import JSONEncoder

# init mongodb and redis client


def load_setting():
    """加载配置文件"""
    object_list = dir(config)
    setting = {}
    for item in object_list:
        if item.isupper():
            setting[item.lower()] = getattr(config, item)
    return setting

def generate_response(status='success',status_code=200,message='Success'):
    """生成返回消息"""
    return  json.dumps(dict({
        'status':status,
        'status_code':status_code,
        'message':message
    }))
def is_json_request(request):
    """判断是否是json的请求"""
    return 'application/json' in request.headers['Content-Type']

def clone_dict_without_id(obj):
    """复制一个字典对象，去除字典的id列"""
    #py 2.6.6不支持下列写法
    #return {key:val for key,val in  obj.items() if key!="_id" and key!="id"}
    result={}
    for item  in obj.items():
        if item[0]=='_id' or item[0]=="id":
            continue
        else:
            result[item[0]]=item[1]

class MongoEncoder(JSONEncoder):
    """针对mongodb的ObjectId的json序列化的封装"""
    def default(self, o,**kwargs):
        if isinstance(o,ObjectId):
            return str(o)
        else:
            return JSONEncoder.default(o,**kwargs)

def bson_encode(obj):
    """
    对mongodb数据文档进行json格式的序列化
    :param obj 需要进行json序列化文档的对象
    :return 返回序列化后的结果
    """
    return json.dumps(obj,cls=MongoEncoder)


def print_url(handlers):
    for item in handlers:
        print "url:%s method:get/post handler:%s"%(item._path ,item.handler_class)


def make_password(password):
    """生成用户的加密后的密码，默认采用md5算法"""
    return hashlib.md5(password).hexdigest()

def get_database():
    """
    获取mongodb的database对象
    :return 返回mongodb的database对象
    """
    client=motor.MotorClient(config.MONGO_URI)
    db=client[config.DB_NAME]
    return db


settings = load_setting()
settings['db'] = get_database()


if __name__ == "__main__":
    print load_setting()
