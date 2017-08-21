# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 16:21:45 2017

@author: nice142
"""

import pandas as pd
import numpy as np

n = 3 # choose column index - date
size_index = 1 # choose size grouping number

raw_data = pd.read_excel('exercise_v01.xlsx',sheetname='Raw_data1',header=None)

data_big = raw_data[(raw_data[n] == size_index)]
data_big = data_big.loc[:,[1,n]]

size = pd.read_excel('exercise_v01.xlsx',sheetname='시가총액1',header=None)
ni = pd.read_excel('exercise_v01.xlsx',sheetname='당기순이익1',header=None)
adjprc = pd.read_excel('exercise_v01.xlsx',sheetname='수정주가1',header=None)

data = pd.concat([data_big, size[n], ni[n], adjprc[n]], axis = 1, join = 'inner', ignore_index = True)
data.columns = ['name', 'group', 'size', 'ni', 'adjprc']
data['1/per'] = data['ni'] / data['size'] 

data=data[data['1/per'].notnull()]
data_size= len(data) 
data=data.assign(rnk=np.floor(data['1/per'].rank(method='first')/((data_size+1)/5)))

data_top=data.query('rnk == 0')
data_bottom=data.query('rnk == 4')
