# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 09:02:25 2017

@author: SH-NoteBook
"""


#==============================================================================
# Dependent double sorting 1) PBR 2) OPerating Income    3x3
#==============================================================================
import pandas as pd
import numpy as np


raw_data = pd.read_excel('exercise_v01.xlsx',sheetname='Raw_data1',header=None)
size = pd.read_excel('exercise_v01.xlsx',sheetname='시가총액1',header=None)
ni = pd.read_excel('exercise_v01.xlsx',sheetname='당기순이익1',header=None)
rtn = pd.read_excel('exercise_v01.xlsx',sheetname='수익률1',header=None)
equity = pd.read_excel('exercise_v01.xlsx',sheetname='자본총계1',header=None)
operate = pd.read_excel('exercise_v01.xlsx',sheetname='영업현금흐름1',header=None)
operate_income = pd.read_excel('exercise_v01.xlsx',sheetname='영업이익1',header=None)     


return_data = np.zeros((5,63))
return_data = pd.DataFrame(return_data)
for i in range(0,3):
    for j in range(0,3):
        locals()['return_data_{}{}'.format(i,j)] = pd.DataFrame(np.zeros((1,63)))
        locals()['data_name_{}{}'.format(i,j)] = pd.DataFrame(np.zeros((80,63)))
        
for n in range(3,66):
    
    data_big = raw_data[(raw_data[n] == 1)|(raw_data[n] == 2)|(raw_data[n]==3)]
    data_big = data_big.loc[:,[1,n]]
    data = pd.concat([data_big, size[n], equity[n], operate_income[n]],axis=1,join='inner',ignore_index=True)
    data.columns = ['name','group','size','equity','operate_income']
    data['pbr']=data['size']/data['equity']
    data['oe']=data['operate_income']/data['equity']
    data=data[data['oe']>0]
    data=data[data['pbr'].notnull()]    # per가 NAN인 Row 제외
    data=data.query('pbr>0')
    data_size= len(data)     # Row count    
    data=data.assign(rnk_pbr=np.floor(data['pbr'].rank(method='first')/(data_size/3+1/3)))
    data=data.assign(rnk_oe=np.floor(data.groupby(['rnk_pbr'])['oe'].rank(method='first')/(data_size/9+1/3)))
    

    for i in range(0,3):
        for j in range(0,3):
                locals()['data_{}{}'.format(i,j)] = data[(data['rnk_pbr']==i)&(data['rnk_oe']==j)]  
                locals()['data_{}{}'.format(i,j)] = pd.concat([locals()['data_{}{}'.format(i,j)],rtn[n-3]],axis=1,join='inner',ignore_index=True) #수익률 매칭
                locals()['data_name_{}{}'.format(i,j)][n-3] = locals()['data_{}{}'.format(i,j)][0].reset_index(drop=True)
                locals()['return_data_{}{}'.format(i,j)].iloc[0,n-3]=np.mean(locals()['data_{}{}'.format(i,j)][9])

    if n == 65 : 
        pass

return_final=pd.DataFrame(np.zeros((3,3)))    

for i in range(0,3):
    for j in range(0,3):
        return_final.iloc[i,j] = np.product(locals()['return_data_{}{}'.format(i,j)],axis=1)   #np.product로 하면 누적, np.average
        
    # 종목 변화율
for n in range(3,65):
    for i in range(0,3):
        for j in range(0,3):
            len1 = len(locals()['data_name_{}{}'.format(i,j)][locals()['data_name_{}{}'.format(i,j)][n-2].notnull()])
            aaa=locals()['data_name_{}{}'.format(i,j)].loc[:,[n-3,n-2]]
            bbb=pd.DataFrame(aaa.stack().value_counts())
            len2=len(bbb[bbb[0]==2])
            locals()['data_name_{}{}'.format(i,j)].loc[len1,n-2]=(len1-len2)/len1    
    
    
    
    
    