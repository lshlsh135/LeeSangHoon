# -*- coding: utf-8 -*-
"""
Created on Mon Aug 14 08:24:37 2017

@author: SH-NoteBook
"""

import pandas as pd
import numpy as np
import cx_Oracle



#이거 두개 반드시 선언!
cx0=cx_Oracle.makedsn("localhost",1521,"xe")
connection = cx_Oracle.connect("lshlsh135","2tkdgns2",cx0) #이게 실행이 안될때가 있는데
#그때는 services에 들어가서 oracle listner를 실행시켜줘야함


#DATA를 가져온다!!
kospi = pd.read_sql("""select * from kospi_ex""",con=connection)
kosdaq = pd.read_sql("""select * from kosdaq_ex""",con=connection)
rebalancing_date = pd.read_sql("""select * from rebalancing_date""",con=connection)
month_date = pd.read_sql("""select * from month_date""",con=connection)

raw_data = pd.concat([kospi,kosdaq],axis=0,ignore_index=True).drop_duplicates()   #왜인지 모르겠는데 db에 중복된 정보가 들어가있네 ..? 
col_length = len(rebalancing_date)-1 #rebalancing_date의 길이는 66이다. range로 이렇게 하면 0부터 65까지 66개의 i 가 만들어진다. -1을 해준건 실제 수익률은 -1개가 생성되기 때문.

return_data = pd.DataFrame(np.zeros((1,col_length)))
return_month_data = pd.DataFrame(np.zeros((1,3*col_length)))
return_final = pd.DataFrame(np.zeros((1,1)))


for n in range(col_length): 
    first_data = raw_data[raw_data['TRD_DATE']==rebalancing_date.iloc[n,0]] # rebalanging할 날짜에 들어있는 모든 db data를 받아온다.
    target_data = raw_data[raw_data['TRD_DATE']==rebalancing_date.iloc[n+1,0]]
    target_data = target_data.loc[:,['TRD_DATE','GICODE','ADJ_PRC']]
    first_data = first_data[(first_data['CAP_SIZE']==1)]
    first_data = first_data[first_data['MARKET_CAP']>100000000000]    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    