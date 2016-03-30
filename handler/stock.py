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
from datetime import datetime

import pandas as pd
from bson import ObjectId
from tornado.gen import coroutine
from tornado.web import url
import  os

import constant
from core.common import NUIMongoHandler, NUIBaseHandler
from core.utils import format_datetime


class DownloadCompanyThreeTable(NUIBaseHandler):
    """下载公司利润表、现金流量表、资产负债表"""

    @coroutine
    def get(self, *args, **kwargs):
        code=self.get_argument('code','')
        # 下载现金流总表
        urls=[
            ('balancesheet','http://money.finance.sina.com.cn/corp/go.php/vDOWN_BalanceSheet/displaytype/4/stockid/%s/ctrl/all.phtml'%code),
            ('profitstatement','http://money.finance.sina.com.cn/corp/go.php/vDOWN_ProfitStatement/displaytype/4/stockid/%s/ctrl/all.phtml'%code),
            ('cashflow','http://money.finance.sina.com.cn/corp/go.php/vDOWN_CashFlow/displaytype/4/stockid/%s/ctrl/all.phtml'%code)
            ]
        db=self.settings['db']
        for cname,url in urls:
            file_path=self.download_file(url,code)
            result=[]
            with open(file_path,'rb') as f:
                for line in f:
                    line=line.decode('gb2312').encode('utf8')
                    line_arr=line.split('\t')
                    if len(line_arr)==1:
                        pass
                    else:
                        result.append(line_arr)
            df=pd.DataFrame(result)
            df=df.set_index(df[0])
            del df[0]

            df=df.T
            df['code']=code
            for i in range(len(df)):
                 data=df.ix[i+1].to_dict()
                 _id=ObjectId()
                 data['_id']=_id
                 data['id']=_id
                 data['create_user']=self.current_user.get('userid')
                 data['create_time']=format_datetime(datetime.now())
                 yield db[cname].insert(data)
            del df

        yield db.csrcindustry.update({'securities_code':code},{'$set':{'download_flag':1}})




        self.send_message('下载成功')

    def download_file(self, url,code,**kwargs):
        res = requests.get(url,proxies= self.settings[constant.NETWORK_PROXY],verify=False)
        file_name = res.headers.get('content-disposition', '')
        file_name = file_name.split(';')[1].split('=')[1]
        file_name = file_name.decode('gbk')
        dir_path = self.create_download_dir(code)
        file_path = dir_path + '/' + file_name
        if os.path.exists(file_path):
            return file_path

        if res and res.status_code == 200:
            with open(file_path, 'a') as f:
                f.write(res.content)
        return  file_path

    def create_download_dir(self,code):
        dir_path = os.path.dirname(__file__).split('/')[:-1]
        dir_path.append('upload')
        dir_path.append(code)
        dir_path = '/'.join(dir_path)
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        return dir_path


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
    url(r'/s/cashflow', NUIMongoHandler, {'cname': 'cashflow'},name='s.cashflow'),
    url(r'/s/csrcindustry/download', DownloadCsrcindustry,name='s.csrcindustry.download'),
    url(r'/s/download/company/tables', DownloadCompanyThreeTable,name='s.download.company.tables'),
     url(r'/page/csrcindustry', NUIBaseHandler, {'template': 'nui/stock/csrcindustry.mgt.html', 'title': '上市公司总表'},name='page.csrcindustry'),
    url(r'/page/cashflow', NUIBaseHandler, {'template': 'nui/stock/cashflow.mgt.html', 'title': '现金流量表'},name='page.cashflow'),
]


