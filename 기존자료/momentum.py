# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 13:47:31 2017

@author: SH-NoteBook
"""


#==============================================================================
# 직전 12month의 수익률을 사용
#==============================================================================
import pandas as pd
import numpy as np


return_data = np.zeros((5,189))
return_data = pd.DataFrame(return_data)
raw_data = pd.read_excel('exercise_v01.xlsx',sheetname='Raw_data_month1',header=None)
rtn_month = pd.read_excel('exercise_v01.xlsx',sheetname='월별수익률1',header=None)
kospi_month = pd.read_pickle('kospi_month')
for i in range(1,6):
    locals()['data_name_{}'.format(i)] = pd.DataFrame(np.zeros((200,63)))

turnover = pd.DataFrame(np.zeros((5,1)))

for n in range(3,192):
    
    data_big = raw_data[(raw_data[n] == 1)|(raw_data[n] == 2)|(raw_data[n]==3)]
    data_big = data_big.loc[:,[1,n]]
    data = pd.concat([data_big,rtn_month.loc[:,n-3:n+8]],axis=1,join='inner',ignore_index=True)
    temp_return=data.loc[:,0:13]
    for k in range(3,14):
        temp_return[2]=temp_return[2]*temp_return[k]
        
    gross_return=temp_return[[0,2]]
    gross_return=gross_return[gross_return[2].notnull()]
    data_size= len(gross_return)     # Row count
    
    gross_return=gross_return.assign(rnk=np.floor(gross_return[2].rank(method='first')/(data_size/5+1/5))) 
    
    data_1=gross_return.query('5>rnk>3')   # 4
    data_2=gross_return.query('4>rnk>2')   # 3
    data_3=gross_return.query('3>rnk>1')   # 2
    data_4=gross_return.query('2>rnk>0')   # 1
    data_5=gross_return.query('1>rnk>-1')  # 0
    
    data_1=pd.concat([data_1,rtn_month[n+9]],axis=1,join='inner',ignore_index=True)    # 각각 수익률 매칭
    data_2=pd.concat([data_2,rtn_month[n+9]],axis=1,join='inner',ignore_index=True)
    data_3=pd.concat([data_3,rtn_month[n+9]],axis=1,join='inner',ignore_index=True)
    data_4=pd.concat([data_4,rtn_month[n+9]],axis=1,join='inner',ignore_index=True)
    data_5=pd.concat([data_5,rtn_month[n+9]],axis=1,join='inner',ignore_index=True)
    
    data_1=data_1[data_1[3].notnull()]
    data_2=data_2[data_2[3].notnull()]
    data_3=data_3[data_3[3].notnull()]
    data_4=data_4[data_4[3].notnull()]
    data_5=data_5[data_5[3].notnull()]
    
    for i in range(1,6):
        locals()['data_name_{}'.format(i)][n-3] = locals()['data_{}'.format(i)][0].reset_index(drop=True)
    
    return_data.iloc[0,n-3]=np.mean(data_1[3])    # 각각  누적수익률 기록
    return_data.iloc[1,n-3]=np.mean(data_2[3])
    return_data.iloc[2,n-3]=np.mean(data_3[3])
    return_data.iloc[3,n-3]=np.mean(data_4[3])
    return_data.iloc[4,n-3]=np.mean(data_5[3])

    if n == 191:
        pass
    
return_final=np.product(return_data,axis=1)

diff = return_data - np.tile(kospi_month,(5,1))
column_lengh = len(diff.columns)
diff = diff>0
#true == 1 , False == 0 으로 판단하기 때문에 다 더하면 가장 끝 column에 0보다 큰 것들 갯수가 남음
diff = diff.cumsum(axis=1)
win_rate = diff[column_lengh-1]/column_lengh

               
               
#평균 turnover 계산
for n in range(3,65):
    for i in range(1,6):
        len1 = len(locals()['data_name_{}'.format(i)][locals()['data_name_{}'.format(i)][n-2].notnull()])
        aaa=locals()['data_name_{}'.format(i)].loc[:,[n-3,n-2]]
        bbb=pd.DataFrame(aaa.stack().value_counts())
        len2=len(bbb[bbb[0]==2])
        locals()['data_name_{}'.format(i)].loc[200,n-2]=(len1-len2)/len1
        qqqqq=locals()['data_name_{}'.format(i)].iloc[200,1:]
        turnover.iloc[i-1,:]=np.mean(qqqqq,axis=0)
        


#==============================================================================
# 직전 1개월 이전 11개월 사용
#==============================================================================
import pandas as pd
import numpy as np


return_data = np.zeros((5,189))
return_data = pd.DataFrame(return_data)
raw_data = pd.read_excel('exercise_v01.xlsx',sheetname='Raw_data_month1',header=None)
rtn_month = pd.read_excel('exercise_v01.xlsx',sheetname='월별수익률1',header=None)
kospi_month = pd.read_pickle('kospi_month')
for i in range(1,6):
    locals()['data_name_{}'.format(i)] = pd.DataFrame(np.zeros((200,63)))

turnover = pd.DataFrame(np.zeros((5,1)))

for n in range(3,192):
    
    data_big = raw_data[(raw_data[n] == 1)|(raw_data[n] == 2)|(raw_data[n]==3)]
    data_big = data_big.loc[:,[1,n]]
    data = pd.concat([data_big,rtn_month.loc[:,n-3:n+7]],axis=1,join='inner',ignore_index=True)
    temp_return=data.loc[:,0:12]
    for k in range(3,13):
        temp_return[2]=temp_return[2]*temp_return[k]
        
    gross_return=temp_return[[0,2]]
    gross_return=gross_return[gross_return[2].notnull()]
    data_size= len(gross_return)     # Row count
    
    gross_return=gross_return.assign(rnk=np.floor(gross_return[2].rank(method='first')/(data_size/5+1/5))) 
    
    data_1=gross_return.query('5>rnk>3')   # 4
    data_2=gross_return.query('4>rnk>2')   # 3
    data_3=gross_return.query('3>rnk>1')   # 2
    data_4=gross_return.query('2>rnk>0')   # 1
    data_5=gross_return.query('1>rnk>-1')  # 0
    
    data_1=pd.concat([data_1,rtn_month[n+9]],axis=1,join='inner',ignore_index=True)    # 각각 수익률 매칭
    data_2=pd.concat([data_2,rtn_month[n+9]],axis=1,join='inner',ignore_index=True)
    data_3=pd.concat([data_3,rtn_month[n+9]],axis=1,join='inner',ignore_index=True)
    data_4=pd.concat([data_4,rtn_month[n+9]],axis=1,join='inner',ignore_index=True)
    data_5=pd.concat([data_5,rtn_month[n+9]],axis=1,join='inner',ignore_index=True)
    
    data_1=data_1[data_1[3].notnull()]
    data_2=data_2[data_2[3].notnull()]
    data_3=data_3[data_3[3].notnull()]
    data_4=data_4[data_4[3].notnull()]
    data_5=data_5[data_5[3].notnull()]
    
    for i in range(1,6):
        locals()['data_name_{}'.format(i)][n-3] = locals()['data_{}'.format(i)][0].reset_index(drop=True)
    
    return_data.iloc[0,n-3]=np.mean(data_1[3])    # 각각  누적수익률 기록
    return_data.iloc[1,n-3]=np.mean(data_2[3])
    return_data.iloc[2,n-3]=np.mean(data_3[3])
    return_data.iloc[3,n-3]=np.mean(data_4[3])
    return_data.iloc[4,n-3]=np.mean(data_5[3])

    if n == 191:
        pass
    
return_final=np.product(return_data,axis=1)

diff = return_data - np.tile(kospi_month,(5,1))
column_lengh = len(diff.columns)
diff = diff>0
#true == 1 , False == 0 으로 판단하기 때문에 다 더하면 가장 끝 column에 0보다 큰 것들 갯수가 남음
diff = diff.cumsum(axis=1)
win_rate = diff[column_lengh-1]/column_lengh

               
               
#평균 turnover 계산
for n in range(3,65):
    for i in range(1,6):
        len1 = len(locals()['data_name_{}'.format(i)][locals()['data_name_{}'.format(i)][n-2].notnull()])
        aaa=locals()['data_name_{}'.format(i)].loc[:,[n-3,n-2]]
        bbb=pd.DataFrame(aaa.stack().value_counts())
        len2=len(bbb[bbb[0]==2])
        locals()['data_name_{}'.format(i)].loc[200,n-2]=(len1-len2)/len1
        qqqqq=locals()['data_name_{}'.format(i)].iloc[200,1:]
        turnover.iloc[i-1,:]=np.mean(qqqqq,axis=0)
        




