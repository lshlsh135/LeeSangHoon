# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 10:39:45 2017

@author: SH-NoteBook
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 09:35:28 2017

@author: SH-NoteBook
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 16:33:21 2017

@author: SH-NoteBook
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 15:40:00 2017

@author: SH-NoteBook
"""

import requests
from pandas.io.json import json_normalize
import json
import pandas as pd
import os
import re
import pandas as pd
import xlrd
import numpy as np

auth = '002090c5e2dbaa01213f95ec7c16903849765293'
target_date = '20170814'
url_tmpl = 'http://dart.fss.or.kr/api/search.json?auth={auth}&start_dt={target_date}&end_dt={target_date}&bsn_tp=A001&bsn_tp=A002&bsn_tp=A003&page_set=500'
url = url_tmpl.format(auth=auth,target_date=target_date)
r = requests.get(url)
jo = json.loads(r.text)
result = json_normalize(jo, 'list')
#E 라는게 코스피랑 코스닥에 상장되지 않은 기업 
result = result[(result['crp_cls']!='E')].reset_index(drop=True)
#정정되서 새로 나온건 데이터가 없어서 뺸다
result = result[(result['rmk']!='정')].reset_index(drop=True)
import copy
result_drop = copy.deepcopy(result)
data_length = len(result)
#첨부정정에는 엑셀파일이 존재하지 않기 때문에 받으나 마나임
for i in range(data_length):    
    if '첨부정정' in result.loc[i,'rpt_nm']:
        print("첨부정정%s",i)
        result_drop=result_drop.drop(i)

result_drop = result_drop.reset_index(drop=True)
rcp_data=result_drop['rcp_no']  #rcp만 따로 저장
crp_data=result_drop['crp_cd']

excel_link_tmpl = "http://dart.fss.or.kr/pdf/download/excel.do?rcp_no={rcp_no}&dcm_no={dcm_no}&lang=ko"
win_data = pd.DataFrame(np.zeros((len(result_drop)*4,14)))
ebit_row_num_temp = pd.DataFrame(np.zeros((1,1)))
# wget: url을 파일(to)로 저장
def wget(url, to=None):
    local_filename = url.split('/')[-1]
    if to:
        local_filename = to
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
    if os.path.getsize(local_filename) <= 0:
        os.remove(local_filename)
        return None
    return local_filename


def get_report_attach_urls(rcp_no):
    attach_urls = []

    url = "http://dart.fss.or.kr/dsaf001/main.do?rcpNo=%s" % (rcp_no)
    r = requests.get(url)

    start_str = "javascript: viewDoc\('" + rcp_no + "', '"
    end_str = "', null, null, null,"
    reg = re.compile(start_str + '(.*)' + end_str)
    m = reg.findall(r.text)
    dcm_no = m[0]

    attach_urls.append(excel_link_tmpl.format(rcp_no=rcp_no, dcm_no=dcm_no))
    return attach_urls

for n in range(len(result_drop)):

    rcp_no = rcp_data[n]
    attach_urls = get_report_attach_urls(rcp_no)


    fname = crp_data[n]+'_' + rcp_no + '.xls'
    wget(attach_urls[0], fname)  #첨부정정,기타법인은 재무재표를 받을 수 없다.
a=0
for n in range(len(result_drop)):
    try:
        df = pd.read_excel(crp_data[n]+'_'+rcp_data[n]+'.xls', sheetname='연결 포괄손익계산서', index_col=0, skiprows=6)
        df1 = '연결 포괄손익계산서'
        
        if len(df.columns)==4:        
            row_name=list(df.index)
            row_name=np.nan_to_num(row_name)
            row_count = len(row_name)
            st2 = '매출'
            temp = pd.DataFrame(np.zeros((row_count,1)))
            for z in range(row_count):
                temp.iloc[z,0] = row_name[z].find(st2)
        
            temp = temp[temp[0]!=-1]
            if temp.empty:    # 영업이익이 포함된 row index가 없다면.... 연결 포괄손익계산서가 이상하게 쓰여진거일듯
                pass
            else:
                ebit_row_num_temp = temp.iloc[0].name
                if (df.iloc[ebit_row_num_temp,0]!=' ')&(df.iloc[ebit_row_num_temp,2]!=' '):
                   
                    win_data.iloc[a,0] = result_drop.loc[n,'rcp_dt']
                    win_data.iloc[a,1] = result_drop.loc[n,'crp_cd']
                    win_data.iloc[a,2] = result_drop.loc[n,'crp_nm']
                    win_data.iloc[a,3] = result_drop.loc[n,'rpt_nm']
                    win_data.iloc[a,4] = df1
                    win_data.iloc[a,5] = row_name[ebit_row_num_temp]
                    win_data.iloc[a,6] = df.iloc[ebit_row_num_temp,0]
                    win_data.iloc[a,7] = df.iloc[ebit_row_num_temp,2]
                    if df.iloc[ebit_row_num_temp,2]!=0:
                        win_data.iloc[a,8] = (df.iloc[ebit_row_num_temp,0]-df.iloc[ebit_row_num_temp,2])/df.iloc[ebit_row_num_temp,2]
                    
            st2 = '영업이익'
            temp = pd.DataFrame(np.zeros((row_count,1)))
            for z in range(row_count):
                temp.iloc[z,0] = row_name[z].find(st2)
        
            temp = temp[temp[0]!=-1]
            if temp.empty:    # 영업이익이 포함된 row index가 없다면.... 연결 포괄손익계산서가 이상하게 쓰여진거일듯
                pass
            else:
                ebit_row_num_temp = temp.iloc[0].name
                if (df.iloc[ebit_row_num_temp,0]!=' ')&(df.iloc[ebit_row_num_temp,2]!=' '):
                   

                    win_data.iloc[a,9] = df1
                    win_data.iloc[a,10] = row_name[ebit_row_num_temp]
                    win_data.iloc[a,11] = df.iloc[ebit_row_num_temp,0]
                    win_data.iloc[a,12] = df.iloc[ebit_row_num_temp,2]
                    if df.iloc[ebit_row_num_temp,2]!=0:
                        win_data.iloc[a,13] = (df.iloc[ebit_row_num_temp,0]-df.iloc[ebit_row_num_temp,2])/df.iloc[ebit_row_num_temp,2]
                    
                    a = a+1
            
            if (win_data.iloc[a-1,6]==0)&(win_data.iloc[a-1,11]!=0):
                st2 = '영업수익'
                temp = pd.DataFrame(np.zeros((row_count,1)))
                for z in range(row_count):
                    temp.iloc[z,0] = row_name[z].find(st2)
            
                temp = temp[temp[0]!=-1]
                if temp.empty:    # 영업이익이 포함된 row index가 없다면.... 연결 포괄손익계산서가 이상하게 쓰여진거일듯
                    pass
                else:
                    ebit_row_num_temp = temp.iloc[0].name
                    if (df.iloc[ebit_row_num_temp,0]!=' ')&(df.iloc[ebit_row_num_temp,2]!=' '):
                       
                        win_data.iloc[a-1,0] = result_drop.loc[n,'rcp_dt']
                        win_data.iloc[a-1,1] = result_drop.loc[n,'crp_cd']
                        win_data.iloc[a-1,2] = result_drop.loc[n,'crp_nm']
                        win_data.iloc[a-1,3] = result_drop.loc[n,'rpt_nm']
                        win_data.iloc[a-1,4] = df1
                        win_data.iloc[a-1,5] = row_name[ebit_row_num_temp]
                        win_data.iloc[a-1,6] = df.iloc[ebit_row_num_temp,0]
                        win_data.iloc[a-1,7] = df.iloc[ebit_row_num_temp,2]
                        if df.iloc[ebit_row_num_temp,2]!=0:
                            win_data.iloc[a-1,8] = (df.iloc[ebit_row_num_temp,0]-df.iloc[ebit_row_num_temp,2])/df.iloc[ebit_row_num_temp,2]
   
    except:
           pass
    
    try:
        df = pd.read_excel(crp_data[n]+'_'+rcp_data[n]+'.xls', sheetname='연결 손익계산서', index_col=0, skiprows=6)
        df1 = '연결 손익계산서'
        
        if len(df.columns)==4:        
            row_name=list(df.index)
            row_name=np.nan_to_num(row_name)
            row_count = len(row_name)
            st2 = '매출'
            temp = pd.DataFrame(np.zeros((row_count,1)))
            for z in range(row_count):
                temp.iloc[z,0] = row_name[z].find(st2)
        
            temp = temp[temp[0]!=-1]
            if temp.empty:    # 영업이익이 포함된 row index가 없다면.... 연결 포괄손익계산서가 이상하게 쓰여진거일듯
                pass
            else:
                ebit_row_num_temp = temp.iloc[0].name
                if (df.iloc[ebit_row_num_temp,0]!=' ')&(df.iloc[ebit_row_num_temp,2]!=' '):
                   
                    win_data.iloc[a,0] = result_drop.loc[n,'rcp_dt']
                    win_data.iloc[a,1] = result_drop.loc[n,'crp_cd']
                    win_data.iloc[a,2] = result_drop.loc[n,'crp_nm']
                    win_data.iloc[a,3] = result_drop.loc[n,'rpt_nm']
                    win_data.iloc[a,4] = df1
                    win_data.iloc[a,5] = row_name[ebit_row_num_temp]
                    win_data.iloc[a,6] = df.iloc[ebit_row_num_temp,0]
                    win_data.iloc[a,7] = df.iloc[ebit_row_num_temp,2]
                    if df.iloc[ebit_row_num_temp,2]!=0:
                        win_data.iloc[a,8] = (df.iloc[ebit_row_num_temp,0]-df.iloc[ebit_row_num_temp,2])/df.iloc[ebit_row_num_temp,2]
                    
            st2 = '영업이익'
            temp = pd.DataFrame(np.zeros((row_count,1)))
            for z in range(row_count):
                temp.iloc[z,0] = row_name[z].find(st2)
        
            temp = temp[temp[0]!=-1]
            if temp.empty:    # 영업이익이 포함된 row index가 없다면.... 연결 포괄손익계산서가 이상하게 쓰여진거일듯
                pass
            else:
                ebit_row_num_temp = temp.iloc[0].name
                if (df.iloc[ebit_row_num_temp,0]!=' ')&(df.iloc[ebit_row_num_temp,2]!=' '):
                   

                    win_data.iloc[a,9] = df1
                    win_data.iloc[a,10] = row_name[ebit_row_num_temp]
                    win_data.iloc[a,11] = df.iloc[ebit_row_num_temp,0]
                    win_data.iloc[a,12] = df.iloc[ebit_row_num_temp,2]
                    if df.iloc[ebit_row_num_temp,2]!=0:
                        win_data.iloc[a,13] = (df.iloc[ebit_row_num_temp,0]-df.iloc[ebit_row_num_temp,2])/df.iloc[ebit_row_num_temp,2]
                    
                    a = a+1
            if (win_data.iloc[a-1,6]==0)&(win_data.iloc[a-1,11]!=0):
                st2 = '영업수익'
                temp = pd.DataFrame(np.zeros((row_count,1)))
                for z in range(row_count):
                    temp.iloc[z,0] = row_name[z].find(st2)
            
                temp = temp[temp[0]!=-1]
                if temp.empty:    # 영업이익이 포함된 row index가 없다면.... 연결 포괄손익계산서가 이상하게 쓰여진거일듯
                    pass
                else:
                    ebit_row_num_temp = temp.iloc[0].name
                    if (df.iloc[ebit_row_num_temp,0]!=' ')&(df.iloc[ebit_row_num_temp,2]!=' '):
                       
                        win_data.iloc[a-1,0] = result_drop.loc[n,'rcp_dt']
                        win_data.iloc[a-1,1] = result_drop.loc[n,'crp_cd']
                        win_data.iloc[a-1,2] = result_drop.loc[n,'crp_nm']
                        win_data.iloc[a-1,3] = result_drop.loc[n,'rpt_nm']
                        win_data.iloc[a-1,4] = df1
                        win_data.iloc[a-1,5] = row_name[ebit_row_num_temp]
                        win_data.iloc[a-1,6] = df.iloc[ebit_row_num_temp,0]
                        win_data.iloc[a-1,7] = df.iloc[ebit_row_num_temp,2]
                        if df.iloc[ebit_row_num_temp,2]!=0:
                            win_data.iloc[a-1,8] = (df.iloc[ebit_row_num_temp,0]-df.iloc[ebit_row_num_temp,2])/df.iloc[ebit_row_num_temp,2]
           
    except:  #표를 받아올 수 없는 종목들이 있다...... pass...
        pass
        
    try:
        df = pd.read_excel(crp_data[n]+'_'+rcp_data[n]+'.xls', sheetname='포괄손익계산서', index_col=0, skiprows=6)
        df1 = '포괄손익계산서'
            
        if len(df.columns)==4:        
            row_name=list(df.index)
            row_name=np.nan_to_num(row_name)
            row_count = len(row_name)
            st2 = '매출'
            temp = pd.DataFrame(np.zeros((row_count,1)))
            for z in range(row_count):
                temp.iloc[z,0] = row_name[z].find(st2)
        
            temp = temp[temp[0]!=-1]
            if temp.empty:    # 영업이익이 포함된 row index가 없다면.... 연결 포괄손익계산서가 이상하게 쓰여진거일듯
                pass
            else:
                ebit_row_num_temp = temp.iloc[0].name
                if (df.iloc[ebit_row_num_temp,0]!=' ')&(df.iloc[ebit_row_num_temp,2]!=' '):
                   
                    win_data.iloc[a,0] = result_drop.loc[n,'rcp_dt']
                    win_data.iloc[a,1] = result_drop.loc[n,'crp_cd']
                    win_data.iloc[a,2] = result_drop.loc[n,'crp_nm']
                    win_data.iloc[a,3] = result_drop.loc[n,'rpt_nm']
                    win_data.iloc[a,4] = df1
                    win_data.iloc[a,5] = row_name[ebit_row_num_temp]
                    win_data.iloc[a,6] = df.iloc[ebit_row_num_temp,0]
                    win_data.iloc[a,7] = df.iloc[ebit_row_num_temp,2]
                    if df.iloc[ebit_row_num_temp,2]!=0:
                        win_data.iloc[a,8] = (df.iloc[ebit_row_num_temp,0]-df.iloc[ebit_row_num_temp,2])/df.iloc[ebit_row_num_temp,2]
                    
            st2 = '영업이익'
            temp = pd.DataFrame(np.zeros((row_count,1)))
            for z in range(row_count):
                temp.iloc[z,0] = row_name[z].find(st2)
        
            temp = temp[temp[0]!=-1]
            if temp.empty:    # 영업이익이 포함된 row index가 없다면.... 연결 포괄손익계산서가 이상하게 쓰여진거일듯
                pass
            else:
                ebit_row_num_temp = temp.iloc[0].name
                if (df.iloc[ebit_row_num_temp,0]!=' ')&(df.iloc[ebit_row_num_temp,2]!=' '):
                   

                    win_data.iloc[a,9] = df1
                    win_data.iloc[a,10] = row_name[ebit_row_num_temp]
                    win_data.iloc[a,11] = df.iloc[ebit_row_num_temp,0]
                    win_data.iloc[a,12] = df.iloc[ebit_row_num_temp,2]
                    if df.iloc[ebit_row_num_temp,2]!=0:
                        win_data.iloc[a,13] = (df.iloc[ebit_row_num_temp,0]-df.iloc[ebit_row_num_temp,2])/df.iloc[ebit_row_num_temp,2]
                    
                    a = a+1
            if (win_data.iloc[a-1,6]==0)&(win_data.iloc[a-1,11]!=0):
                st2 = '영업수익'
                temp = pd.DataFrame(np.zeros((row_count,1)))
                for z in range(row_count):
                    temp.iloc[z,0] = row_name[z].find(st2)
            
                temp = temp[temp[0]!=-1]
                if temp.empty:    # 영업이익이 포함된 row index가 없다면.... 연결 포괄손익계산서가 이상하게 쓰여진거일듯
                    pass
                else:
                    ebit_row_num_temp = temp.iloc[0].name
                    if (df.iloc[ebit_row_num_temp,0]!=' ')&(df.iloc[ebit_row_num_temp,2]!=' '):
                       
                        win_data.iloc[a-1,0] = result_drop.loc[n,'rcp_dt']
                        win_data.iloc[a-1,1] = result_drop.loc[n,'crp_cd']
                        win_data.iloc[a-1,2] = result_drop.loc[n,'crp_nm']
                        win_data.iloc[a-1,3] = result_drop.loc[n,'rpt_nm']
                        win_data.iloc[a-1,4] = df1
                        win_data.iloc[a-1,5] = row_name[ebit_row_num_temp]
                        win_data.iloc[a-1,6] = df.iloc[ebit_row_num_temp,0]
                        win_data.iloc[a-1,7] = df.iloc[ebit_row_num_temp,2]
                        if df.iloc[ebit_row_num_temp,2]!=0:
                            win_data.iloc[a-1,8] = (df.iloc[ebit_row_num_temp,0]-df.iloc[ebit_row_num_temp,2])/df.iloc[ebit_row_num_temp,2]
              
    except:
        pass

    try:
        df = pd.read_excel(crp_data[n]+'_'+rcp_data[n]+'.xls', sheetname='손익계산서', index_col=0, skiprows=6)
        df1 = '손익계산서'
            
        if len(df.columns)==4:        
            row_name=list(df.index)
            row_name=np.nan_to_num(row_name)
            row_count = len(row_name)
            st2 = '매출'
            temp = pd.DataFrame(np.zeros((row_count,1)))
            for z in range(row_count):
                temp.iloc[z,0] = row_name[z].find(st2)
        
            temp = temp[temp[0]!=-1]
            if temp.empty:    # 영업이익이 포함된 row index가 없다면.... 연결 포괄손익계산서가 이상하게 쓰여진거일듯
                pass
            else:
                ebit_row_num_temp = temp.iloc[0].name
                if (df.iloc[ebit_row_num_temp,0]!=' ')&(df.iloc[ebit_row_num_temp,2]!=' '):
                   
                    win_data.iloc[a,0] = result_drop.loc[n,'rcp_dt']
                    win_data.iloc[a,1] = result_drop.loc[n,'crp_cd']
                    win_data.iloc[a,2] = result_drop.loc[n,'crp_nm']
                    win_data.iloc[a,3] = result_drop.loc[n,'rpt_nm']
                    win_data.iloc[a,4] = df1
                    win_data.iloc[a,5] = row_name[ebit_row_num_temp]
                    win_data.iloc[a,6] = df.iloc[ebit_row_num_temp,0]
                    win_data.iloc[a,7] = df.iloc[ebit_row_num_temp,2]
                    if df.iloc[ebit_row_num_temp,2]!=0:
                        win_data.iloc[a,8] = (df.iloc[ebit_row_num_temp,0]-df.iloc[ebit_row_num_temp,2])/df.iloc[ebit_row_num_temp,2]
                    
            st2 = '영업이익'
            temp = pd.DataFrame(np.zeros((row_count,1)))
            for z in range(row_count):
                temp.iloc[z,0] = row_name[z].find(st2)
        
            temp = temp[temp[0]!=-1]
            if temp.empty:    # 영업이익이 포함된 row index가 없다면.... 연결 포괄손익계산서가 이상하게 쓰여진거일듯
                pass
            else:
                ebit_row_num_temp = temp.iloc[0].name
                if (df.iloc[ebit_row_num_temp,0]!=' ')&(df.iloc[ebit_row_num_temp,2]!=' '):
                   

                    win_data.iloc[a,9] = df1
                    win_data.iloc[a,10] = row_name[ebit_row_num_temp]
                    win_data.iloc[a,11] = df.iloc[ebit_row_num_temp,0]
                    win_data.iloc[a,12] = df.iloc[ebit_row_num_temp,2]
                    if df.iloc[ebit_row_num_temp,2]!=0:
                        win_data.iloc[a,13] = (df.iloc[ebit_row_num_temp,0]-df.iloc[ebit_row_num_temp,2])/df.iloc[ebit_row_num_temp,2]
                    a = a+1
                    
            if (win_data.iloc[a-1,6]==0)&(win_data.iloc[a-1,11]!=0):
                st2 = '영업수익'
                temp = pd.DataFrame(np.zeros((row_count,1)))
                for z in range(row_count):
                    temp.iloc[z,0] = row_name[z].find(st2)
            
                temp = temp[temp[0]!=-1]
                if temp.empty:    # 영업이익이 포함된 row index가 없다면.... 연결 포괄손익계산서가 이상하게 쓰여진거일듯
                    pass
                else:
                    ebit_row_num_temp = temp.iloc[0].name
                    if (df.iloc[ebit_row_num_temp,0]!=' ')&(df.iloc[ebit_row_num_temp,2]!=' '):
                       
                        win_data.iloc[a-1,0] = result_drop.loc[n,'rcp_dt']
                        win_data.iloc[a-1,1] = result_drop.loc[n,'crp_cd']
                        win_data.iloc[a-1,2] = result_drop.loc[n,'crp_nm']
                        win_data.iloc[a-1,3] = result_drop.loc[n,'rpt_nm']
                        win_data.iloc[a-1,4] = df1
                        win_data.iloc[a-1,5] = row_name[ebit_row_num_temp]
                        win_data.iloc[a-1,6] = df.iloc[ebit_row_num_temp,0]
                        win_data.iloc[a-1,7] = df.iloc[ebit_row_num_temp,2]
                        if df.iloc[ebit_row_num_temp,2]!=0:
                            win_data.iloc[a-1,8] = (df.iloc[ebit_row_num_temp,0]-df.iloc[ebit_row_num_temp,2])/df.iloc[ebit_row_num_temp,2]
                   
    except:
        pass   
    


for p in range(len(win_data)):
    if win_data.iloc[p,7]<0:
        win_data.iloc[p,7] = win_data.iloc[p,7]*(-1)
        




