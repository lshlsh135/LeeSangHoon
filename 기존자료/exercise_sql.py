# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 13:06:53 2017

@author: SH-NoteBook
"""

import pandas as pd
import numpy as np
#%%==============================================================================
# Data Download
#==============================================================================
url = 'https://raw.github.com/pandas-dev/pandas/master/pandas/tests/data/tips.csv'
tips = pd.read_csv(url)
    
#%%==============================================================================
# Select
#==============================================================================
tips.head()                             #.head() 라는건 출력하는 row의 수를 정하는듯 () 빈칸으로 두면 default 값 5.
tips[['total_bill']]                    #index가 total_bill 인 column만 출력

#%%==============================================================================
# Where
#==============================================================================
tips[tips['sex']=='Male']               #index 'sex'에서 male 인것만 고름, 개좋은건 좌측 Row index가 살아있음 이용가능해보임

is_dinner = tips['time']=='Dinner'      #이렇게 하면 True or False 로만 정리가 됨
is_dinner.value_counts()                #.value_counts() 는 series type만 된다. DataFrame에는 안되는군, True, False의 수를 세어줌
#%%==============================================================================
# Where + and& / Or|
#==============================================================================

tips[(tips['time']=='Dinner')&(tips['tip']>5.00)]             # 논리 비교 할때 숫자에는 '' 안붙임
tips[(tips['size']>=5.00)|(tips['total_bill']>45)]


#%%==============================================================================
# Null Checking     - > (1)isnull() , (2)notnull()
#==============================================================================
frame = pd.DataFrame({'col1':['A','B',np.NaN,'C','D'],              #Frame 이라는 NaN 을 포함한 Data Frame을 생성
....:'col2':['F',np.NaN,'G','H','I']})                              #코드가 너무 길면 ....: 로 다음줄 연결 가

frame

frame[frame['col1'].isnull()]
frame[frame['col2'].notnull()]
    
frame2 =  pd.DataFrame({'col1':['A','B',np.NaN,'C','D'],'col2':['F',np.NaN,np.NaN,'H','I']})            #모든 Row가 NaN인거 생성해봄

frame2[(frame2['col1'].notnull())&(frame2['col2'].notnull())]               #NAN이 Row를 제외한 결과 ㅋㅋㅋ


#==============================================================================
# Group by
#==============================================================================

tips.groupby('sex').size()     #size()랑 count()의 차이,

tips.groupby('sex').count()

tips.groupby('sex')['total_bill'].count()  #특정 column

tips.groupby('day').size()

tips.groupby('day').agg({'tip':np.mean,'day':np.size})              #day로 볼때 tip의 평균과 day수

tips.groupby(['smoker','day']).agg({'tip':[np.size,np.mean]})
            
            
#==============================================================================
# Join
#==============================================================================
            
df1 = pd.DataFrame({'key': ['A', 'B', 'C', 'D'],
   ....:                     'value': np.random.randn(4)})   

df2 = pd.DataFrame({'key': ['B', 'D', 'D', 'E'],
   ....:                     'value': np.random.randn(4)})

a=np.random.randn(4)    # 4x1 matrix 생성
            
            
pd.merge(df1, df2, on='key')      #df1, df2 순서대로 key 가 같은것 합쳐짐

indexed_df2 = df2.set_index('key')   #df2의 key column을 index로 쓰겠다.

pd.merge(df1, indexed_df2, left_on='key', right_index=True)  #primary key 다른거 merge

                           
#==============================================================================
# # show all records from df1
#==============================================================================
                           
pd.merge(df1,df2,on='key',how='left')
                           
 pd.merge(df1, df2, on='key', how='right')       # show all records from df2                    
                          
        
            
#==============================================================================
# Full join            
#==============================================================================
pd.merge(df1, df2, on='key', how='outer')            #how='outer' 이 붙으면 key에 있는 모든거에 대해서 다 나옴

        
#==============================================================================
#Union            
#==============================================================================
df1 = pd.DataFrame({'city': ['Chicago', 'San Francisco', 'New York City'],
   ....:                     'rank': range(1, 4)})            
            
df2 = pd.DataFrame({'city': ['Chicago', 'Boston', 'Los Angeles'],
   ....:                     'rank': [1, 4, 5]})            
            
pd.concat([df1, df2])      #그냥 union all

pd.concat([df1, df2]).drop_duplicates()         

#==============================================================================
#      Top N rows with offset    
#==============================================================================
         
 tips.nlargest(2, columns='tip')  
         
#==============================================================================
#         Top N rows per group
#==============================================================================
         
(tips.assign(rnk=tips.groupby(['day'])['total_bill'].rank(method='first', ascending=False)).query('rnk < 8').sort_values(['day','rnk']))
            
a=tips.assign(rnk=tips.groupby(['day'])['total_bill'].rank(method='average', ascending=False)) #이렇게 하면 각 day별로 total_bill 순으로 rank 매            
 
tips['decile'] = pd.qcut(tips['tip'], 5, labels=None,retbins='optional')
#==============================================================================
# pd.pcut은 box plot 용으로 나눠줌
#==============================================================================
import numpy as np
import pandas as pd
investment_df = pd.DataFrame(np.arange(12), columns=['investment'])
investment_df['decile'] = pd.qcut(investment_df['investment'], 10, labels=False)
investment_df['quintile'] = pd.qcut(investment_df['investment'], 5, labels=False)


#==============================================================================
# assign은 새로운 column 추가하는 것
#==============================================================================


a=tips[['total_bill','tip']]      # 두개의 column만 겨우 모앗다 시발
a=a.assign(rnk=np.floor(a['tip'].rank(method='first')/(244/5+1)))      # grouping + ranking을 성공해버림

          







































