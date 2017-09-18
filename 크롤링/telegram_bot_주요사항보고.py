# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 09:18:25 2017

@author: SH-NoteBook
"""
import threading
import time
import pandas as pd
import requests
from pandas.io.json import json_normalize
import json
import pandas as pd
import os
import re
import pandas as pd
import xlrd
import numpy as np
import telegram

auth = '002090c5e2dbaa01213f95ec7c16903849765293'
target_date = '20170915'
url_tmpl = 'http://dart.fss.or.kr/api/search.json?auth={auth}&start_dt={target_date}&end_dt={target_date}&dsp_tp=B&page_set=500'
url = url_tmpl.format(auth=auth,target_date=target_date)
r = requests.get(url)
jo = json.loads(r.text)
result = json_normalize(jo, 'list')
#E 라는게 코스피랑 코스닥에 상장되지 않은 기업 `

#만약 아직 새로운 공시가 올라오지 않았다면, 올라올때까지 while로 받아온다.
while result.empty:
    auth = '002090c5e2dbaa01213f95ec7c16903849765293'
    target_date = '20170915'
    url_tmpl = 'http://dart.fss.or.kr/api/search.json?auth={auth}&start_dt={target_date}&end_dt={target_date}&dsp_tp=B&page_set=500'
    url = url_tmpl.format(auth=auth,target_date=target_date)
    r = requests.get(url)
    jo = json.loads(r.text)
    result = json_normalize(jo, 'list')
    #E 라는게 코스피랑 코스닥에 상장되지 않은 기업 `
    print('while')
    time.sleep(30)
    
result = result[(result['crp_cls']!='E')].reset_index(drop=True)
result['web_address'] = 0
for i in range(len(result)):
    result.loc[i,'web_address'] = 'http://dart.fss.or.kr/dsaf001/main.do?rcpNo='+result.loc[i,'rcp_no']

my_token = '413222030:AAG-Yz8eDMfJ-XNCw9UceSVZ7RXNM8EDlvE' #토큰을 설정해 줍니다.
bot = telegram.Bot(token = my_token) #봇을 생성합니다.
bot.sendMessage(chat_id='@lshlsh135_test', text=str(result.loc[:,['crp_nm','rpt_nm']]))
latest_result = result
before_result = latest_result

def fun_a():
    global latest_result
    global before_result
    timer=threading.Timer(30,fun_a)
    print('test')
    timer.start()
    if before_result.equals(latest_result):
        #업뎃 된게 없으면 굳이 보내지 말아보자.
#        my_token = '413222030:AAG-Yz8eDMfJ-XNCw9UceSVZ7RXNM8EDlvE' #토큰을 설정해 줍니다.
#        bot = telegram.Bot(token = my_token) #봇을 생성합니다.
#        bot.sendMessage(chat_id='@lshlsh135_test', text="업데이트 되지 않았습니다.")
        r = requests.get(url)
        jo = json.loads(r.text)
        result = json_normalize(jo, 'list')
        #E 라는게 코스피랑 코스닥에 상장되지 않은 기업 
        result = result[(result['crp_cls']!='E')].reset_index(drop=True)
        result['web_address'] = 0
        for i in range(len(result)):
            result.loc[i,'web_address'] = 'http://dart.fss.or.kr/dsaf001/main.do?rcpNo='+result.loc[i,'rcp_no']
        latest_result = result
    else:
        union_result = pd.concat([before_result,latest_result]).drop_duplicates(keep=False)
        union_result = union_result.loc[:,['crp_nm','rpt_nm']]
        my_token = '413222030:AAG-Yz8eDMfJ-XNCw9UceSVZ7RXNM8EDlvE' #토큰을 설정해 줍니다.
        bot = telegram.Bot(token = my_token) #봇을 생성합니다.
        bot.sendMessage(chat_id='@lshlsh135_test', text=str(union_result))
        before_result = latest_result #과거 자료 업데이트
        r = requests.get(url)
        jo = json.loads(r.text)
        result = json_normalize(jo, 'list')
        #E 라는게 코스피랑 코스닥에 상장되지 않은 기업 
        result = result[(result['crp_cls']!='E')].reset_index(drop=True)
        result['web_address'] = 0
        for i in range(len(result)):
            result.loc[i,'web_address'] = 'http://dart.fss.or.kr/dsaf001/main.do?rcpNo='+result.loc[i,'rcp_no']
        latest_result = result
        
        

fun_a()

