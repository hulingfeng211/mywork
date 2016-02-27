# -*- coding:utf-8 -*-

import requests
import json
import argparse
import os
import sys
import pymongo
import config


def add_root_user():
    """
    脚本添加用户
    :param username 用户名
    :param email  邮箱
    :return None
    """
    client=pymongo.MongoClient(config.MONGO_URI)
    db=client['test']
    root={
      "_id": 1,
      "loginname": "15921315347@163.com",
      "name": "胡佐治",
      "email": "15921315347@163.com",
      "pwd": "96e79218965eb72c92a549dd5a330112",
      "role_id":"root",
      "nologin": 0,
      "superuser": 1
    }
    db.users.insert(root)
    #db.users.insert(
#        {'username':username,'email'}
#    )

    pass

def get_user_session(cookie=""):
    """
    获取用户session数据，包括session id和xsrf数据,在请求中使用
    """
    cookies={

    }
    cookie_str="msid=a0ca8a7cc8a247c5a1a172c418162b91; _xsrf=2|aad874ab|79226be0682275e091b9f3cfadb4bd0a|1456586828"
    for cookie in cookie_str.split(';'):
        item=cookie.strip().split('=')
        cookies[item[0].strip()]=item[1]
        if item[0].strip()=="_xsrf":
            cookies['X-Xsrftoken']=item[1]

    #login_url='http://localhost:10000/page/login'
    #data={'username':user,"pwd":pwd}
    #response=requests.post(login_url,data)
    #print response.headers
    #pass
    print cookies
    return cookies

def import_data(file,resources='menus'):
    """
    导入系统的菜单数据
    :param file 菜单文件（json数据）的路径
    :return None
    """
    service_url="http://localhost:10000/s/%s"%resources
    with open(file,'r') as f:
        #print dir(f)
        menu_str=''.join(f.readlines())
        menu_json=json.loads(menu_str)
        print type(menu_json)
        cookies=get_user_session()
        res=requests.post(service_url,data=menu_str,headers={
            'content-type':'application/json',
            'X-Xsrftoken':cookies['X-Xsrftoken']
        },cookies=cookies)
        print res.text



if __name__=="__main__":
    parser = argparse.ArgumentParser()
    # 参数前加--表示为可选参数，一般设置默认值
    # 不加--表示为必须的参数
    parser.add_argument('--op',default='menu',type=str,help="数据类型")
    args=parser.parse_args()
    #if args.op:
    #    print args.op

    # menus
    menu_json_path=os.path.join(os.path.dirname(__file__),'menu.json')
    import_data(menu_json_path,resources='menus')
    #
 # resources
    menu_json_path=os.path.join(os.path.dirname(__file__),'resource.json')
    import_data(menu_json_path,resources='resources')
    # # get_user_session()
    #
    #
    # # roles
    role_json_path=os.path.join(os.path.dirname(__file__),'roles.json')
    import_data(role_json_path,resources='roles')

    # add root
    #add_root_user()


