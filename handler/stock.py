# -*- coding:utf-8 -*-
"""==========================================================
|
|
|       creater:george
|       email:15921315347@163.com
|       description:tornado股票筛选系统
|
|
|
============================================================="""
import requests
import pandas as pd
from tornado.gen import coroutine
from tornado.web import url
import  os

from core.common import NUIMongoHandler, NUIBaseHandler

class DownloadCompanyThreeTable(NUIBaseHandler):
    """下载公司利润表、现金流量表、资产负债表"""

    @coroutine
    def get(self, *args, **kwargs):
        code=self.get_argument('code','')
        code=self.formate_code(code)
        # 下载现金流总表
        url='http://money.finance.sina.com.cn/corp/go.php/vDOWN_CashFlow/displaytype/4/stockid/%s/ctrl/all.phtml'%code
        res=requests.get(url)
        if res and res.status_code==200:
            all_lines=res.text.split('\n')
            pass
        pass




class DownloadCsrcindustry(NUIBaseHandler):

    def formate_code(self,code):
        while len(code)<6:
            code='0'+code
        return code

    @coroutine
    def get(self, *args, **kwargs):
        file_name='csrcindustry.xls'
        tmp=os.path.dirname(__file__).split('/')[:-1]
        tmp.append('static')
        tmp.append('stock')

        file_path='/'.join(tmp)+'/'+file_name
        df=pd.read_excel(file_path)
        columns=df.columns
        columns=map(lambda x:x.split('\n')[1],columns)
        columns=map(lambda x:x.lower().replace(' ','_').replace('.',''),columns)
        df.columns=columns
        df['securities_code']=df['securities_code'].astype(str).apply(self.formate_code)
        result=[]
        for item in range(len(df)):
            result.append(df.ix[item].to_dict())


        self.send_message(result)
        del df


routes = [
    url(r'/s/csrcindustry', NUIMongoHandler, {'cname': 'csrcindustry'},name='s.csrcindustry'),
    url(r'/s/csrcindustry/download', DownloadCsrcindustry,name='s.csrcindustry.download'),
    url(r'/s/download/company/tables', DownloadCompanyThreeTable,name='s.download.company.tables'),
     url(r'/page/csrcindustry', NUIBaseHandler, {'template': 'nui/stock/csrcindustry.mgt.html', 'title': '上市公司总表'},name='page.csrcindustry'),
]


