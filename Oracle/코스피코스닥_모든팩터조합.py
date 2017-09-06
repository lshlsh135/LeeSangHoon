# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 13:27:10 2017

@author: SH-NoteBook
"""


import pandas as pd
import numpy as np
import cx_Oracle
from factor_1 import factor_1
from factor_2 import factor_2
from factor_3 import factor_3
from factor_2_mid import factor_2_mid
from factor_3_mid import factor_3_mid
from factor_4_mid import factor_4_mid
from factor_3_mid_대_중소코 import factor_3_mid_대_중소코


#이거 두개 반드시 선언!
cx0=cx_Oracle.makedsn("localhost",1521,"xe")
connection = cx_Oracle.connect("lshlsh135","2tkdgns2",cx0) #이게 실행이 안될때가 있는데
#그때는 services에 들어가서 oracle listner를 실행시켜줘야함

kospi_quarter = pd.read_excel("kospi_quarter_data.xlsx",sheetname="kospi",header=None)
#DATA를 가져온다!!
kospi = pd.read_sql("""select * from kospi""",con=connection)
kosdaq = pd.read_sql("""select * from kosdaq""",con=connection)
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


first_column = len(raw_data.columns)  # 1/pbr 의 loc
raw_data['1/pbr']=raw_data['EQUITY']/raw_data['MARKET_CAP']
raw_data['1/per']=raw_data['ADJ_NI_12M_FWD']/raw_data['MARKET_CAP']
raw_data['div_yield']=raw_data['CASH_DIV_COM']/raw_data['MARKET_CAP']
raw_data['roe']=raw_data['NI']/raw_data['EQUITY']
raw_data['roa']=raw_data['NI']/raw_data['ASSET']
raw_data['sales_cap']=raw_data['SALES']/raw_data['MARKET_CAP']
raw_data['gpro_cap']=raw_data['GROSS_PROFIT']/raw_data['MARKET_CAP']
raw_data['opro_cap']=raw_data['OPE_PROFIT']/raw_data['MARKET_CAP'] # 이놈 시총제한 있고 없고 차이 심한데 
raw_data['sales_cap_ttm']=raw_data['SALES_TTM']/raw_data['MARKET_CAP']
raw_data['opro_cap_ttm']=raw_data['OPE_PROFIT_TTM']/raw_data['MARKET_CAP']
raw_data['1/trd_value']=raw_data['MARKET_CAP'] /raw_data['TRD_VALUE_60D_MEAN']
raw_data['1/vol'] = 1/raw_data['STD_52WEEK']
raw_data['1/beta'] = 1/raw_data['BEDA_52WEEK_D']

final_column = len(raw_data.columns)-1 # roa 의 loc

ir_data = pd.DataFrame(np.zeros((final_column-first_column+1,30)))
factor_num = 1
row_num = 0
for i in range(first_column,final_column+1):
    a=factor_1(raw_data,rebalancing_date,month_date,i)
    locals()['aaa_{}'.format(i)] =a.factor_1()    
    ir_data.iloc[row_num,factor_num] = (2*(np.mean(locals()['aaa_{}'.format(i)][1].iloc[4,:])-np.mean(kospi_quarter,axis=1))/np.std(locals()['aaa_{}'.format(i)][1].iloc[4,:]-kospi_quarter,axis=1))[0]
    
    row_num += 1


for i in range(first_column,final_column+1):
    for j in range(first_column,final_column+1):
        if i<j:
            a=factor_2(raw_data,rebalancing_date,month_date,i,j)
            locals()['aaa_{}{}'.format(i,j)] =a.factor_2()
            locals()['ir_data_{}{}'.format(i,j)] = pd.DataFrame(np.zeros((5,30)))
            locals()['ir_data_{}{}'.format(i,j)] = (2*(np.mean(locals()['aaa_{}{}'.format(i,j)][1].iloc[4,:])-np.mean(kospi_quarter,axis=1))/np.std(locals()['aaa_{}{}'.format(i,j)][1].iloc[4,:]-kospi_quarter,axis=1))[0]


for i in range(first_column,final_column+1):
    for j in range(first_column,final_column+1):
        for z in range(first_column,final_column+1):
            if i<j<z:
                a=factor_3(raw_data,rebalancing_date,month_date,i,j,z)
                locals()['aaa_{}{}{}'.format(i,j,z)] =a.factor_3()
                locals()['ir_data_{}{}{}'.format(i,j,z)] = pd.DataFrame(np.zeros((1,30)))
                locals()['ir_data_{}{}{}'.format(i,j,z)] = (2*(np.mean(locals()['aaa_{}{}{}'.format(i,j,z)][1].iloc[4,:])-np.mean(kospi_quarter,axis=1))/np.std(locals()['aaa_{}{}{}'.format(i,j,z)][1].iloc[4,:]-kospi_quarter,axis=1))[0]




a=factor_3_mid(raw_data,rebalancing_date,month_date,wics_mid,32,34,38)
adfadf=a.factor_3_mid()



for i in range(32,34):
    for j in range(first_column,final_column+1):
        if i<j:
            a=factor_2_mid(raw_data,rebalancing_date,month_date,wics_mid,i,j)
            locals()['aaa_{}{}'.format(i,j)] =a.factor_2_mid()
            locals()['ir_data_{}{}'.format(i,j)] = (2*(np.mean(locals()['aaa_{}{}'.format(i,j)][1],axis=1)-np.mean(kospi_quarter,axis=1))/np.std(locals()['aaa_{}{}'.format(i,j)][1]-kospi_quarter,axis=1))[0]


#factor 3개 랜덤하게 골라서 성과 측정
for i in range(32,34):
    for j in range(first_column,final_column+1):
        for z in range(first_column,final_column+1):
            if i<j<z:
                a=factor_3_mid(raw_data,rebalancing_date,month_date,wics_mid,i,j,z)
                locals()['aaa_{}{}{}'.format(i,j,z)] =a.factor_3_mid()
                locals()['ir_data_{}{}{}'.format(i,j,z)] = (2*(np.mean(locals()['aaa_{}{}{}'.format(i,j,z)][1],axis=1)-np.mean(kospi_quarter,axis=1))/np.std(locals()['aaa_{}{}{}'.format(i,j,z)][1]-kospi_quarter,axis=1))[0]


#factor 4개 랜덤하게 골라서 성과 측정
for i in range(32,34):  #per나 pbr은 꼭 들어가야해..
    for j in range(first_column,final_column+1):
        for z in range(first_column,final_column+1):
            for p in range(first_column,final_column+1):
                if i<j<z<p:
                    a=factor_4_mid(raw_data,rebalancing_date,month_date,wics_mid,i,j,z,p)
                    locals()['aaa_{}{}{}{}'.format(i,j,z,p)] =a.factor_4_mid()
                    locals()['ir_data_{}{}{}{}'.format(i,j,z,p)] = (2*(np.mean(locals()['aaa_{}{}{}{}'.format(i,j,z,p)][1],axis=1)-np.mean(kospi_quarter,axis=1))/np.std(locals()['aaa_{}{}{}{}'.format(i,j,z,p)][1]-kospi_quarter,axis=1))[0]


#factor 3개 랜덤하게 골라서 대형주25, 중소코스피 75종목 고름
for i in range(first_column,final_column+1):
    for j in range(first_column,final_column+1):
        for z in range(first_column,final_column+1):
            if i<j<z:
                a=factor_3_mid_대_중소코(raw_data,rebalancing_date,month_date,wics_mid,i,j,z)
                locals()['aaa_{}{}{}'.format(i,j,z)] =a.factor_3_mid_대_중소코()
                locals()['ir_data_{}{}{}'.format(i,j,z)] = (2*(np.mean(locals()['aaa_{}{}{}'.format(i,j,z)][1],axis=1)-np.mean(kospi_quarter,axis=1))/np.std(locals()['aaa_{}{}{}'.format(i,j,z)][1]-kospi_quarter,axis=1))[0]





import itertools       
a=list(itertools.combinations(range(first_column,final_column+1), 2))


    
    
    
    
    
    
    