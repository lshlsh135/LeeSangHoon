# -*- coding: utf-8 -*-
"""
Created on Tue Apr  4 10:12:30 2017

@author: SH-NoteBook
"""
#==============================================================================
# dividend yeild only
#==============================================================================
import pandas as pd
import numpy as np


return_data = np.zeros((5,63))
return_data = pd.DataFrame(return_data)
raw_data = pd.read_excel('exercise_v01.xlsx',sheetname='Raw_data1',header=None)
size = pd.read_excel('exercise_v01.xlsx',sheetname='시가총액1',header=None)
cash_div = pd.read_excel('exercise_v01.xlsx',sheetname='현금배당액1',header=None)
rtn = pd.read_excel('exercise_v01.xlsx',sheetname='수익률1',header=None)
kospi_quarter = pd.read_pickle('kospi_quarter')

for i in range(1,6):
    locals()['data_name_{}'.format(i)] = pd.DataFrame(np.zeros((200,63)))

turnover = pd.DataFrame(np.zeros((5,1)))



for n in range(3,66):
       
    data_big = raw_data[(raw_data[n] == 1)|(raw_data[n] == 2)|(raw_data[n]==3)]
    data_big = data_big.loc[:,[1,n]]
    data = pd.concat([data_big, size[n],  cash_div[n]],axis=1,join='inner',ignore_index=True)
    data.columns = ['name','group','size','cash_div']
    data['div_yield']=data['cash_div']/data['size']

#    data=data[data['div_yield']>0]    # per가 NAN인 Row 제외
    data=data[data['div_yield'].notnull()]
    data_size= len(data)     # Row count
    data=data.assign(rnk=np.floor(data['div_yield'].rank(method='first')/(data_size/5+1/5)))          
                    
    data_1=data.query('5>rnk>3')   # 4
    data_2=data.query('4>rnk>2')   # 3
    data_3=data.query('3>rnk>1')   # 2
    data_4=data.query('2>rnk>0')   # 1
    data_5=data.query('1>rnk>-1')  # 0
        
    data_1=pd.concat([data_1,rtn[n-3]],axis=1,join='inner',ignore_index=True)    # 각각 수익률 매칭
    data_2=pd.concat([data_2,rtn[n-3]],axis=1,join='inner',ignore_index=True)
    data_3=pd.concat([data_3,rtn[n-3]],axis=1,join='inner',ignore_index=True)
    data_4=pd.concat([data_4,rtn[n-3]],axis=1,join='inner',ignore_index=True)
    data_5=pd.concat([data_5,rtn[n-3]],axis=1,join='inner',ignore_index=True)
    
    for i in range(1,6):
        locals()['data_name_{}'.format(i)][n-3] = locals()['data_{}'.format(i)][0].reset_index(drop=True)

    
    return_data.iloc[0,n-3]=np.mean(data_1[6])    # 각각  누적수익률 기록
    return_data.iloc[1,n-3]=np.mean(data_2[6])
    return_data.iloc[2,n-3]=np.mean(data_3[6])
    return_data.iloc[3,n-3]=np.mean(data_4[6])
    return_data.iloc[4,n-3]=np.mean(data_5[6])
    if n == 65 : 
        pass
    
return_final=np.product(return_data,axis=1)

diff = return_data - np.tile(kospi_quarter,(5,1))
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
# dividend yeild & PBR
#==============================================================================
import pandas as pd
import numpy as np


raw_data = pd.read_pickle('raw_data')
size = pd.read_pickle('size')
rtn = pd.read_pickle('rtn')
equity = pd.read_pickle('equity')
cash_div = pd.read_pickle('cash_div')
ni = pd.read_pickle('ni')
kospi_quarter = pd.read_pickle('kospi_quarter')
return_data = np.zeros((5,63))
return_data = pd.DataFrame(return_data)
turnover = pd.DataFrame(np.zeros((4,4)))
for i in range(0,4):
    for j in range(0,4):
        locals()['return_data_{}{}'.format(i,j)] = pd.DataFrame(np.zeros((1,63)))
        locals()['beta_{}{}'.format(i,j)] = pd.DataFrame(np.zeros((1,822)))
        locals()['beta_sum_{}{}'.format(i,j)] = pd.DataFrame(np.zeros((1,822)))
        locals()['data_name_{}{}'.format(i,j)] = pd.DataFrame(np.zeros((80,63)))
        



for n in range(3,66):
    
    data_big = raw_data[(raw_data[n] == 1)|(raw_data[n] == 2)|(raw_data[n]==3)]
    data_big = data_big.loc[:,[1,n]]
    data = pd.concat([data_big, size[n], cash_div[n], equity[n]],axis=1,join='inner',ignore_index=True)
    data.columns = ['name','group','size','cash_div','equity']
        
    data['pbr']=data['size']/data['equity']
    data['div_yield']=data['cash_div']/data['size']
    
    # dividend yield >0 or ==0
    data=data[data['div_yield']>0]
    data=data[data['div_yield'].notnull()]
    data=data[data['pbr'].notnull()]    # per가 NAN인 Row 제외
    data=data.query('pbr>0')
        
    data_size= len(data)     # Row count
    data=data.assign(rnk_pbr=np.floor(data['pbr'].rank(method='first')/(data_size/4+1/4)))             
    data=data.assign(rnk_div=np.floor(data.groupby(['rnk_pbr'])['div_yield'].rank(method='first')/(data_size/16+1/4)))

    
      

    for i in range(0,4):
        for j in range(0,4):
                locals()['data_{}{}'.format(i,j)] = data[(data['rnk_pbr']==i)&(data['rnk_div']==j)]  
                locals()['data_{}{}'.format(i,j)] = pd.concat([locals()['data_{}{}'.format(i,j)],rtn[n-3]],axis=1,join='inner',ignore_index=True) #수익률 매칭
                locals()['data_name_{}{}'.format(i,j)][n-3] = locals()['data_{}{}'.format(i,j)][0].reset_index(drop=True)
                locals()['data_{}{}'.format(i,j)]=locals()['data_{}{}'.format(i,j)][locals()['data_{}{}'.format(i,j)][9].notnull()]
                locals()['data_{}{}'.format(i,j)]=locals()['data_{}{}'.format(i,j)][locals()['data_{}{}'.format(i,j)][9]>0]
                locals()['return_data_{}{}'.format(i,j)].iloc[0,n-3]=np.mean(locals()['data_{}{}'.format(i,j)][9])
            
                    
    if n == 65 : 
        pass

return_final=pd.DataFrame(np.zeros((4,4)))    
sharpe_final=pd.DataFrame(np.zeros((4,4)))
win_rate=pd.DataFrame(np.zeros((4,4))) 
#승률 저장
for i in range(0,4):
        for j in range(0,4):
            locals()['diff_{}{}'.format(i,j)] = pd.DataFrame(np.zeros((1,63)))
            locals()['diff_{}{}'.format(i,j)] = locals()['return_data_{}{}'.format(i,j)] - kospi_quarter
            column_lengh = len(locals()['diff_{}{}'.format(i,j)].columns)
            locals()['diff_{}{}'.format(i,j)] = locals()['diff_{}{}'.format(i,j)]>0
#true == 1 , False == 0 으로 판단하기 때문에 다 더하면 가장 끝 column에 0보다 큰 것들 갯수가 남음
            locals()['diff_{}{}'.format(i,j)] = locals()['diff_{}{}'.format(i,j)].cumsum(axis=1)
            win_rate.iloc[i,j] = np.array(locals()['diff_{}{}'.format(i,j)][column_lengh-1]/column_lengh)


for i in range(0,4):
    for j in range(0,4):
        return_final.iloc[i,j] = np.product(locals()['return_data_{}{}'.format(i,j)],axis=1)   #np.product로 하면 누적, np.average
        #샤프비율 저장    
        sharpe_final.iloc[i,j] = np.average(locals()['return_data_{}{}'.format(i,j)],axis=1)/np.array(np.std(locals()['return_data_{}{}'.format(i,j)],axis=1))
    # 종목 변화율
for n in range(3,65):
    for i in range(0,4):
        for j in range(0,4):
            len1 = len(locals()['data_name_{}{}'.format(i,j)][locals()['data_name_{}{}'.format(i,j)][n-2].notnull()])
            aaa=locals()['data_name_{}{}'.format(i,j)].loc[:,[n-3,n-2]]
            bbb=pd.DataFrame(aaa.stack().value_counts())
            len2=len(bbb[bbb[0]==2])
            locals()['data_name_{}{}'.format(i,j)].loc[200,n-2]=(len1-len2)/len1    
            qqqqq=locals()['data_name_{}{}'.format(i,j)].loc[200,1:]
            turnover.iloc[i,j]=np.mean(qqqqq,axis=0)      
             
                  
#==============================================================================
# dividend yeild & PER
#==============================================================================
import pandas as pd
import numpy as np

ni = pd.read_pickle('ni')
raw_data = pd.read_pickle('raw_data')
size = pd.read_pickle('size')
rtn = pd.read_pickle('rtn')
equity = pd.read_pickle('equity')
cash_div = pd.read_pickle('cash_div')

return_data = np.zeros((5,63))
return_data = pd.DataFrame(return_data)

for i in range(0,4):
    for j in range(0,4):
        locals()['return_data_{}{}'.format(i,j)] = pd.DataFrame(np.zeros((1,63)))
        locals()['beta_{}{}'.format(i,j)] = pd.DataFrame(np.zeros((1,822)))
        locals()['beta_sum_{}{}'.format(i,j)] = pd.DataFrame(np.zeros((1,822)))
        locals()['data_name_{}{}'.format(i,j)] = pd.DataFrame(np.zeros((80,63)))
        




for n in range(3,66):
    
    data_big = raw_data[(raw_data[n] == 1)|(raw_data[n] == 2)|(raw_data[n]==3)]
    data_big = data_big.loc[:,[1,n]]
    data = pd.concat([data_big, size[n], cash_div[n], ni[n]],axis=1,join='inner',ignore_index=True)
    data.columns = ['name','group','size','cash_div','ni']
    data['div_yield']=data['cash_div']/data['size']
    data['1/per']=data['ni']/data['size']
    
#    data=data[data['div_yield']>0]
    data=data[data['div_yield'].notnull()]
    data=data[data['1/per'].notnull()]    # per가 NAN인 Row 제외
    
        
    data_size= len(data)     # Row count
    data=data.assign(rnk_per=np.floor(data['1/per'].rank(method='first')/(data_size/4+1/4)))             
    data=data.assign(rnk_div=np.floor(data.groupby(['rnk_per'])['div_yield'].rank(method='first')/(data_size/16+1/4)))
    
      

    for i in range(0,4):
        for j in range(0,4):
                locals()['data_{}{}'.format(i,j)] = data[(data['rnk_per']==i)&(data['rnk_div']==j)]  
                locals()['data_{}{}'.format(i,j)] = pd.concat([locals()['data_{}{}'.format(i,j)],rtn[n-3]],axis=1,join='inner',ignore_index=True) #수익률 매칭
                locals()['data_name_{}{}'.format(i,j)][n-3] = locals()['data_{}{}'.format(i,j)][0].reset_index(drop=True)
                locals()['data_{}{}'.format(i,j)]=locals()['data_{}{}'.format(i,j)][locals()['data_{}{}'.format(i,j)][9].notnull()]
                locals()['data_{}{}'.format(i,j)]=locals()['data_{}{}'.format(i,j)][locals()['data_{}{}'.format(i,j)][9]>0]
                locals()['return_data_{}{}'.format(i,j)].iloc[0,n-3]=np.mean(locals()['data_{}{}'.format(i,j)][9])
            
                    
    if n == 65 : 
        pass

return_final=pd.DataFrame(np.zeros((4,4)))    
sharpe_final=pd.DataFrame(np.zeros((4,4)))

for i in range(0,4):
    for j in range(0,4):
        return_final.iloc[i,j] = np.product(locals()['return_data_{}{}'.format(i,j)],axis=1)   #np.product로 하면 누적, np.average
        #샤프비율 저장    
        sharpe_final.iloc[i,j] = np.average(locals()['return_data_{}{}'.format(i,j)],axis=1)/np.array(np.std(locals()['return_data_{}{}'.format(i,j)],axis=1))
    # 종목 변화율
for n in range(3,65):
    for i in range(0,4):
        for j in range(0,4):
            len1 = len(locals()['data_name_{}{}'.format(i,j)][locals()['data_name_{}{}'.format(i,j)][n-2].notnull()])
            aaa=locals()['data_name_{}{}'.format(i,j)].loc[:,[n-3,n-2]]
            bbb=pd.DataFrame(aaa.stack().value_counts())
            len2=len(bbb[bbb[0]==2])
            locals()['data_name_{}{}'.format(i,j)].loc[100,n-2]=(len1-len2)/len1    
                  
                  
                  

#==============================================================================
# PBR x dividend yeild & ROE 
#==============================================================================
import pandas as pd
import numpy as np


raw_data = pd.read_pickle('raw_data')
size = pd.read_pickle('size')
rtn = pd.read_pickle('rtn')
equity = pd.read_pickle('equity')
cash_div = pd.read_pickle('cash_div')
ni = pd.read_pickle('ni')

return_data = np.zeros((5,63))
return_data = pd.DataFrame(return_data)

for i in range(0,4):
    for j in range(0,4):
        locals()['return_data_{}{}'.format(i,j)] = pd.DataFrame(np.zeros((1,63)))
        locals()['beta_{}{}'.format(i,j)] = pd.DataFrame(np.zeros((1,822)))
        locals()['beta_sum_{}{}'.format(i,j)] = pd.DataFrame(np.zeros((1,822)))
        locals()['data_name_{}{}'.format(i,j)] = pd.DataFrame(np.zeros((80,63)))
        



for n in range(3,66):
    
    data_big = raw_data[(raw_data[n] == 1)|(raw_data[n] == 2)|(raw_data[n]==3)]
    data_big = data_big.loc[:,[1,n]]
    data = pd.concat([data_big, size[n], cash_div[n], equity[n],ni[n]],axis=1,join='inner',ignore_index=True)
    data.columns = ['name','group','size','cash_div','equity','ni']
        
    data['pbr']=data['size']/data['equity']
    data['div_yield']=data['cash_div']/data['size']
    data['roe']=data['ni']/data['equity']
    
    data=data[data['roe']>0]
    data=data[data['roe'].notnull()] 
#    data=data[data['div_yield']>0]
    data=data[data['div_yield'].notnull()]
    data=data[data['pbr'].notnull()]    # per가 NAN인 Row 제외
    data=data.query('pbr>0')
        
    data_size= len(data)     # Row count
    data=data.assign(rnk_pbr=np.floor(data['pbr'].rank(method='first')/(data_size/4+1/4)))             
    data=data.assign(rnk_div=np.floor(data.groupby(['rnk_pbr'])['div_yield'].rank(method='first')/(data_size/16+1/4)))
    data=data.assign(rnk_roe=np.floor(data.groupby(['rnk_pbr'])['roe'].rank(method='first')/(data_size/16+1/4)))
    
      

    for i in range(0,4):
        for j in range(0,4):
                locals()['data_{}{}'.format(i,j)] = data[(data['rnk_pbr']==i)&(data['rnk_div']==j)&(data['rnk_roe']==j)]  
                locals()['data_{}{}'.format(i,j)] = pd.concat([locals()['data_{}{}'.format(i,j)],rtn[n-3]],axis=1,join='inner',ignore_index=True) #수익률 매칭
                locals()['data_name_{}{}'.format(i,j)][n-3] = locals()['data_{}{}'.format(i,j)][0].reset_index(drop=True)
                locals()['data_{}{}'.format(i,j)]=locals()['data_{}{}'.format(i,j)][locals()['data_{}{}'.format(i,j)][12].notnull()]
                locals()['data_{}{}'.format(i,j)]=locals()['data_{}{}'.format(i,j)][locals()['data_{}{}'.format(i,j)][12]>0]
                locals()['return_data_{}{}'.format(i,j)].iloc[0,n-3]=np.mean(locals()['data_{}{}'.format(i,j)][12])
            
                    
    if n == 65 : 
        pass

return_final=pd.DataFrame(np.zeros((4,4)))    
sharpe_final=pd.DataFrame(np.zeros((4,4)))

for i in range(0,4):
    for j in range(0,4):
        return_final.iloc[i,j] = np.product(locals()['return_data_{}{}'.format(i,j)],axis=1)   #np.product로 하면 누적, np.average
        #샤프비율 저장    
        sharpe_final.iloc[i,j] = np.average(locals()['return_data_{}{}'.format(i,j)],axis=1)/np.array(np.std(locals()['return_data_{}{}'.format(i,j)],axis=1))
    # 종목 변화율
for n in range(3,65):
    for i in range(0,4):
        for j in range(0,4):
            len1 = len(locals()['data_name_{}{}'.format(i,j)][locals()['data_name_{}{}'.format(i,j)][n-2].notnull()])
            aaa=locals()['data_name_{}{}'.format(i,j)].loc[:,[n-3,n-2]]
            bbb=pd.DataFrame(aaa.stack().value_counts())
            len2=len(bbb[bbb[0]==2])
            locals()['data_name_{}{}'.format(i,j)].loc[100,n-2]=(len1-len2)/len1    
                  