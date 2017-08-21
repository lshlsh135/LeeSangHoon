# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 15:18:44 2017

@author: SH-NoteBook
"""
#==============================================================================
# size_index 설명 : 1 은 대형주 2는 중형주 3은 소형주 -> 중소형주(2,3), 코스피전체(1,2,3)도 해보아야함
# strategy_index : 1은 저 per, 2는 저 pbr 전략, 3은 ROE, 4는 영업현금흐름
# 승률 계산도 추가
#==============================================================================
import pandas as pd
import numpy as np

size_index = 2 # choose size grouping number  1은 대형주
return_data = np.zeros((5,63))
return_data = pd.DataFrame(return_data)
raw_data = pd.read_excel('exercise_v01.xlsx',sheetname='Raw_data1',header=None)
size = pd.read_excel('exercise_v01.xlsx',sheetname='시가총액1',header=None)
ni = pd.read_excel('exercise_v01.xlsx',sheetname='당기순이익1',header=None)
rtn = pd.read_excel('exercise_v01.xlsx',sheetname='수익률1',header=None)
equity = pd.read_excel('exercise_v01.xlsx',sheetname='자본총계1',header=None)
operate = pd.read_excel('exercise_v01.xlsx',sheetname='영업현금흐름1',header=None)
kospi_quarter = pd.read_pickle('kospi_quarter')

for i in range(1,6):
    locals()['data_name_{}'.format(i)] = pd.DataFrame(np.zeros((200,63)))

turnover = pd.DataFrame(np.zeros((5,1)))

strategy_index = 1 # 1은 PER


if strategy_index == 1:
    for n in range(3,66):
        
        data_big = raw_data[(raw_data[n] == 1)|(raw_data[n] == 2)|(raw_data[n]==3)]
        data_big = data_big.loc[:,[1,n]]
        data = pd.concat([data_big, size[n], ni[n]],axis=1,join='inner',ignore_index=True)
        data.columns = ['name','group','size','ni']
        data['1/per']=data['ni']/data['size']
    
        data=data[data['1/per'].notnull()]    # per가 NAN인 Row 제외
        data_size= len(data)     # Row count
        data=data.assign(rnk=np.floor(data['1/per'].rank(method='first')/(data_size/5+1/5)))          
                        
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
    
    #np.tile은 matlab에서 repmat과 같은 함수(똑같은 row 5개 만들어서 행렬로 만들어줌)
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
            

       
elif strategy_index == 2:
        for n in range(3,66):
          
            data_big = raw_data[(raw_data[n] == 1)|(raw_data[n] == 2)|(raw_data[n]==3)]
            data_big = data_big.loc[:,[1,n]]
            data = pd.concat([data_big, size[n], equity[n]],axis=1,join='inner',ignore_index=True)
            data.columns = ['name','group','size','equity']
            data['pbr']=data['size']/data['equity']
        
            data=data[data['pbr'].notnull()]    # per가 NAN인 Row 제외
            data=data.query('pbr>0')
            data_size= len(data)     # Row count
            data=data.assign(rnk=np.floor(data['pbr'].rank(method='first')/(data_size/5+1/5)))          
                            
            data_5=data.query('5>rnk>3')   # 4
            data_4=data.query('4>rnk>2')   # 3
            data_3=data.query('3>rnk>1')   # 2
            data_2=data.query('2>rnk>0')   # 1
            data_1=data.query('1>rnk>-1')  # 0
                
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
            


elif strategy_index == 3:
        for n in range(3,66):
            
            data_big = raw_data[(raw_data[n] == 1)|(raw_data[n] == 2)|(raw_data[n]==3)]
            data_big = data_big.loc[:,[1,n]]
            data = pd.concat([data_big, ni[n], equity[n]],axis=1,join='inner',ignore_index=True)
            data.columns = ['name','group','ni','equity']
            data['roe']=data['ni']/data['equity']
            data=data[data['roe']>0]
#            data=data[data['1/roe'].notnull()]    
            data_size= len(data)     # Row count
            data=data.assign(rnk=np.floor(data['roe'].rank(method='first')/(data_size/5+1/5)))          
                            
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
            

elif strategy_index == 4:
        for n in range(3,66):
            
            data_big = raw_data[(raw_data[n] == 1)|(raw_data[n] == 2)|(raw_data[n]==3)]
            data_big = data_big.loc[:,[1,n]]
            data = pd.concat([data_big, operate[n], equity[n]],axis=1,join='inner',ignore_index=True)
            data.columns = ['name','group','operate','equity']
            data['oe']=data['operate']/data['equity']
        
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
            
            for i in range(1,6):
                locals()['data_name_{}'.format(i)][n-3] = locals()['data_{}'.format(i)][0].reset_index(drop=True)

            
            return_data.iloc[0,n-3]=np.mean(data_1[6])    # 각각  누적수익률 기록
            return_data.iloc[1,n-3]=np.mean(data_2[6])
            return_data.iloc[2,n-3]=np.mean(data_3[6])
            return_data.iloc[3,n-3]=np.mean(data_4[6])
            return_data.iloc[4,n-3]=np.mean(data_5[6])
            if n == 65 : 
                pass
            return_data=return_data.replace(np.nan,1)
            
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
                if len1>0:
                    aaa=locals()['data_name_{}'.format(i)].loc[:,[n-3,n-2]]
                    bbb=pd.DataFrame(aaa.stack().value_counts())
                    len2=len(bbb[bbb[0]==2])
                    locals()['data_name_{}'.format(i)].loc[200,n-2]=(len1-len2)/len1
                    qqqqq=locals()['data_name_{}'.format(i)].iloc[200,1:]
                    turnover.iloc[i-1,:]=np.mean(qqqqq,axis=0)

