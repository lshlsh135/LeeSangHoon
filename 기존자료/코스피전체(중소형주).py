# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 10:58:18 2017

@author: SH-NoteBook
"""

import pandas as pd
import numpy as np


return_data = np.zeros((5,63))
return_data = pd.DataFrame(return_data)
raw_data = pd.read_excel('exercise_v01.xlsx',sheetname='Raw_data1',header=None)
size = pd.read_excel('exercise_v01.xlsx',sheetname='시가총액1',header=None)
ni = pd.read_excel('exercise_v01.xlsx',sheetname='당기순이익1',header=None)
rtn = pd.read_excel('exercise_v01.xlsx',sheetname='수익률1',header=None)
equity = pd.read_excel('exercise_v01.xlsx',sheetname='자본총계1',header=None)
operate = pd.read_excel('exercise_v01.xlsx',sheetname='영업현금흐름1',header=None)
operate1 = pd.read_excel('exercise_v01.xlsx',sheetname='분기영업현금흐름1',header=None)
strategy_index = 4 # 1은 PER
#==============================================================================
# 2 3 이니깐 중소형주
#==============================================================================
if strategy_index == 4:   #영업현금흐름/시총
        for n in range(3,66):
            
            data_big = raw_data[(raw_data[n] == 2)|(raw_data[n]==3)]
            data_big = data_big.loc[:,[1,n]]
            data = pd.concat([data_big, operate[n], size[n]],axis=1,join='inner',ignore_index=True)
            data.columns = ['name','group','operate','size']
            data['oe']=data['operate']/data['size']
        
            data=data.replace([np.inf, -np.inf],np.nan)      
            
            data=data[data['oe'].notnull()]    # per가 NAN인 Row 제외
            
            data=data.query('oe>0')
            data_size= len(data)     # Row count
            data=data.assign(rnk=np.floor(data['oe'].rank(method='first')/(data_size/5+1/5)))          
                            
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
            
            return_data.iloc[0,n-3]=np.mean(data_1[6])    # 각각  누적수익률 기록
            return_data.iloc[1,n-3]=np.mean(data_2[6])
            return_data.iloc[2,n-3]=np.mean(data_3[6])
            return_data.iloc[3,n-3]=np.mean(data_4[6])
            return_data.iloc[4,n-3]=np.mean(data_5[6])
            if n == 65 : 
                pass
            return_data=return_data.replace(np.nan,1)
            
            return_final=np.product(return_data,axis=1)
#==============================================================================
# 코스피 전체
#==============================================================================
if strategy_index == 4:   #영업현금흐름/시총
        for n in range(3,66):
            
            data_big = raw_data[(raw_data[n] == 1)|(raw_data[n] == 2)|(raw_data[n]==3)]
            data_big = data_big.loc[:,[1,n]]
            data = pd.concat([data_big, operate[n], size[n]],axis=1,join='inner',ignore_index=True)
            data.columns = ['name','group','operate','size']
            data['oe']=data['operate']/data['size']
        
            data=data.replace([np.inf, -np.inf],np.nan)      
            
            data=data[data['oe'].notnull()]    # per가 NAN인 Row 제외
            
            data=data.query('oe>0')
            data_size= len(data)     # Row count
            data=data.assign(rnk=np.floor(data['oe'].rank(method='first')/(data_size/5+1/5)))          
                            
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
            
            return_data.iloc[0,n-3]=np.mean(data_1[6])    # 각각  누적수익률 기록
            return_data.iloc[1,n-3]=np.mean(data_2[6])
            return_data.iloc[2,n-3]=np.mean(data_3[6])
            return_data.iloc[3,n-3]=np.mean(data_4[6])
            return_data.iloc[4,n-3]=np.mean(data_5[6])
            if n == 65 : 
                pass
            return_data=return_data.replace(np.nan,1)
            
            return_final=np.product(return_data,axis=1)