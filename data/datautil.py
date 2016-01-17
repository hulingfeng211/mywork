# -*- coding:utf-8 -*-

import requests
import json
import argparse
import os
import sys

def import_menu(file):
    """
    导入系统的菜单数据
    :param file 菜单文件（json数据）的路径
    :return None
    """
    service_url="http://localhost:10000/s/menu"
    with open(file,'r') as f:
        #print dir(f)
        menu_str=''.join(f.readlines())
        menu_json=json.loads(menu_str)
        print type(menu_json)
        res=requests.post(service_url,data=menu_str,headers={
            'content-type':'application/json'
        })
        print res.text


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    # 参数前加--表示为可选参数，一般设置默认值
    # 不加--表示为必须的参数
    parser.add_argument('--op',default='menu',type=str,help="数据类型")
    args=parser.parse_args()
    #if args.op:
    #    print args.op
    menu_json_path=os.path.join(os.path.dirname(__file__),'menu.json')
    import_menu(menu_json_path)


