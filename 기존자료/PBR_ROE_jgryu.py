# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 10:30:19 2017

@author: nice142
"""

import pandas as pd
import numpy as np

raw_data = pd.read_excel('exercise_v01.xlsx', sheetname = 'Raw_data1', header = None)
size = pd.read_excel('exercise_v01.xlsx',sheetname='시가총액1',header=None)
ni = pd.read_excel('exercise_v01.xlsx', sheetname = '당기순이익1', header = None)
rtn = pd.read_excel('exercise_v01.xlsx', sheetname = '수익률1', header = None)
equity = pd.read_excel('exercise_v01.xlsx', sheetname = '자본총계1', header = None)

num_sort = 4 # n x n

for n in range(3,66):
            
     data_kospi = raw_data[(raw_data[n] == 1)|(raw_data[n] == 2)|(raw_data[n] == 3)]
     data_kospi = data_kospi.loc[:,[1,n]]
     data = pd.concat([data_kospi, equity[n], size[n], ni[n], rtn[n-3]], axis = 1, join = 'inner', ignore_index = True)
     data.columns = ['name','group','book','size','ni', 'rtn']
     data['pbr'] = data['size']/data['book']
     data['roe'] = data['ni']/data['book']
     
     data = data.replace([np.inf, -np.inf],np.nan)      
     data = data[data['roe'].notnull()]
     data = data[data['pbr'].notnull()]
     data = data[data['rtn'].notnull()]
     data = data.query('roe>0')
     data = data.query('pbr>0')
     
     # dependent sorting
     len1 = len(data)     # Row count
     data = data.assign(rnk_pbr = np.floor(data['pbr'].rank(method = 'first')/((len1 + 1) / num_sort)))          
         #두번째로 sorting, 먼저 각각의 개수를 len2로 count 후 data에 붙여서 rank 매김
     len2 = data.groupby(['rnk_pbr'])['roe'].size()
     len2 = len2.to_frame().reset_index()
     len2.columns = ['rnk_pbr', 'count']
     data = data.merge(len2, left_on = 'rnk_pbr', right_on = 'rnk_pbr')
     data = data.assign(rnk_roe = data.groupby(['rnk_pbr'])['roe'].rank(method='first'))
     data['rnk_roe'] = np.floor(data['rnk_roe']/((data['count'] + 1)/num_sort))
        
     data = data.sort_values(by = ['rnk_pbr', 'rnk_roe'])
     if n == 3:
         ret = data.groupby(['rnk_roe','rnk_pbr']).mean()
         ret = ret['rtn']
     elif n == 65: 
         pass
     else:
         ret_temp = data.groupby(['rnk_roe','rnk_pbr']).mean()
         ret = pd.concat([ret, ret_temp['rtn']], axis = 1, join ='outer', ignore_index = True)
     
ret = ret.replace(np.nan, 1)
ret_final = np.product(ret, axis = 1)