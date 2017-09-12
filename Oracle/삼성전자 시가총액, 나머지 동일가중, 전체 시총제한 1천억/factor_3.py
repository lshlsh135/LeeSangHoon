# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 08:31:31 2017

@author: SH-NoteBook
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 07:34:45 2017

@author: SH-NoteBook
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 15:18:59 2017

@author: SH-NoteBook
"""


import numpy as np
import pandas as pd
class factor_3:
 
    def __init__(self,raw_data,rebalancing_date,month_date,col_num,col_num2,col_num3):
        self.raw_data = raw_data
        self.rebalancing_date = rebalancing_date
        self.month_date = month_date
        self.col_num = col_num
        self.col_num2 = col_num2
        self.col_num3 = col_num3
        
    def factor_3(self):
        col_length = len(self.rebalancing_date)-1 #rebalancing_date의 길이는 66이다. range로 이렇게 하면 0부터 65까지 66개의 i 가 만들어진다. -1을 해준건 실제 수익률은 -1개가 생성되기 때문.

        group_goal = 5  #몇개의 그룹으로 나눌지 설정한다.
        
        for i in range(group_goal):
            locals()['data_{}'.format(i)] = pd.DataFrame(np.zeros((1000,col_length)))
        
        for i in range(group_goal):
            locals()['data_name_{}'.format(i)] = pd.DataFrame(np.zeros((1000,col_length)))
            
        
        return_data = pd.DataFrame(np.zeros((group_goal,col_length)))
        return_final = pd.DataFrame(np.zeros((group_goal,1)))
        return_month_data = pd.DataFrame(np.zeros((group_goal,3*col_length)))
        turnover = pd.DataFrame(np.zeros((5,1)))
        turnover_quarter = pd.DataFrame(np.zeros((group_goal,col_length)))
        for n in range(col_length): 
            first_data = self.raw_data[self.raw_data['TRD_DATE']==self.rebalancing_date.iloc[n,0]] # rebalanging할 날짜에 들어있는 모든 db data를 받아온다.
            target_data = self.raw_data[self.raw_data['TRD_DATE']==self.rebalancing_date.iloc[n+1,0]]
            target_data = target_data.loc[:,['TRD_DATE','GICODE','ADJ_PRC']]
            first_data = first_data[(first_data['CAP_SIZE']==1)|(first_data['CAP_SIZE']==2)|(first_data['CAP_SIZE']==3)|(first_data['ISKOSDAQ']=='KOSDAQ')]
            first_data = first_data[first_data['MARKET_CAP']>100000000000]
            #first_data = first_data[first_data['EQUITY'].notnull()] # 처음 받아온 전체 data 에서 equity가 없는 종목은 제외한다 -> equity가 null값이라는건 저 당시에 데이타가 존재하지 않는다는 것.
            
            first_data = first_data[first_data.iloc[:,self.col_num].notnull()] # 1/PER이 NULL인걸 제외한다. EQUITY 가 NULL인걸 미리 제거하지 않아도 여기서 제거됨.
            first_data = first_data[first_data.iloc[:,self.col_num2].notnull()]
            first_data = first_data[first_data.iloc[:,self.col_num3].notnull()]
            data_length = len(first_data) # 몇개의 종목이 rebalanging_date때 존재했는지 본다.
            #월별 수익률을 구하기 위해 month_date 에서 필요한 날짜가 몇번쨰 row에 있는지 확인
            past_month=self.month_date.loc[self.month_date['MONTH_DATE']==self.rebalancing_date.iloc[n,0]].index[0]
            cur_month=self.month_date.loc[self.month_date['MONTH_DATE']==self.rebalancing_date.iloc[n+1,0]].index[0]
            
            first_data=first_data.assign(rnk1=np.floor(first_data.iloc[:,self.col_num].rank(method='first')))
            first_data=first_data.assign(rnk2=np.floor(first_data.iloc[:,self.col_num2].rank(method='first')))
            first_data=first_data.assign(rnk3=np.floor(first_data.iloc[:,self.col_num3].rank(method='first')))
            first_data=first_data.assign(rnk_sum=first_data['rnk1']+first_data['rnk2']+first_data['rnk3'])
            first_data=first_data.assign(rnk=np.floor(first_data.loc[:,'rnk_sum'].rank(method='first')/(data_length/group_goal+1/group_goal)))          # rnk가 클수록 저평가
            
            sum_data = pd.merge(target_data,first_data,on='GICODE') # 3개월치 수익률을 구하기 위해 3개월 후 존재하는 data에 현재 data를 붙임
            sum_data['3M_RETURN'] = sum_data['ADJ_PRC_x']/sum_data['ADJ_PRC_y'] # 3개월동안의 종목 수익률
            
            first_data = first_data.loc[:,['TRD_DATE','GICODE','ADJ_PRC']]
            for i in range(past_month+1,cur_month): # 3개월치의 월별 수익률을 구하기 위해선 4개의 price 데이터가 필요한데 2개밖에 없으니 2개를 더 받아온다.
                second_data = self.raw_data[self.raw_data['TRD_DATE']==self.month_date.iloc[i,0]]  #월별 데이터를 받아와서
                second_data = second_data.loc[:,['TRD_DATE','GICODE','ADJ_PRC']]   # 간단하게 만든다음
                first_data = pd.merge(first_data,second_data,on='GICODE')   # first_data와 합친다
            
            first_data['1ST_RETURN'] =  first_data['ADJ_PRC_y']/ first_data['ADJ_PRC_x']   #0->1 , 즉 첫 한개월간의 수익률
            first_data['2ND_RETURN'] =  first_data['ADJ_PRC']/ first_data['ADJ_PRC_y']# 1->2 한달이후 한달간 수익률
            first_data = first_data.loc[:,['GICODE','1ST_RETURN','2ND_RETURN']] #데이터를 간단하게 만들어준다음
            sum_data = pd.merge(sum_data,first_data,on='GICODE') # 기존 data와 합친다.
            sum_data['2M_CUM_RETURN'] = sum_data['1ST_RETURN'] * sum_data['2ND_RETURN'] 
            
           
            #숫자가 클수록 1/PER 가 큰거니 저평가
            for i in range(group_goal):
                locals()['data_{}'.format(i)] = sum_data[sum_data['rnk']==i]
               
            for i in range(group_goal):
                locals()['data_name_{}'.format(i)][n] = locals()['data_{}'.format(i)]['CO_NM'].reset_index(drop=True)
                
            for i in range(group_goal):
                return_data.iloc[i,n] = np.mean(locals()['data_{}'.format(i)]['3M_RETURN'])
                
            for i in range(group_goal):
                return_month_data.iloc[i,3*n]= np.mean(locals()['data_{}'.format(i)]['1ST_RETURN'])
                return_month_data.iloc[i,3*n+1]= np.mean(locals()['data_{}'.format(i)]['2M_CUM_RETURN']) / np.mean(locals()['data_{}'.format(i)]['1ST_RETURN'])
                return_month_data.iloc[i,3*n+2]= np.mean(locals()['data_{}'.format(i)]['3M_RETURN']) / np.mean(locals()['data_{}'.format(i)]['2M_CUM_RETURN'])
                
            return_final=np.product(return_data,axis=1)
                    #turnover 계산    
        for n in range(col_length-1):
            for i in range(group_goal):
                len1 = len(locals()['data_name_{}'.format(i)][locals()['data_name_{}'.format(i)][n+1].notnull()])
                aaa=locals()['data_name_{}'.format(i)].loc[:,[n,n+1]]
                bbb=pd.DataFrame(aaa.stack().value_counts())
                len2=len(bbb[bbb[0]==2])
                locals()['data_name_{}'.format(i)].loc[999,n+1]=(len1-len2)/len1
                turnover_quarter.iloc[i,:]=locals()['data_name_{}'.format(i)].loc[999,1:]
                
        turnover=np.mean(turnover_quarter,axis=1)   
        #turnvoer에 1.5% 곱해서 거래비용 계산하기
        #첫기에는 거래비용이 100%이다
        
        turnover_quarter.iloc[:,0]=1
        turnover_quarter = turnover_quarter * 0.01
        return_diff = return_data - turnover_quarter
        return_transaction_cost_final=np.product(return_diff,axis=1)    
            
        #monthly data에도 cost 반영
        import copy   # 엠창 존나 어려운거발견함 장족의 발전이다
        #deep copy랑 swallow copy 가 있는데  a=[1,2,3]을 만들면 a에 [1,2,3]이 저장되는게 아니라
        #[1,2,3]이라는 객체가 생성되고 여기에 a 가 할당됨. 그런데 여기다 a=b 를 해버리면 b도 
        # 저 객체에 할당되어버려서, b를변경하든 a를 변경하든 같이 바뀜. 
        #deep copy를 하면 새로운 객체가 생김.
        return_month_data_costed = copy.deepcopy(return_month_data)
        
        
        # monthly data에 turnover cost를 빼는건, 종목을 변경한 달에 적용...
        for n in range(col_length):
            return_month_data_costed[3*n] = np.subtract(return_month_data[3*n],turnover_quarter[n])
        
            
            
#               
        
            
        return [return_final, return_diff, return_month_data_costed]  # 이렇게 return 하면 list로 받아짐
                
        