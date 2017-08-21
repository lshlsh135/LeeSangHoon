# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 14:19:11 2017

@author: nice142
"""

# momentum
# monthly rebalacing
# universe: all (no consider about size)

# purpose: momentum + reversal / momentum

import pandas as pd
import numpy as np

rtn_month = pd.read_excel('exercise_v01.xlsx', sheetname = '월별수익률1', header = None)

momrev = np.ones((1155,189))
momrev = pd.DataFrame(momrev)

mom = np.ones((1155,189))
mom = pd.DataFrame(mom)

retm_data = np.zeros((5,189))
retm_data = pd.DataFrame(retm_data)

retm_data_r = np.zeros((5,189))
retm_data_r = pd.DataFrame(retm_data_r)

for i in range(0, 189):
     for n_momrev in range(0, 12):
         momrev[i] = momrev[i] * rtn_month[n_momrev + i]
     for n_mom in range(0, 11):
         mom[i] = mom[i] * rtn_month[n_mom + i]

for i in range(0, 189):
    # only momentum
    data = pd.concat([mom[i], rtn_month[i + 12]], axis = 1, join = 'inner', ignore_index = True)
    data.columns = ['mom', 'retm']
    data = data[data['mom'].notnull()] 
    data = data[data['retm'].notnull()] 
    
    data_size = len(data)     # Row count
    data = data.assign(rnk = np.floor(data['mom'].rank(method = 'first')/((data_size + 1) / 5)))
    
    data_1 = data.query('5>rnk>3')   # 4
    data_2 = data.query('4>rnk>2')   # 3
    data_3 = data.query('3>rnk>1')   # 2
    data_4 = data.query('2>rnk>0')   # 1
    data_5 = data.query('1>rnk>-1')  # 0
    
    retm_data.iloc[0, i] = np.mean(data_1['retm'])    # 각각  누적수익률 기록
    retm_data.iloc[1, i] = np.mean(data_2['retm'])
    retm_data.iloc[2, i] = np.mean(data_3['retm'])
    retm_data.iloc[3, i] = np.mean(data_4['retm'])
    retm_data.iloc[4, i] = np.mean(data_5['retm'])
    
    # momentum + reversal
    data_r = pd.concat([momrev[i], rtn_month[i + 12]], axis = 1, join = 'inner', ignore_index = True)
    data_r.columns = ['momrev', 'retm']
    data_r = data_r[data_r['momrev'].notnull()] 
    data_r = data_r[data_r['retm'].notnull()] 
    
    data_size_r = len(data)     # Row count
    data_r = data_r.assign(rnk = np.floor(data_r['momrev'].rank(method = 'first')/((data_size_r + 1) / 5)))
    
    data_1_r = data_r.query('5>rnk>3')   # 4
    data_2_r = data_r.query('4>rnk>2')   # 3
    data_3_r = data_r.query('3>rnk>1')   # 2
    data_4_r = data_r.query('2>rnk>0')   # 1
    data_5_r = data_r.query('1>rnk>-1')  # 0
    
    retm_data_r.iloc[0, i] = np.mean(data_1_r['retm'])    # 각각  누적수익률 기록
    retm_data_r.iloc[1, i] = np.mean(data_2_r['retm'])
    retm_data_r.iloc[2, i] = np.mean(data_3_r['retm'])
    retm_data_r.iloc[3, i] = np.mean(data_4_r['retm'])
    retm_data_r.iloc[4, i] = np.mean(data_5_r['retm'])
    
    if i == 188 : 
        pass  

retm_final = np.product(retm_data, axis = 1)
retm_final_r = np.product(retm_data_r, axis = 1)                 