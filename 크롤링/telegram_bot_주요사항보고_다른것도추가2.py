# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 15:22:21 2017

@author: SH-NoteBook
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 14:26:32 2017

@author: SH-NoteBook
"""

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
#잠깐 수시,공정공시만보자

pd.set_option('display.max_colwidth',-1)
auth = '002090c5e2dbaa01213f95ec7c16903849765293'
target_date = '20170918'
url_tmpl = 'http://dart.fss.or.kr/api/search.json?auth={auth}&start_dt={target_date}&end_dt={target_date}&bsn_tp=A001&bsn_tp=A002&bsn_tp=A003&bsn_tp=B001&bsn_tp=B002&bsn_tp=B003&page_set=500'
url = url_tmpl.format(auth=auth,target_date=target_date)
r = requests.get(url)
jo = json.loads(r.text)
result = json_normalize(jo, 'list')
url_tmpl='http://dart.fss.or.kr/api/search.json?auth={auth}&start_dt={target_date}&end_dt={target_date}&bsn_tp=I001&bsn_tp=I002&page_set=500'
url = url_tmpl.format(auth=auth,target_date=target_date)
r = requests.get(url)
jo = json.loads(r.text)
result2 = json_normalize(jo, 'list')
#E 라는게 코스피랑 코스닥에 상장되지 않은 기업 `

#만약 아직 새로운 공시가 올라오지 않았다면, 올라올때까지 while로 받아온다.
while (result.empty)&(result2.empty):
    auth = '002090c5e2dbaa01213f95ec7c16903849765293'
    target_date = '20170918'
    url_tmpl = 'http://dart.fss.or.kr/api/search.json?auth={auth}&start_dt={target_date}&end_dt={target_date}&bsn_tp=A001&bsn_tp=A002&bsn_tp=A003&bsn_tp=B001&bsn_tp=B002&bsn_tp=B003&page_set=500'
    url = url_tmpl.format(auth=auth,target_date=target_date)
    r = requests.get(url)
    jo = json.loads(r.text)
    result = json_normalize(jo, 'list')
    url_tmpl='http://dart.fss.or.kr/api/search.json?auth={auth}&start_dt={target_date}&end_dt={target_date}&bsn_tp=I001&bsn_tp=I002&page_set=500'
    url = url_tmpl.format(auth=auth,target_date=target_date)
    r = requests.get(url)
    jo = json.loads(r.text)
    result2 = json_normalize(jo, 'list')
    #E 라는게 코스피랑 코스닥에 상장되지 않은 기업 `
    print('while')
    time.sleep(30)

if not result2.empty:
    result2['first'] = 0
    for i in range(len(result2)):
        result2.loc[i,'first']=result2.loc[i,'rpt_nm'].find('단일판매')
    result2['second'] = 0
    for i in range(len(result2)):
        result2.loc[i,'second']=result2.loc[i,'rpt_nm'].find('풍문')
    result2['third'] = 0
    for i in range(len(result2)):
        result2.loc[i,'third']=result2.loc[i,'rpt_nm'].find('소송')
    result2['fourth'] = 0
    for i in range(len(result2)):
        result2.loc[i,'fourth']=result2.loc[i,'rpt_nm'].find('증자')
    result2['fifth'] = 0
    for i in range(len(result2)):
        result2.loc[i,'fifth']=result2.loc[i,'rpt_nm'].find('실적')
    
    result2 = result2[(result2['first']!=-1)|(result2['second']!=-1)|(result2['third']!=-1)|(result2['fourth']!=-1)|(result2['fifth']!=-1)]
    
if not (result.empty)&(result2.empty):
    result = pd.concat([result,result2])
    
    
result = result[(result['crp_cls']!='E')].reset_index(drop=True)
result['web_address'] = 0
for i in range(len(result)):
    result.loc[i,'web_address'] = 'http://dart.fss.or.kr/dsaf001/main.do?rcpNo='+result.loc[i,'rcp_no']

my_token = '413222030:AAG-Yz8eDMfJ-XNCw9UceSVZ7RXNM8EDlvE' #토큰을 설정해 줍니다.
bot = telegram.Bot(token = my_token) #봇을 생성합니다.
bot.sendMessage(chat_id='@lshlsh135_test', text=str(result.loc[:,['crp_nm','rpt_nm','web_address']]))
latest_result = result
before_result = latest_result

def fun_a():
    global latest_result
    global before_result
    global url
    global result2
    timer=threading.Timer(30,fun_a)
    print('test')
    timer.start()
    if before_result.equals(latest_result):
        #업뎃 된게 없으면 굳이 보내지 말아보자.
#        my_token = '413222030:AAG-Yz8eDMfJ-XNCw9UceSVZ7RXNM8EDlvE' #토큰을 설정해 줍니다.
#        bot = telegram.Bot(token = my_token) #봇을 생성합니다.
#        bot.sendMessage(chat_id='@lshlsh135_test', text="업데이트 되지 않았습니다.")
        url_tmpl = 'http://dart.fss.or.kr/api/search.json?auth={auth}&start_dt={target_date}&end_dt={target_date}&bsn_tp=A001&bsn_tp=A002&bsn_tp=A003&bsn_tp=B001&bsn_tp=B002&bsn_tp=B003&page_set=500'
        url = url_tmpl.format(auth=auth,target_date=target_date)
        r = requests.get(url)
        jo = json.loads(r.text)
        result = json_normalize(jo, 'list')
        url_tmpl='http://dart.fss.or.kr/api/search.json?auth={auth}&start_dt={target_date}&end_dt={target_date}&bsn_tp=I001&bsn_tp=I002&page_set=500'
        url = url_tmpl.format(auth=auth,target_date=target_date)
        r = requests.get(url)
        jo = json.loads(r.text)
        result2 = json_normalize(jo, 'list')
        
        if not result2.empty:
            result2['first'] = 0
            for i in range(len(result2)):
                result2.loc[i,'first']=result2.loc[i,'rpt_nm'].find('단일판매')
            result2['second'] = 0
            for i in range(len(result2)):
                result2.loc[i,'second']=result2.loc[i,'rpt_nm'].find('풍문')
            result2['third'] = 0
            for i in range(len(result2)):
                result2.loc[i,'third']=result2.loc[i,'rpt_nm'].find('소송')
            result2['fourth'] = 0
            for i in range(len(result2)):
                result2.loc[i,'fourth']=result2.loc[i,'rpt_nm'].find('증자')
            result2['fifth'] = 0
            for i in range(len(result2)):
                result2.loc[i,'fifth']=result2.loc[i,'rpt_nm'].find('실적')
            
            result2 = result2[(result2['first']!=-1)|(result2['second']!=-1)|(result2['third']!=-1)|(result2['fourth']!=-1)|(result2['fifth']!=-1)]
    
        if not (result.empty)&(result2.empty):
            result = pd.concat([result,result2])
        #E 라는게 코스피랑 코스닥에 상장되지 않은 기업 
        result = result[(result['crp_cls']!='E')].reset_index(drop=True)
        result['web_address'] = 0
        for i in range(len(result)):
            result.loc[i,'web_address'] = 'http://dart.fss.or.kr/dsaf001/main.do?rcpNo='+result.loc[i,'rcp_no']
        latest_result = result
    else:
        union_result = pd.concat([before_result,latest_result]).drop_duplicates(keep=False)
        union_result = union_result.loc[:,['crp_nm','rpt_nm','web_address']]
        if not union_result.empty:
            my_token = '413222030:AAG-Yz8eDMfJ-XNCw9UceSVZ7RXNM8EDlvE' #토큰을 설정해 줍니다.
            bot = telegram.Bot(token = my_token) #봇을 생성합니다.
            bot.sendMessage(chat_id='@lshlsh135_test', text=str(union_result))
        before_result = latest_result #과거 자료 업데이트
        url_tmpl = 'http://dart.fss.or.kr/api/search.json?auth={auth}&start_dt={target_date}&end_dt={target_date}&bsn_tp=A001&bsn_tp=A002&bsn_tp=A003&bsn_tp=B001&bsn_tp=B002&bsn_tp=B003&page_set=500'
        url = url_tmpl.format(auth=auth,target_date=target_date)
        r = requests.get(url)
        jo = json.loads(r.text)
        result = json_normalize(jo, 'list')
        url_tmpl='http://dart.fss.or.kr/api/search.json?auth={auth}&start_dt={target_date}&end_dt={target_date}&bsn_tp=I001&bsn_tp=I002&page_set=500'
        url = url_tmpl.format(auth=auth,target_date=target_date)
        r = requests.get(url)
        jo = json.loads(r.text)
        result2 = json_normalize(jo, 'list')
        
        if not result2.empty:
            result2['first'] = 0
            for i in range(len(result2)):
                result2.loc[i,'first']=result2.loc[i,'rpt_nm'].find('단일판매')
            result2['second'] = 0
            for i in range(len(result2)):
                result2.loc[i,'second']=result2.loc[i,'rpt_nm'].find('풍문')
            result2['third'] = 0
            for i in range(len(result2)):
                result2.loc[i,'third']=result2.loc[i,'rpt_nm'].find('소송')
            result2['fourth'] = 0
            for i in range(len(result2)):
                result2.loc[i,'fourth']=result2.loc[i,'rpt_nm'].find('증자')
            result2['fifth'] = 0
            for i in range(len(result2)):
                result2.loc[i,'fifth']=result2.loc[i,'rpt_nm'].find('실적')
            
            result2 = result2[(result2['first']!=-1)|(result2['second']!=-1)|(result2['third']!=-1)|(result2['fourth']!=-1)|(result2['fifth']!=-1)]
        
        if not (result.empty)&(result2.empty):
            result = pd.concat([result,result2])
        #E 라는게 코스피랑 코스닥에 상장되지 않은 기업 
        result = result[(result['crp_cls']!='E')].reset_index(drop=True)
        result['web_address'] = 0
        for i in range(len(result)):
            result.loc[i,'web_address'] = 'http://dart.fss.or.kr/dsaf001/main.do?rcpNo='+result.loc[i,'rcp_no']
        latest_result = result
        
        

fun_a()
