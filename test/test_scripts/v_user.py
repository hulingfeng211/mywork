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
    cookie_str="msid=8dc48fd69f80446fa2304786d54053dd; _xsrf=2|0e2212d9|be3a7f3c45c84f0d31f411bd2e67e1d6|1457438251"
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
        assert res.status_code==200
        #print res.status_code
        self.custom_timers['Example_Timer'] = end-start


if __name__ == '__main__':
    trans = Transaction()
    #for i in range(1,1000):
    #    print i
        #time.sleep(1)
    #    trans.run()
    trans.run()
    print trans.custom_timers
