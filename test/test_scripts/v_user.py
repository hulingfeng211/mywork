# -*- coding:utf-8 -*-
import random
import time
import requests


def get_user_session(cookie=""):
    """
    获取用户session数据，包括session id和xsrf数据,在请求中使用
    """
    cookies={

    }
    cookie_str="msid=b9b1c197b6084731a1842e7f16eb0fe7; _xsrf=2|104e19af|70037b46a5ec209814572f53ddeb6b09|1457395534"
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
    return cookies

class Transaction(object):
    def __init__(self):
        self.custom_timers={}

    def run(self):
        url='http://localhost:10000/s/onlineuser'
        cookies=get_user_session()
        start=time.time()
        res=requests.get(url,headers={
            'content-type':'application/json',
            'X-Xsrftoken':cookies['X-Xsrftoken']
        },cookies=cookies)

        end=time.time()
        #assert res.status_code==200
        print res.status_code
        self.custom_timers['Example_Timer'] = end-start


if __name__ == '__main__':
    trans = Transaction()
    for i in range(1,1000):
        print i
        #time.sleep(1)
        trans.run()
    print trans.custom_timers
