# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 21:33:25 2017

@author: LSH-I7-4790
"""

# =============================================================================
# 12개월 모멘텀 (직전 1개월 제외)
# =============================================================================
import pandas as pd
import cx_Oracle
import numpy as np

#이거 두개 반드시 선언!
cx0=cx_Oracle.makedsn("localhost",1521,"xe")
connection = cx_Oracle.connect("lshlsh135","2tkdgns2",cx0)


#DATA를 가져온다!!
america_stock_return = pd.read_sql("""select * from america_stock_return where SHRCD = '10' or SHRCD = '11'""",con=connection)
monthly_rebalancing_date = pd.read_sql("""select distinct TRD_DATE from america_stock_return order by TRD_DATE""",con=connection)
col_length = len(monthly_rebalancing_date)-1


return_data = pd.DataFrame(np.zeros((5,col_length-12)))
america_stock_return['MONTHLY_GROSS_RETURN'] = america_stock_return['RET'] + 1
a=america_stock_return.head(500)

for n in range(12,col_length): 

    #wics mid sector Momentum 전략을 먼저
    first_mom = america_stock_return[america_stock_return['TRD_DATE']==monthly_rebalancing_date.iloc[n,0]]
    last_mom = america_stock_return[america_stock_return['TRD_DATE']==monthly_rebalancing_date.iloc[n-11,0]]
    target_mom = america_stock_return[america_stock_return['TRD_DATE']==monthly_rebalancing_date.iloc[n+1,0]].loc[:,['PERMNO','MONTHLY_GROSS_RETURN']]
    last_mom['11M_GROSS_RETURN'] = last_mom.loc[:,'MONTHLY_GROSS_RETURN']
    for i in range(n-10,n): # 직전 1개월 제외한 12개월치 누적수익률구하기
        monyhly_date= america_stock_return[america_stock_return['TRD_DATE']==monthly_rebalancing_date.iloc[i,0]].loc[:,['PERMNO','MONTHLY_GROSS_RETURN']]
        last_mom = pd.merge(last_mom,monyhly_date,on='PERMNO')
        last_mom['11M_GROSS_RETURN'] = last_mom['11M_GROSS_RETURN'] * last_mom['MONTHLY_GROSS_RETURN_y']
        last_mom.drop('MONTHLY_GROSS_RETURN_y',axis=1,inplace=True)
        last_mom.rename(columns={'MONTHLY_GROSS_RETURN_x':'MONTHLY_GROSS_RETURN'},inplace=True)
        
    
    last_mom = last_mom[last_mom['11M_GROSS_RETURN'].notnull()]
    last_mom = pd.merge(last_mom,target_mom,on='PERMNO')
    last_mom = last_mom[last_mom['MONTHLY_GROSS_RETURN_y'].notnull()]
    data_size = len(last_mom)
    last_mom=last_mom.assign(rnk=np.floor(last_mom['11M_GROSS_RETURN'].rank(method='first')/(data_size/5+1/5))) 
        
    
    data_1=last_mom.query('5>rnk>3')   # 4
    data_2=last_mom.query('4>rnk>2')   # 3
    data_3=last_mom.query('3>rnk>1')   # 2
    data_4=last_mom.query('2>rnk>0')   # 1
    data_5=last_mom.query('1>rnk>-1')  # 0    
     
    return_data.iloc[0,n-12]=np.mean(data_1['MONTHLY_GROSS_RETURN_y'])    # 각각  누적수익률 기록
    return_data.iloc[1,n-12]=np.mean(data_2['MONTHLY_GROSS_RETURN_y'])
    return_data.iloc[2,n-12]=np.mean(data_3['MONTHLY_GROSS_RETURN_y'])
    return_data.iloc[3,n-12]=np.mean(data_4['MONTHLY_GROSS_RETURN_y'])
    return_data.iloc[4,n-12]=np.mean(data_5['MONTHLY_GROSS_RETURN_y'])

    return_data = return_data.iloc[:,:1079]
    return_result = np.product(return_data,axis=1)


# =============================================================================
# 12개월 모멘텀 (직전 1개월 포함)
# =============================================================================
import pandas as pd
import cx_Oracle
import numpy as np

#이거 두개 반드시 선언!
cx0=cx_Oracle.makedsn("localhost",1521,"xe")
connection = cx_Oracle.connect("lshlsh135","2tkdgns2",cx0)


#DATA를 가져온다!!
america_stock_return = pd.read_sql("""select * from america_stock_return where SHRCD = '10' or SHRCD = '11'""",con=connection)
monthly_rebalancing_date = pd.read_sql("""select distinct TRD_DATE from america_stock_return order by TRD_DATE""",con=connection)
col_length = len(monthly_rebalancing_date)-1


return_data = pd.DataFrame(np.zeros((5,col_length-12)))
america_stock_return['MONTHLY_GROSS_RETURN'] = america_stock_return['RET'] + 1
a=america_stock_return.head(500)

for n in range(12,col_length): 

    #wics mid sector Momentum 전략을 먼저
    first_mom = america_stock_return[america_stock_return['TRD_DATE']==monthly_rebalancing_date.iloc[n,0]]
    last_mom = america_stock_return[america_stock_return['TRD_DATE']==monthly_rebalancing_date.iloc[n-11,0]]
    target_mom = america_stock_return[america_stock_return['TRD_DATE']==monthly_rebalancing_date.iloc[n+1,0]].loc[:,['PERMNO','MONTHLY_GROSS_RETURN']]
    last_mom['11M_GROSS_RETURN'] = last_mom.loc[:,'MONTHLY_GROSS_RETURN']
    for i in range(n-10,n+1): # 직전 1개월 제외한 12개월치 누적수익률구하기
        monyhly_date= america_stock_return[america_stock_return['TRD_DATE']==monthly_rebalancing_date.iloc[i,0]].loc[:,['PERMNO','MONTHLY_GROSS_RETURN']]
        last_mom = pd.merge(last_mom,monyhly_date,on='PERMNO')
        last_mom['11M_GROSS_RETURN'] = last_mom['11M_GROSS_RETURN'] * last_mom['MONTHLY_GROSS_RETURN_y']
        last_mom.drop('MONTHLY_GROSS_RETURN_y',axis=1,inplace=True)
        last_mom.rename(columns={'MONTHLY_GROSS_RETURN_x':'MONTHLY_GROSS_RETURN'},inplace=True)
        
    
    last_mom = last_mom[last_mom['11M_GROSS_RETURN'].notnull()]
    last_mom = pd.merge(last_mom,target_mom,on='PERMNO')
    last_mom = last_mom[last_mom['MONTHLY_GROSS_RETURN_y'].notnull()]
    data_size = len(last_mom)
    last_mom=last_mom.assign(rnk=np.floor(last_mom['11M_GROSS_RETURN'].rank(method='first')/(data_size/5+1/5))) 
        
    
    data_1=last_mom.query('5>rnk>3')   # 4
    data_2=last_mom.query('4>rnk>2')   # 3
    data_3=last_mom.query('3>rnk>1')   # 2
    data_4=last_mom.query('2>rnk>0')   # 1
    data_5=last_mom.query('1>rnk>-1')  # 0    
     
    return_data.iloc[0,n-12]=np.mean(data_1['MONTHLY_GROSS_RETURN_y'])    # 각각  누적수익률 기록
    return_data.iloc[1,n-12]=np.mean(data_2['MONTHLY_GROSS_RETURN_y'])
    return_data.iloc[2,n-12]=np.mean(data_3['MONTHLY_GROSS_RETURN_y'])
    return_data.iloc[3,n-12]=np.mean(data_4['MONTHLY_GROSS_RETURN_y'])
    return_data.iloc[4,n-12]=np.mean(data_5['MONTHLY_GROSS_RETURN_y'])

    return_data = return_data.iloc[:,:1079]
    return_result = np.product(return_data,axis=1)
