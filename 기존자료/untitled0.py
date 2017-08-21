import pandas as pd
import numpy as np


return_data = np.zeros((5,63))
return_data = pd.DataFrame(return_data)

for i in range(0,4):
    for j in range(0,4):
        locals()['return_data_{}{}'.format(i,j)] = pd.DataFrame(np.zeros((1,63)))
        locals()['beta_{}{}'.format(i,j)] = pd.DataFrame(np.zeros((1,822)))
        locals()['beta_sum_{}{}'.format(i,j)] = pd.DataFrame(np.zeros((1,822)))
        locals()['data_name_{}{}'.format(i,j)] = pd.DataFrame(np.zeros((80,63)))
        


raw_data = pd.read_pickle('raw_data')
size = pd.read_pickle('size')
rtn = pd.read_pickle('rtn')
equity = pd.read_pickle('equity')
cash_div = pd.read_pickle('cash_div')
ni = pd.read_pickle('ni')

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
    data=data[data['div_yield']>0]
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

for i in range(0,4):
    for j in range(0,4):
        return_final.iloc[i,j] = np.product(locals()['return_data_{}{}'.format(i,j)],axis=1)   #np.product로 하면 누적, np.average
        
    # 종목 변화율
for n in range(3,65):
    for i in range(0,4):
        for j in range(0,4):
            len1 = len(locals()['data_name_{}{}'.format(i,j)][locals()['data_name_{}{}'.format(i,j)][n-2].notnull()])
            aaa=locals()['data_name_{}{}'.format(i,j)].loc[:,[n-3,n-2]]
            bbb=pd.DataFrame(aaa.stack().value_counts())
            len2=len(bbb[bbb[0]==2])
            locals()['data_name_{}{}'.format(i,j)].loc[100,n-2]=(len1-len2)/len1    
                  # -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 16:53:33 2017

@author: SH-NoteBook
"""

