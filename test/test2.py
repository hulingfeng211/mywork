# -*- coding:utf-8 -*-
import logging
import urllib

import requests
from tornado import httpclient
from tornado.gen import coroutine
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from tornado.log import app_log, logging
from tornado.ioloop import IOLoop

logging = logging.getLogger('custome')
body = {
    "name": '15921315347',
    "pwd": 'A0DDFEB95A860E7DAF55D5062752',
    "content": 'OA短信(测试)',
    "stime": '',
    "sign": '外高桥造船',
    "type": 'pt',
    "extno": ''  # 视情况继续讨论
}
body['mobile'] = '15921315347'


# @coroutine
def complete(*args, **kwargs):
    pass


def send_message():
    url = 'http://sms.1xinxi.cn/asmx2/smsservice.aspx'
    # AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = httpclient.HTTPClient()
    request = HTTPRequest(url, method="POST", headers=header, body=urllib.urlencode(body))
    try:
        response = http_client.fetch(request)
        print response.body
    except httpclient.HTTPError as e:
        # HTTPError is raised for non-200 responses; the response
        # can be found in e.response.
        print e
        app_log.debug(e)
    except Exception as e:
        # Other errors are possible, such as IOError.
        app_log.debug(e)
    http_client.close()  # try:
#     request = HTTPRequest(url, method="POST", headers=header, body=urllib.urlencode(body))
#     response = AsyncHTTPClient().fetch(request, callback=complete)
# except Exception, e:
#     app_log.log(e)


if __name__ == '__main__':
    header = {
        "content-type": "application/x-www-form-urlencoded"
    }

    # res=requests.post('http://sms.1xinxi.cn/asmx/smsservice.aspx',data=body)
    # if res and res.status_code==200:
    #    pass
    send_message()
    # IOLoop.current().run_sync(send_message)
