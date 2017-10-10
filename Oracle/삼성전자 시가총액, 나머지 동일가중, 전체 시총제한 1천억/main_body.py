# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 08:49:09 2017

@author: SH-NoteBook
"""


import pandas as pd
import numpy as np
import cx_Oracle
from factor_5_mid import factor_5_mid
from return_calculator import return_calculator




#이거 두개 반드시 선언!
cx0=cx_Oracle.makedsn("localhost",1521,"xe")
connection = cx_Oracle.connect("lshlsh135","2tkdgns2",cx0) #이게 실행이 안될때가 있는데
#그때는 services에 들어가서 oracle listner를 실행시켜줘야함


kospi_quarter = pd.read_sql("""select * from kospi_quarter_return""",con=connection)
kospi_month = pd.read_sql("""select * from kospi_month_return""",con=connection)
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
raw_data['1/pbr']=raw_data['EQUITY']/raw_data['MARKET_CAP'] # 32번째 column
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



#factor 5개 랜덤하게 골라서 성과 측정
for i in range(32,34):  #per나 pbr은 꼭 들어가야해..
    for j in range(first_column,final_column+1):
        for z in range(first_column,final_column+1):
            for p in range(first_column,final_column+1):
                for k in range(first_column,final_column+1):
                    if i<j<z<p<k:
                        a=factor_5_mid(raw_data,rebalancing_date,month_date,wics_mid,i,j,z,p,k)
                        locals()['aaa_{}{}{}{}{}'.format(i,j,z,p,k)] =a.factor_5_mid()
                        locals()['ir_data_{}{}{}{}{}'.format(i,j,z,p,k)] = 2*(np.mean(locals()['aaa_{}{}{}{}{}'.format(i,j,z,p,k)][1],axis=1)-np.mean(kospi_quarter['RET']))/np.std(locals()['aaa_{}{}{}{}{}'.format(i,j,z,p,k)][1]-kospi_quarter['RET'],axis=1)
                        b=return_calculator(locals()['aaa_{}{}{}{}{}'.format(i,j,z,p,k)][1],locals()['aaa_{}{}{}{}{}'.format(i,j,z,p,k)][2],kospi_quarter,kospi_month)
                        b.rolling_12month_return_5factor(i,j,z,p,k)

    
    
    
    
    
    