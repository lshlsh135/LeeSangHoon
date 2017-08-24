# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 13:27:10 2017

@author: SH-NoteBook
"""


import pandas as pd
import numpy as np
import cx_Oracle
from factor_1 import factor_1


#이거 두개 반드시 선언!
cx0=cx_Oracle.makedsn("localhost",1521,"xe")
connection = cx_Oracle.connect("lshlsh135","2tkdgns2",cx0) #이게 실행이 안될때가 있는데
#그때는 services에 들어가서 oracle listner를 실행시켜줘야함

kospi_quarter = pd.read_pickle('kospi_quarter')
#DATA를 가져온다!!
kospi = pd.read_sql("""select * from kospi_ex""",con=connection)
kosdaq = pd.read_sql("""select * from kosdaq_ex""",con=connection)
rebalancing_date = pd.read_sql("""select * from rebalancing_date""",con=connection)
month_date = pd.read_sql("""select * from month_date""",con=connection)
wics_mid = pd.read_sql("""select * from wics_mid""",con=connection)

raw_data = pd.concat([kospi,kosdaq],axis=0,ignore_index=True).drop_duplicates()   #왜인지 모르겠는데 db에 중복된 정보가 들어가있네 ..? 
col_length = len(rebalancing_date)-1 #rebalancing_date의 길이는 66이다. range로 이렇게 하면 0부터 65까지 66개의 i 가 만들어진다. -1을 해준건 실제 수익률은 -1개가 생성되기 때문.

return_data = pd.DataFrame(np.zeros((1,col_length)))
data_name = pd.DataFrame(np.zeros((200,col_length)))
return_month_data = pd.DataFrame(np.zeros((1,3*col_length)))
quarter_data = pd.DataFrame(np.zeros((200,3*col_length)))
return_final = pd.DataFrame(np.zeros((1,1)))
return_month_data = pd.DataFrame(np.zeros((1,3*col_length)))
ir_data = pd.DataFrame(np.zeros((5,30)))

first_column = len(raw_data.columns)  # 1/pbr 의 loc
raw_data['1/pbr']=raw_data['EQUITY']/raw_data['MARKET_CAP']
raw_data['1/per']=raw_data['ADJ_NI_12M_FWD']/raw_data['MARKET_CAP']
raw_data['div_yield']=raw_data['CASH_DIV_COM']/raw_data['MARKET_CAP']
raw_data['roe']=raw_data['NI']/raw_data['EQUITY']
raw_data['roa']=raw_data['NI']/raw_data['ASSET']
final_column = len(raw_data.columns)-1 # roa 의 loc

factor_num = 1
row_num = 0
for i in range(first_column,final_column+1):
    a=factor_1(raw_data,rebalancing_date,month_date,i)
    locals()['aaa_{}'.format(i)] =a.per()    
    ir_data.iloc[row_num,factor_num] = (2*(np.mean(locals()['aaa_{}'.format(i)][1].iloc[4,:])-np.mean(kospi_quarter,axis=1))/np.std(locals()['aaa_{}'.format(i)][1].iloc[4,:]-kospi_quarter,axis=1))[0]
    
    row_num += 1


a=[3,4]
len(a)
a.extend([5])








import itertools       
a=list(itertools.combinations(range(first_column,final_column+1), 2))


for n in range(col_length): 
    first_data = raw_data[raw_data['TRD_DATE']==rebalancing_date.iloc[n,0]] # rebalanging할 날짜에 들어있는 모든 db data를 받아온다.
    target_data = raw_data[raw_data['TRD_DATE']==rebalancing_date.iloc[n+1,0]] # 다음 리밸런싱 날짜.
    target_data = target_data.loc[:,['TRD_DATE','GICODE','ADJ_PRC']]
    # CAP_SIZE : 1코스피대2코스피중3코스피소4코스닥대5코스닥중6코스닥소
    # 코스닥은 문제가 발생 4 5 6 은 2002년도에 kosdaq big mid small지수가 상장되었기 때문에 그 이전 데이타는 0이라고 나옴
    # 따라서 iskosdaq라는 새로운 column을 추가했음.
    # 기존에 했던 backtesting도 틀렸었음.. 물론 2002년 이전 구간만. 그 이후에는 같을것으로 예상
    first_data = first_data[(first_data['CAP_SIZE']==1)|(first_data['CAP_SIZE']==2)|(first_data['CAP_SIZE']==3)|(first_data['ISKOSDAQ']=='KOSDAQ')]
    first_data = first_data[first_data['MARKET_CAP']>100000000000]
    first_data['size_FIF_wisefn'] = first_data['JISU_STOCK']*first_data['FIF_RATIO']*first_data['ADJ_PRC']
    samsung = first_data[first_data['CO_NM']=='삼성전자']
    
    
    
    
    
    
    
    
    
    
    
    
    