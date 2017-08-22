# -*- coding: utf-8 -*-
"""
Created on Mon Aug 14 08:24:37 2017

@author: SH-NoteBook
"""

import pandas as pd
import numpy as np
import cx_Oracle



#이거 두개 반드시 선언!
cx0=cx_Oracle.makedsn("localhost",1521,"xe")
connection = cx_Oracle.connect("lshlsh135","2tkdgns2",cx0) #이게 실행이 안될때가 있는데
#그때는 services에 들어가서 oracle listner를 실행시켜줘야함


#DATA를 가져온다!!
kospi = pd.read_sql("""select * from kospi_ex""",con=connection)
kosdaq = pd.read_sql("""select * from kosdaq_ex""",con=connection)
rebalancing_date = pd.read_sql("""select * from rebalancing_date""",con=connection)
month_date = pd.read_sql("""select * from month_date""",con=connection)
wics_mid = pd.read_sql("""select * from wics_mid""",con=connection)

raw_data = pd.concat([kospi,kosdaq],axis=0,ignore_index=True).drop_duplicates()   #왜인지 모르겠는데 db에 중복된 정보가 들어가있네 ..? 
col_length = len(rebalancing_date)-1 #rebalancing_date의 길이는 66이다. range로 이렇게 하면 0부터 65까지 66개의 i 가 만들어진다. -1을 해준건 실제 수익률은 -1개가 생성되기 때문.

return_data = pd.DataFrame(np.zeros((1,col_length)))
return_month_data = pd.DataFrame(np.zeros((1,3*col_length)))
quarter_data = pd.DataFrame(np.zeros((1,3*col_length)))
return_final = pd.DataFrame(np.zeros((1,1)))

for n in range(col_length): 
    #wics mid sector Momentum 전략을 먼저
    first_mom = wics_mid[wics_mid['TRD_DATE']==rebalancing_date.iloc[n,0]] 
    cur_mom_row=month_date.loc[month_date['MONTH_DATE']==rebalancing_date.iloc[n,0]].index[0]
    
    #cur_month=month_date.loc[month_date['MONTH_DATE']==rebalancing_date.iloc[n+1,0]].index[0]
    
    mom_return_data_1 = wics_mid[wics_mid['TRD_DATE']==month_date.iloc[cur_mom_row-1,0]] #t-2 data
    mom_return_data_2 = wics_mid[wics_mid['TRD_DATE']==month_date.iloc[cur_mom_row-12,0]] #t-12 data
    mom_return_data_1 = pd.merge(mom_return_data_1,mom_return_data_2,on='GICODE') # 따로따로 계산하려고 했더니 index가 안맞아서 gicode로 merge 했다.
    mom_return_data_1['11M_GROSS_RETURN'] = mom_return_data_1['END_PRICE_x'] / mom_return_data_1['END_PRICE_y'] # 머지하면 index가 필요 없어져서 수익률 계산이 쉬워짐
    
    mom_return_data_1=mom_return_data_1.assign(rnk=np.floor(mom_return_data_1['11M_GROSS_RETURN'].rank(method='first',ascending=False))) # 누적수익률이 높은 섹터별로 ranking
    sector_mom = mom_return_data_1.query('rnk<16') #상위 15 섹터 선택 완료
    
    
    first_data = raw_data[raw_data['TRD_DATE']==rebalancing_date.iloc[n,0]] # rebalanging할 날짜에 들어있는 모든 db data를 받아온다.
    target_data = raw_data[raw_data['TRD_DATE']==rebalancing_date.iloc[n+1,0]] # 다음 리밸런싱 날짜.
    target_data = target_data.loc[:,['TRD_DATE','GICODE','ADJ_PRC']]
    first_data = first_data[(first_data['CAP_SIZE']==1)]
    first_data = first_data[first_data['MARKET_CAP']>100000000000]
    first_data['size_FIF_wisefn'] = first_data['JISU_STOCK']*first_data['FIF_RATIO']*first_data['ADJ_PRC']
    
    samsung = first_data[first_data['CO_NM']=='삼성전자']
    
    first_data = first_data[first_data['EQUITY'].notnull()]
    first_data = first_data[first_data['CASH_DIV_COM'].notnull()]
    first_data = first_data[first_data['ADJ_NI_12M_FWD'].notnull()]

    a=1
        #에너지 섹터
    if (np.sum(first_data['WICS_MID']=='에너지')>0)&(np.sum(sector_mom['CO_NM_x']=='에너지')==1):
        data_에너지 = first_data[first_data['WICS_MID']=='에너지']
        # per, pbr, div_yield 구할때는 전체 시가총액을 사용,
        # 시총비중 구할떄는 free-float
#        data_에너지['size_FIF_wisefn']=data_에너지['size_FIF_wisefn']/1000    #size 단위 thousand
        data_에너지.loc[:,'size_FIF_wisefn']=data_에너지.loc[:,'size_FIF_wisefn']/1000        
        data_에너지['1/pbr']=data_에너지['EQUITY']/data_에너지['MARKET_CAP']
        data_에너지['1/per']=data_에너지['ADJ_NI_12M_FWD']/data_에너지['MARKET_CAP']
        data_에너지['div_yield']=data_에너지['CASH_DIV_COM']/data_에너지['MARKET_CAP']
        
        # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
        data_에너지 = data_에너지.replace([np.inf, -np.inf],np.nan)  
        
        # Null 값 제거
        data_에너지_per = data_에너지[data_에너지['1/per'].notnull()]
        data_에너지_pbr = data_에너지[data_에너지['1/pbr'].notnull()]
        data_에너지_div = data_에너지[data_에너지['div_yield'].notnull()]
    
    
        # 시가총액비중 구함 
        data_에너지_pbr_cap = np.sum(data_에너지_pbr['size_FIF_wisefn'])
        data_에너지_per_cap = np.sum(data_에너지_per['size_FIF_wisefn'])
        data_에너지_div_cap = np.sum(data_에너지_div['size_FIF_wisefn'])
    
        data_에너지_pbr = data_에너지_pbr.assign(market_weight=data_에너지_pbr['size_FIF_wisefn']/data_에너지_pbr_cap)
        data_에너지_per = data_에너지_per.assign(market_weight=data_에너지_per['size_FIF_wisefn']/data_에너지_per_cap)
        data_에너지_div = data_에너지_div.assign(market_weight=data_에너지_div['size_FIF_wisefn']/data_에너지_div_cap)
        
        # 시총가중 평균 
        mu_inv_pbr=np.sum(data_에너지_pbr['1/pbr']*data_에너지_pbr['market_weight'])
        mu_inv_per=np.sum(data_에너지_per['1/per']*data_에너지_per['market_weight'])
        mu_inv_div=np.sum(data_에너지_div['div_yield']*data_에너지_div['market_weight'])
        
        # 시총 가중 표준편자
        std_inv_pbr=np.sqrt(np.sum(np.square(data_에너지_pbr['1/pbr']-mu_inv_pbr)*data_에너지_pbr['market_weight']))
        std_inv_per=np.sqrt(np.sum(np.square(data_에너지_per['1/per']-mu_inv_per)*data_에너지_per['market_weight']))
        std_inv_div=np.sqrt(np.sum(np.square(data_에너지_div['div_yield']-mu_inv_div)*data_에너지_div['market_weight']))
        
        data_에너지1=(data_에너지_pbr['1/pbr']-mu_inv_pbr)/std_inv_pbr
        data_에너지1.name= 'pbr_z'
        data_에너지2=(data_에너지_per['1/per']-mu_inv_per)/std_inv_per
        data_에너지2.name= 'per_z'
        data_에너지3=(data_에너지_div['div_yield']-mu_inv_div)/std_inv_div
        data_에너지3.name= 'div_z'
              
        result_에너지 = pd.concat([data_에너지, data_에너지1, data_에너지2, data_에너지3], axis = 1)
        
        # np.nanmean : nan 값 포함해서 평균 내기!!
        result_에너지 = result_에너지.assign(z_score=np.nanmean(result_에너지.loc[:,['pbr_z','per_z','div_z']],axis=1))
    #    result_temp = result
    
        
        # z_score > 0 인것이 가치주라고 msci에서 하고있음
        locals()['result_{}'.format(a)] =result_에너지[result_에너지['z_score'].notnull()]
        a=a+1
        
    #소재 섹터
    if (np.sum(first_data['WICS_MID']=='소재')>0)&(np.sum(sector_mom['CO_NM_x']=='소재')==1):
        data_소재 = first_data[first_data['WICS_MID']=='소재']
        # per, pbr, div_yield 구할때는 전체 시가총액을 사용,
        # 시총비중 구할떄는 free-float
        data_소재['size_FIF_wisefn']=data_소재['size_FIF_wisefn']/1000    #size 단위 thousand
        data_소재['1/pbr']=data_소재['EQUITY']/data_소재['MARKET_CAP']
        data_소재['1/per']=data_소재['ADJ_NI_12M_FWD']/data_소재['MARKET_CAP']
        data_소재['div_yield']=data_소재['CASH_DIV_COM']/data_소재['MARKET_CAP']
        
        # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
        data_소재 = data_소재.replace([np.inf, -np.inf],np.nan)  
        
        # Null 값 제거
        data_소재_per = data_소재[data_소재['1/per'].notnull()]
        data_소재_pbr = data_소재[data_소재['1/pbr'].notnull()]
        data_소재_div = data_소재[data_소재['div_yield'].notnull()]
    
    
        # 시가총액비중 구함 
        data_소재_pbr_cap = np.sum(data_소재_pbr['size_FIF_wisefn'])
        data_소재_per_cap = np.sum(data_소재_per['size_FIF_wisefn'])
        data_소재_div_cap = np.sum(data_소재_div['size_FIF_wisefn'])
    
        data_소재_pbr = data_소재_pbr.assign(market_weight=data_소재_pbr['size_FIF_wisefn']/data_소재_pbr_cap)
        data_소재_per = data_소재_per.assign(market_weight=data_소재_per['size_FIF_wisefn']/data_소재_per_cap)
        data_소재_div = data_소재_div.assign(market_weight=data_소재_div['size_FIF_wisefn']/data_소재_div_cap)
        
        # 시총가중 평균 
        mu_inv_pbr=np.sum(data_소재_pbr['1/pbr']*data_소재_pbr['market_weight'])
        mu_inv_per=np.sum(data_소재_per['1/per']*data_소재_per['market_weight'])
        mu_inv_div=np.sum(data_소재_div['div_yield']*data_소재_div['market_weight'])
        
        # 시총 가중 표준편자
        std_inv_pbr=np.sqrt(np.sum(np.square(data_소재_pbr['1/pbr']-mu_inv_pbr)*data_소재_pbr['market_weight']))
        std_inv_per=np.sqrt(np.sum(np.square(data_소재_per['1/per']-mu_inv_per)*data_소재_per['market_weight']))
        std_inv_div=np.sqrt(np.sum(np.square(data_소재_div['div_yield']-mu_inv_div)*data_소재_div['market_weight']))
        
        data_소재1=(data_소재_pbr['1/pbr']-mu_inv_pbr)/std_inv_pbr
        data_소재1.name= 'pbr_z'
        data_소재2=(data_소재_per['1/per']-mu_inv_per)/std_inv_per
        data_소재2.name= 'per_z'
        data_소재3=(data_소재_div['div_yield']-mu_inv_div)/std_inv_div
        data_소재3.name= 'div_z'
              
        result_소재 = pd.concat([data_소재, data_소재1, data_소재2, data_소재3], axis = 1)
        
        # np.nanmean : nan 값 포함해서 평균 내기!!
        result_소재 = result_소재.assign(z_score=np.nanmean(result_소재.loc[:,['pbr_z','per_z','div_z']],axis=1))
    #    result_temp = result
    
        
        # z_score > 0 인것이 가치주라고 msci에서 하고있음
        locals()['result_{}'.format(a)] =result_소재[result_소재['z_score'].notnull()]
        a=a+1    
    #자본재 섹터
    if (np.sum(first_data['WICS_MID']=='자본재')>0)&(np.sum(sector_mom['CO_NM_x']=='자본재')==1):
        data_자본재 = first_data[first_data['WICS_MID']=="자본재"]
        # per, pbr, div_yield 구할때는 전체 시가총액을 사용,
        # 시총비중 구할떄는 free-float
        data_자본재['size_FIF_wisefn']=data_자본재['size_FIF_wisefn']/1000    #size 단위 thousand
        data_자본재['1/pbr']=data_자본재['EQUITY']/data_자본재['MARKET_CAP']
        data_자본재['1/per']=data_자본재['ADJ_NI_12M_FWD']/data_자본재['MARKET_CAP']
        data_자본재['div_yield']=data_자본재['CASH_DIV_COM']/data_자본재['MARKET_CAP']
        
        # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
        data_자본재 = data_자본재.replace([np.inf, -np.inf],np.nan)  
        
        # Null 값 제거
        data_자본재_per = data_자본재[data_자본재['1/per'].notnull()]
        data_자본재_pbr = data_자본재[data_자본재['1/pbr'].notnull()]
        data_자본재_div = data_자본재[data_자본재['div_yield'].notnull()]
    
    
        # 시가총액비중 구함 
        data_자본재_pbr_cap = np.sum(data_자본재_pbr['size_FIF_wisefn'])
        data_자본재_per_cap = np.sum(data_자본재_per['size_FIF_wisefn'])
        data_자본재_div_cap = np.sum(data_자본재_div['size_FIF_wisefn'])
    
        data_자본재_pbr = data_자본재_pbr.assign(market_weight=data_자본재_pbr['size_FIF_wisefn']/data_자본재_pbr_cap)
        data_자본재_per = data_자본재_per.assign(market_weight=data_자본재_per['size_FIF_wisefn']/data_자본재_per_cap)
        data_자본재_div = data_자본재_div.assign(market_weight=data_자본재_div['size_FIF_wisefn']/data_자본재_div_cap)
        
        # 시총가중 평균 
        mu_inv_pbr=np.sum(data_자본재_pbr['1/pbr']*data_자본재_pbr['market_weight'])
        mu_inv_per=np.sum(data_자본재_per['1/per']*data_자본재_per['market_weight'])
        mu_inv_div=np.sum(data_자본재_div['div_yield']*data_자본재_div['market_weight'])
        
        # 시총 가중 표준편자
        std_inv_pbr=np.sqrt(np.sum(np.square(data_자본재_pbr['1/pbr']-mu_inv_pbr)*data_자본재_pbr['market_weight']))
        std_inv_per=np.sqrt(np.sum(np.square(data_자본재_per['1/per']-mu_inv_per)*data_자본재_per['market_weight']))
        std_inv_div=np.sqrt(np.sum(np.square(data_자본재_div['div_yield']-mu_inv_div)*data_자본재_div['market_weight']))
        
        data_자본재1=(data_자본재_pbr['1/pbr']-mu_inv_pbr)/std_inv_pbr
        data_자본재1.name= 'pbr_z'
        data_자본재2=(data_자본재_per['1/per']-mu_inv_per)/std_inv_per
        data_자본재2.name= 'per_z'
        data_자본재3=(data_자본재_div['div_yield']-mu_inv_div)/std_inv_div
        data_자본재3.name= 'div_z'
              
        result_자본재 = pd.concat([data_자본재, data_자본재1, data_자본재2, data_자본재3], axis = 1)
        
        # np.nanmean : nan 값 포함해서 평균 내기!!
        result_자본재 = result_자본재.assign(z_score=np.nanmean(result_자본재.loc[:,['pbr_z','per_z','div_z']],axis=1))
    #    result_temp = result
    
        
        # z_score > 0 인것이 가치주라고 msci에서 하고있음
        locals()['result_{}'.format(a)] =result_자본재[result_자본재['z_score'].notnull()]
        a=a+1
    
    
    #상업서비스와공급품 섹터
    if (np.sum(first_data['WICS_MID']=='상업서비스와공급품')>0)&(np.sum(sector_mom['CO_NM_x']=='상업서비스와공급품')==1):
        data_상업서비스와공급품 = first_data[first_data['WICS_MID']=='상업서비스와공급품']
        # per, pbr, div_yield 구할때는 전체 시가총액을 사용,
        # 시총비중 구할떄는 free-float
        data_상업서비스와공급품['size_FIF_wisefn']=data_상업서비스와공급품['size_FIF_wisefn']/1000    #size 단위 thousand
        data_상업서비스와공급품['1/pbr']=data_상업서비스와공급품['EQUITY']/data_상업서비스와공급품['MARKET_CAP']
        data_상업서비스와공급품['1/per']=data_상업서비스와공급품['ADJ_NI_12M_FWD']/data_상업서비스와공급품['MARKET_CAP']
        data_상업서비스와공급품['div_yield']=data_상업서비스와공급품['CASH_DIV_COM']/data_상업서비스와공급품['MARKET_CAP']
        
        # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
        data_상업서비스와공급품 = data_상업서비스와공급품.replace([np.inf, -np.inf],np.nan)  
        
        # Null 값 제거
        data_상업서비스와공급품_per = data_상업서비스와공급품[data_상업서비스와공급품['1/per'].notnull()]
        data_상업서비스와공급품_pbr = data_상업서비스와공급품[data_상업서비스와공급품['1/pbr'].notnull()]
        data_상업서비스와공급품_div = data_상업서비스와공급품[data_상업서비스와공급품['div_yield'].notnull()]
    
    
        # 시가총액비중 구함 
        data_상업서비스와공급품_pbr_cap = np.sum(data_상업서비스와공급품_pbr['size_FIF_wisefn'])
        data_상업서비스와공급품_per_cap = np.sum(data_상업서비스와공급품_per['size_FIF_wisefn'])
        data_상업서비스와공급품_div_cap = np.sum(data_상업서비스와공급품_div['size_FIF_wisefn'])
    
        data_상업서비스와공급품_pbr = data_상업서비스와공급품_pbr.assign(market_weight=data_상업서비스와공급품_pbr['size_FIF_wisefn']/data_상업서비스와공급품_pbr_cap)
        data_상업서비스와공급품_per = data_상업서비스와공급품_per.assign(market_weight=data_상업서비스와공급품_per['size_FIF_wisefn']/data_상업서비스와공급품_per_cap)
        data_상업서비스와공급품_div = data_상업서비스와공급품_div.assign(market_weight=data_상업서비스와공급품_div['size_FIF_wisefn']/data_상업서비스와공급품_div_cap)
        
        # 시총가중 평균 
        mu_inv_pbr=np.sum(data_상업서비스와공급품_pbr['1/pbr']*data_상업서비스와공급품_pbr['market_weight'])
        mu_inv_per=np.sum(data_상업서비스와공급품_per['1/per']*data_상업서비스와공급품_per['market_weight'])
        mu_inv_div=np.sum(data_상업서비스와공급품_div['div_yield']*data_상업서비스와공급품_div['market_weight'])
        
        # 시총 가중 표준편자
        std_inv_pbr=np.sqrt(np.sum(np.square(data_상업서비스와공급품_pbr['1/pbr']-mu_inv_pbr)*data_상업서비스와공급품_pbr['market_weight']))
        std_inv_per=np.sqrt(np.sum(np.square(data_상업서비스와공급품_per['1/per']-mu_inv_per)*data_상업서비스와공급품_per['market_weight']))
        std_inv_div=np.sqrt(np.sum(np.square(data_상업서비스와공급품_div['div_yield']-mu_inv_div)*data_상업서비스와공급품_div['market_weight']))
        
        data_상업서비스와공급품1=(data_상업서비스와공급품_pbr['1/pbr']-mu_inv_pbr)/std_inv_pbr
        data_상업서비스와공급품1.name= 'pbr_z'
        data_상업서비스와공급품2=(data_상업서비스와공급품_per['1/per']-mu_inv_per)/std_inv_per
        data_상업서비스와공급품2.name= 'per_z'
        data_상업서비스와공급품3=(data_상업서비스와공급품_div['div_yield']-mu_inv_div)/std_inv_div
        data_상업서비스와공급품3.name= 'div_z'
              
        result_상업서비스와공급품 = pd.concat([data_상업서비스와공급품, data_상업서비스와공급품1, data_상업서비스와공급품2, data_상업서비스와공급품3], axis = 1)
        
        # np.nanmean : nan 값 포함해서 평균 내기!!
        result_상업서비스와공급품 = result_상업서비스와공급품.assign(z_score=np.nanmean(result_상업서비스와공급품.loc[:,['pbr_z','per_z','div_z']],axis=1))
    #    result_temp = result
    
        
        # z_score > 0 인것이 가치주라고 msci에서 하고있음
        locals()['result_{}'.format(a)] =result_상업서비스와공급품[result_상업서비스와공급품['z_score'].notnull()]
        a=a+1
       #운송 섹터
    if (np.sum(first_data['WICS_MID']=='운송')>0)&(np.sum(sector_mom['CO_NM_x']=='운송')==1):
        data_운송 = first_data[first_data['WICS_MID']=='운송']
        # per, pbr, div_yield 구할때는 전체 시가총액을 사용,
        # 시총비중 구할떄는 free-float
        data_운송['size_FIF_wisefn']=data_운송['size_FIF_wisefn']/1000    #size 단위 thousand
        data_운송['1/pbr']=data_운송['EQUITY']/data_운송['MARKET_CAP']
        data_운송['1/per']=data_운송['ADJ_NI_12M_FWD']/data_운송['MARKET_CAP']
        data_운송['div_yield']=data_운송['CASH_DIV_COM']/data_운송['MARKET_CAP']
        
        # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
        data_운송 = data_운송.replace([np.inf, -np.inf],np.nan)  
        
        # Null 값 제거
        data_운송_per = data_운송[data_운송['1/per'].notnull()]
        data_운송_pbr = data_운송[data_운송['1/pbr'].notnull()]
        data_운송_div = data_운송[data_운송['div_yield'].notnull()]
    
    
        # 시가총액비중 구함 
        data_운송_pbr_cap = np.sum(data_운송_pbr['size_FIF_wisefn'])
        data_운송_per_cap = np.sum(data_운송_per['size_FIF_wisefn'])
        data_운송_div_cap = np.sum(data_운송_div['size_FIF_wisefn'])
    
        data_운송_pbr = data_운송_pbr.assign(market_weight=data_운송_pbr['size_FIF_wisefn']/data_운송_pbr_cap)
        data_운송_per = data_운송_per.assign(market_weight=data_운송_per['size_FIF_wisefn']/data_운송_per_cap)
        data_운송_div = data_운송_div.assign(market_weight=data_운송_div['size_FIF_wisefn']/data_운송_div_cap)
        
        # 시총가중 평균 
        mu_inv_pbr=np.sum(data_운송_pbr['1/pbr']*data_운송_pbr['market_weight'])
        mu_inv_per=np.sum(data_운송_per['1/per']*data_운송_per['market_weight'])
        mu_inv_div=np.sum(data_운송_div['div_yield']*data_운송_div['market_weight'])
        
        # 시총 가중 표준편자
        std_inv_pbr=np.sqrt(np.sum(np.square(data_운송_pbr['1/pbr']-mu_inv_pbr)*data_운송_pbr['market_weight']))
        std_inv_per=np.sqrt(np.sum(np.square(data_운송_per['1/per']-mu_inv_per)*data_운송_per['market_weight']))
        std_inv_div=np.sqrt(np.sum(np.square(data_운송_div['div_yield']-mu_inv_div)*data_운송_div['market_weight']))
        
        data_운송1=(data_운송_pbr['1/pbr']-mu_inv_pbr)/std_inv_pbr
        data_운송1.name= 'pbr_z'
        data_운송2=(data_운송_per['1/per']-mu_inv_per)/std_inv_per
        data_운송2.name= 'per_z'
        data_운송3=(data_운송_div['div_yield']-mu_inv_div)/std_inv_div
        data_운송3.name= 'div_z'
              
        result_운송 = pd.concat([data_운송, data_운송1, data_운송2, data_운송3], axis = 1)
        
        # np.nanmean : nan 값 포함해서 평균 내기!!
        result_운송 = result_운송.assign(z_score=np.nanmean(result_운송.loc[:,['pbr_z','per_z','div_z']],axis=1))
    #    result_temp = result
    
        
        # z_score > 0 인것이 가치주라고 msci에서 하고있음
        locals()['result_{}'.format(a)] =result_운송[result_운송['z_score'].notnull()]
        a=a+1
    #자동차와부품 섹터
    if (np.sum(first_data['WICS_MID']=='자동차와부품')>0)&(np.sum(sector_mom['CO_NM_x']=='자동차와부품')==1):
        data_자동차와부품 = first_data[first_data['WICS_MID']=='자동차와부품']
        # per, pbr, div_yield 구할때는 전체 시가총액을 사용,
        # 시총비중 구할떄는 free-float
        data_자동차와부품['size_FIF_wisefn']=data_자동차와부품['size_FIF_wisefn']/1000    #size 단위 thousand
        data_자동차와부품['1/pbr']=data_자동차와부품['EQUITY']/data_자동차와부품['MARKET_CAP']
        data_자동차와부품['1/per']=data_자동차와부품['ADJ_NI_12M_FWD']/data_자동차와부품['MARKET_CAP']
        data_자동차와부품['div_yield']=data_자동차와부품['CASH_DIV_COM']/data_자동차와부품['MARKET_CAP']
        
        # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
        data_자동차와부품 = data_자동차와부품.replace([np.inf, -np.inf],np.nan)  
        
        # Null 값 제거
        data_자동차와부품_per = data_자동차와부품[data_자동차와부품['1/per'].notnull()]
        data_자동차와부품_pbr = data_자동차와부품[data_자동차와부품['1/pbr'].notnull()]
        data_자동차와부품_div = data_자동차와부품[data_자동차와부품['div_yield'].notnull()]
    
    
        # 시가총액비중 구함 
        data_자동차와부품_pbr_cap = np.sum(data_자동차와부품_pbr['size_FIF_wisefn'])
        data_자동차와부품_per_cap = np.sum(data_자동차와부품_per['size_FIF_wisefn'])
        data_자동차와부품_div_cap = np.sum(data_자동차와부품_div['size_FIF_wisefn'])
    
        data_자동차와부품_pbr = data_자동차와부품_pbr.assign(market_weight=data_자동차와부품_pbr['size_FIF_wisefn']/data_자동차와부품_pbr_cap)
        data_자동차와부품_per = data_자동차와부품_per.assign(market_weight=data_자동차와부품_per['size_FIF_wisefn']/data_자동차와부품_per_cap)
        data_자동차와부품_div = data_자동차와부품_div.assign(market_weight=data_자동차와부품_div['size_FIF_wisefn']/data_자동차와부품_div_cap)
        
        # 시총가중 평균 
        mu_inv_pbr=np.sum(data_자동차와부품_pbr['1/pbr']*data_자동차와부품_pbr['market_weight'])
        mu_inv_per=np.sum(data_자동차와부품_per['1/per']*data_자동차와부품_per['market_weight'])
        mu_inv_div=np.sum(data_자동차와부품_div['div_yield']*data_자동차와부품_div['market_weight'])
        
        # 시총 가중 표준편자
        std_inv_pbr=np.sqrt(np.sum(np.square(data_자동차와부품_pbr['1/pbr']-mu_inv_pbr)*data_자동차와부품_pbr['market_weight']))
        std_inv_per=np.sqrt(np.sum(np.square(data_자동차와부품_per['1/per']-mu_inv_per)*data_자동차와부품_per['market_weight']))
        std_inv_div=np.sqrt(np.sum(np.square(data_자동차와부품_div['div_yield']-mu_inv_div)*data_자동차와부품_div['market_weight']))
        
        data_자동차와부품1=(data_자동차와부품_pbr['1/pbr']-mu_inv_pbr)/std_inv_pbr
        data_자동차와부품1.name= 'pbr_z'
        data_자동차와부품2=(data_자동차와부품_per['1/per']-mu_inv_per)/std_inv_per
        data_자동차와부품2.name= 'per_z'
        data_자동차와부품3=(data_자동차와부품_div['div_yield']-mu_inv_div)/std_inv_div
        data_자동차와부품3.name= 'div_z'
              
        result_자동차와부품 = pd.concat([data_자동차와부품, data_자동차와부품1, data_자동차와부품2, data_자동차와부품3], axis = 1)
        
        # np.nanmean : nan 값 포함해서 평균 내기!!
        result_자동차와부품 = result_자동차와부품.assign(z_score=np.nanmean(result_자동차와부품.loc[:,['pbr_z','per_z','div_z']],axis=1))
    #    result_temp = result
    
        
        # z_score > 0 인것이 가치주라고 msci에서 하고있음
        locals()['result_{}'.format(a)] =result_자동차와부품[result_자동차와부품['z_score'].notnull()]
        a=a+1
    #내구소비재와의류 섹터
    if (np.sum(first_data['WICS_MID']=='내구소비재와의류')>0)&(np.sum(sector_mom['CO_NM_x']=='내구소비재와의류')==1):
        data_내구소비재와의류 = first_data[first_data['WICS_MID']=='내구소비재와의류']
        # per, pbr, div_yield 구할때는 전체 시가총액을 사용,
        # 시총비중 구할떄는 free-float
        data_내구소비재와의류['size_FIF_wisefn']=data_내구소비재와의류['size_FIF_wisefn']/1000    #size 단위 thousand
        data_내구소비재와의류['1/pbr']=data_내구소비재와의류['EQUITY']/data_내구소비재와의류['MARKET_CAP']
        data_내구소비재와의류['1/per']=data_내구소비재와의류['ADJ_NI_12M_FWD']/data_내구소비재와의류['MARKET_CAP']
        data_내구소비재와의류['div_yield']=data_내구소비재와의류['CASH_DIV_COM']/data_내구소비재와의류['MARKET_CAP']
        
        # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
        data_내구소비재와의류 = data_내구소비재와의류.replace([np.inf, -np.inf],np.nan)  
        
        # Null 값 제거
        data_내구소비재와의류_per = data_내구소비재와의류[data_내구소비재와의류['1/per'].notnull()]
        data_내구소비재와의류_pbr = data_내구소비재와의류[data_내구소비재와의류['1/pbr'].notnull()]
        data_내구소비재와의류_div = data_내구소비재와의류[data_내구소비재와의류['div_yield'].notnull()]
    
    
        # 시가총액비중 구함 
        data_내구소비재와의류_pbr_cap = np.sum(data_내구소비재와의류_pbr['size_FIF_wisefn'])
        data_내구소비재와의류_per_cap = np.sum(data_내구소비재와의류_per['size_FIF_wisefn'])
        data_내구소비재와의류_div_cap = np.sum(data_내구소비재와의류_div['size_FIF_wisefn'])
    
        data_내구소비재와의류_pbr = data_내구소비재와의류_pbr.assign(market_weight=data_내구소비재와의류_pbr['size_FIF_wisefn']/data_내구소비재와의류_pbr_cap)
        data_내구소비재와의류_per = data_내구소비재와의류_per.assign(market_weight=data_내구소비재와의류_per['size_FIF_wisefn']/data_내구소비재와의류_per_cap)
        data_내구소비재와의류_div = data_내구소비재와의류_div.assign(market_weight=data_내구소비재와의류_div['size_FIF_wisefn']/data_내구소비재와의류_div_cap)
        
        # 시총가중 평균 
        mu_inv_pbr=np.sum(data_내구소비재와의류_pbr['1/pbr']*data_내구소비재와의류_pbr['market_weight'])
        mu_inv_per=np.sum(data_내구소비재와의류_per['1/per']*data_내구소비재와의류_per['market_weight'])
        mu_inv_div=np.sum(data_내구소비재와의류_div['div_yield']*data_내구소비재와의류_div['market_weight'])
        
        # 시총 가중 표준편자
        std_inv_pbr=np.sqrt(np.sum(np.square(data_내구소비재와의류_pbr['1/pbr']-mu_inv_pbr)*data_내구소비재와의류_pbr['market_weight']))
        std_inv_per=np.sqrt(np.sum(np.square(data_내구소비재와의류_per['1/per']-mu_inv_per)*data_내구소비재와의류_per['market_weight']))
        std_inv_div=np.sqrt(np.sum(np.square(data_내구소비재와의류_div['div_yield']-mu_inv_div)*data_내구소비재와의류_div['market_weight']))
        
        data_내구소비재와의류1=(data_내구소비재와의류_pbr['1/pbr']-mu_inv_pbr)/std_inv_pbr
        data_내구소비재와의류1.name= 'pbr_z'
        data_내구소비재와의류2=(data_내구소비재와의류_per['1/per']-mu_inv_per)/std_inv_per
        data_내구소비재와의류2.name= 'per_z'
        data_내구소비재와의류3=(data_내구소비재와의류_div['div_yield']-mu_inv_div)/std_inv_div
        data_내구소비재와의류3.name= 'div_z'
              
        result_내구소비재와의류 = pd.concat([data_내구소비재와의류, data_내구소비재와의류1, data_내구소비재와의류2, data_내구소비재와의류3], axis = 1)
        
        # np.nanmean : nan 값 포함해서 평균 내기!!
        result_내구소비재와의류 = result_내구소비재와의류.assign(z_score=np.nanmean(result_내구소비재와의류.loc[:,['pbr_z','per_z','div_z']],axis=1))
    #    result_temp = result
    
        
        # z_score > 0 인것이 가치주라고 msci에서 하고있음
        locals()['result_{}'.format(a)] =result_내구소비재와의류[result_내구소비재와의류['z_score'].notnull()]
        a=a+1
    

    #호텔_레스토랑_레저 섹터
    if (np.sum(first_data['WICS_MID']=='호텔_레스토랑_레저')>0)&(np.sum(sector_mom['CO_NM_x']=='호텔_레스토랑_레저')==1):
        data_호텔_레스토랑_레저 = first_data[first_data['WICS_MID']=='호텔_레스토랑_레저']
        # per, pbr, div_yield 구할때는 전체 시가총액을 사용,
        # 시총비중 구할떄는 free-float
        data_호텔_레스토랑_레저['size_FIF_wisefn']=data_호텔_레스토랑_레저['size_FIF_wisefn']/1000    #size 단위 thousand
        data_호텔_레스토랑_레저['1/pbr']=data_호텔_레스토랑_레저['EQUITY']/data_호텔_레스토랑_레저['MARKET_CAP']
        data_호텔_레스토랑_레저['1/per']=data_호텔_레스토랑_레저['ADJ_NI_12M_FWD']/data_호텔_레스토랑_레저['MARKET_CAP']
        data_호텔_레스토랑_레저['div_yield']=data_호텔_레스토랑_레저['CASH_DIV_COM']/data_호텔_레스토랑_레저['MARKET_CAP']
        
        # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
        data_호텔_레스토랑_레저 = data_호텔_레스토랑_레저.replace([np.inf, -np.inf],np.nan)  
        
        # Null 값 제거
        data_호텔_레스토랑_레저_per = data_호텔_레스토랑_레저[data_호텔_레스토랑_레저['1/per'].notnull()]
        data_호텔_레스토랑_레저_pbr = data_호텔_레스토랑_레저[data_호텔_레스토랑_레저['1/pbr'].notnull()]
        data_호텔_레스토랑_레저_div = data_호텔_레스토랑_레저[data_호텔_레스토랑_레저['div_yield'].notnull()]
    
    
        # 시가총액비중 구함 
        data_호텔_레스토랑_레저_pbr_cap = np.sum(data_호텔_레스토랑_레저_pbr['size_FIF_wisefn'])
        data_호텔_레스토랑_레저_per_cap = np.sum(data_호텔_레스토랑_레저_per['size_FIF_wisefn'])
        data_호텔_레스토랑_레저_div_cap = np.sum(data_호텔_레스토랑_레저_div['size_FIF_wisefn'])
    
        data_호텔_레스토랑_레저_pbr = data_호텔_레스토랑_레저_pbr.assign(market_weight=data_호텔_레스토랑_레저_pbr['size_FIF_wisefn']/data_호텔_레스토랑_레저_pbr_cap)
        data_호텔_레스토랑_레저_per = data_호텔_레스토랑_레저_per.assign(market_weight=data_호텔_레스토랑_레저_per['size_FIF_wisefn']/data_호텔_레스토랑_레저_per_cap)
        data_호텔_레스토랑_레저_div = data_호텔_레스토랑_레저_div.assign(market_weight=data_호텔_레스토랑_레저_div['size_FIF_wisefn']/data_호텔_레스토랑_레저_div_cap)
        
        # 시총가중 평균 
        mu_inv_pbr=np.sum(data_호텔_레스토랑_레저_pbr['1/pbr']*data_호텔_레스토랑_레저_pbr['market_weight'])
        mu_inv_per=np.sum(data_호텔_레스토랑_레저_per['1/per']*data_호텔_레스토랑_레저_per['market_weight'])
        mu_inv_div=np.sum(data_호텔_레스토랑_레저_div['div_yield']*data_호텔_레스토랑_레저_div['market_weight'])
        
        # 시총 가중 표준편자
        std_inv_pbr=np.sqrt(np.sum(np.square(data_호텔_레스토랑_레저_pbr['1/pbr']-mu_inv_pbr)*data_호텔_레스토랑_레저_pbr['market_weight']))
        std_inv_per=np.sqrt(np.sum(np.square(data_호텔_레스토랑_레저_per['1/per']-mu_inv_per)*data_호텔_레스토랑_레저_per['market_weight']))
        std_inv_div=np.sqrt(np.sum(np.square(data_호텔_레스토랑_레저_div['div_yield']-mu_inv_div)*data_호텔_레스토랑_레저_div['market_weight']))
        
        data_호텔_레스토랑_레저1=(data_호텔_레스토랑_레저_pbr['1/pbr']-mu_inv_pbr)/std_inv_pbr
        data_호텔_레스토랑_레저1.name= 'pbr_z'
        data_호텔_레스토랑_레저2=(data_호텔_레스토랑_레저_per['1/per']-mu_inv_per)/std_inv_per
        data_호텔_레스토랑_레저2.name= 'per_z'
        data_호텔_레스토랑_레저3=(data_호텔_레스토랑_레저_div['div_yield']-mu_inv_div)/std_inv_div
        data_호텔_레스토랑_레저3.name= 'div_z'
              
        result_호텔_레스토랑_레저 = pd.concat([data_호텔_레스토랑_레저, data_호텔_레스토랑_레저1, data_호텔_레스토랑_레저2, data_호텔_레스토랑_레저3], axis = 1)
        
        # np.nanmean : nan 값 포함해서 평균 내기!!
        result_호텔_레스토랑_레저 = result_호텔_레스토랑_레저.assign(z_score=np.nanmean(result_호텔_레스토랑_레저.loc[:,['pbr_z','per_z','div_z']],axis=1))
    #    result_temp = result
    
        
        # z_score > 0 인것이 가치주라고 msci에서 하고있음
        locals()['result_{}'.format(a)] =result_호텔_레스토랑_레저[result_호텔_레스토랑_레저['z_score'].notnull()]
        a=a+1
    #미디어 섹터
    if (np.sum(first_data['WICS_MID']=='미디어')>0)&(np.sum(sector_mom['CO_NM_x']=='미디어')==1):
        data_미디어 = first_data[first_data['WICS_MID']=='미디어']
        # per, pbr, div_yield 구할때는 전체 시가총액을 사용,
        # 시총비중 구할떄는 free-float
        data_미디어['size_FIF_wisefn']=data_미디어['size_FIF_wisefn']/1000    #size 단위 thousand
        data_미디어['1/pbr']=data_미디어['EQUITY']/data_미디어['MARKET_CAP']
        data_미디어['1/per']=data_미디어['ADJ_NI_12M_FWD']/data_미디어['MARKET_CAP']
        data_미디어['div_yield']=data_미디어['CASH_DIV_COM']/data_미디어['MARKET_CAP']
        
        # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
        data_미디어 = data_미디어.replace([np.inf, -np.inf],np.nan)  
        
        # Null 값 제거
        data_미디어_per = data_미디어[data_미디어['1/per'].notnull()]
        data_미디어_pbr = data_미디어[data_미디어['1/pbr'].notnull()]
        data_미디어_div = data_미디어[data_미디어['div_yield'].notnull()]
    
    
        # 시가총액비중 구함 
        data_미디어_pbr_cap = np.sum(data_미디어_pbr['size_FIF_wisefn'])
        data_미디어_per_cap = np.sum(data_미디어_per['size_FIF_wisefn'])
        data_미디어_div_cap = np.sum(data_미디어_div['size_FIF_wisefn'])
    
        data_미디어_pbr = data_미디어_pbr.assign(market_weight=data_미디어_pbr['size_FIF_wisefn']/data_미디어_pbr_cap)
        data_미디어_per = data_미디어_per.assign(market_weight=data_미디어_per['size_FIF_wisefn']/data_미디어_per_cap)
        data_미디어_div = data_미디어_div.assign(market_weight=data_미디어_div['size_FIF_wisefn']/data_미디어_div_cap)
        
        # 시총가중 평균 
        mu_inv_pbr=np.sum(data_미디어_pbr['1/pbr']*data_미디어_pbr['market_weight'])
        mu_inv_per=np.sum(data_미디어_per['1/per']*data_미디어_per['market_weight'])
        mu_inv_div=np.sum(data_미디어_div['div_yield']*data_미디어_div['market_weight'])
        
        # 시총 가중 표준편자
        std_inv_pbr=np.sqrt(np.sum(np.square(data_미디어_pbr['1/pbr']-mu_inv_pbr)*data_미디어_pbr['market_weight']))
        std_inv_per=np.sqrt(np.sum(np.square(data_미디어_per['1/per']-mu_inv_per)*data_미디어_per['market_weight']))
        std_inv_div=np.sqrt(np.sum(np.square(data_미디어_div['div_yield']-mu_inv_div)*data_미디어_div['market_weight']))
        
        data_미디어1=(data_미디어_pbr['1/pbr']-mu_inv_pbr)/std_inv_pbr
        data_미디어1.name= 'pbr_z'
        data_미디어2=(data_미디어_per['1/per']-mu_inv_per)/std_inv_per
        data_미디어2.name= 'per_z'
        data_미디어3=(data_미디어_div['div_yield']-mu_inv_div)/std_inv_div
        data_미디어3.name= 'div_z'
              
        result_미디어 = pd.concat([data_미디어, data_미디어1, data_미디어2, data_미디어3], axis = 1)
        
        # np.nanmean : nan 값 포함해서 평균 내기!!
        result_미디어 = result_미디어.assign(z_score=np.nanmean(result_미디어.loc[:,['pbr_z','per_z','div_z']],axis=1))
    #    result_temp = result
    
        
        # z_score > 0 인것이 가치주라고 msci에서 하고있음
        locals()['result_{}'.format(a)] =result_미디어[result_미디어['z_score'].notnull()]
        a=a+1
    #소매(유통) 섹터
    if (np.sum(first_data['WICS_MID']=='소매(유통)')>0)&(np.sum(sector_mom['CO_NM_x']=='소매(유통)')==1):
        data_소매_유통 = first_data[first_data['WICS_MID']=='소매(유통)']
        # per, pbr, div_yield 구할때는 전체 시가총액을 사용,
        # 시총비중 구할떄는 free-float
        data_소매_유통['size_FIF_wisefn']=data_소매_유통['size_FIF_wisefn']/1000    #size 단위 thousand
        data_소매_유통['1/pbr']=data_소매_유통['EQUITY']/data_소매_유통['MARKET_CAP']
        data_소매_유통['1/per']=data_소매_유통['ADJ_NI_12M_FWD']/data_소매_유통['MARKET_CAP']
        data_소매_유통['div_yield']=data_소매_유통['CASH_DIV_COM']/data_소매_유통['MARKET_CAP']
        
        # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
        data_소매_유통 = data_소매_유통.replace([np.inf, -np.inf],np.nan)  
        
        # Null 값 제거
        data_소매_유통_per = data_소매_유통[data_소매_유통['1/per'].notnull()]
        data_소매_유통_pbr = data_소매_유통[data_소매_유통['1/pbr'].notnull()]
        data_소매_유통_div = data_소매_유통[data_소매_유통['div_yield'].notnull()]
    
    
        # 시가총액비중 구함 
        data_소매_유통_pbr_cap = np.sum(data_소매_유통_pbr['size_FIF_wisefn'])
        data_소매_유통_per_cap = np.sum(data_소매_유통_per['size_FIF_wisefn'])
        data_소매_유통_div_cap = np.sum(data_소매_유통_div['size_FIF_wisefn'])
    
        data_소매_유통_pbr = data_소매_유통_pbr.assign(market_weight=data_소매_유통_pbr['size_FIF_wisefn']/data_소매_유통_pbr_cap)
        data_소매_유통_per = data_소매_유통_per.assign(market_weight=data_소매_유통_per['size_FIF_wisefn']/data_소매_유통_per_cap)
        data_소매_유통_div = data_소매_유통_div.assign(market_weight=data_소매_유통_div['size_FIF_wisefn']/data_소매_유통_div_cap)
        
        # 시총가중 평균 
        mu_inv_pbr=np.sum(data_소매_유통_pbr['1/pbr']*data_소매_유통_pbr['market_weight'])
        mu_inv_per=np.sum(data_소매_유통_per['1/per']*data_소매_유통_per['market_weight'])
        mu_inv_div=np.sum(data_소매_유통_div['div_yield']*data_소매_유통_div['market_weight'])
        
        # 시총 가중 표준편자
        std_inv_pbr=np.sqrt(np.sum(np.square(data_소매_유통_pbr['1/pbr']-mu_inv_pbr)*data_소매_유통_pbr['market_weight']))
        std_inv_per=np.sqrt(np.sum(np.square(data_소매_유통_per['1/per']-mu_inv_per)*data_소매_유통_per['market_weight']))
        std_inv_div=np.sqrt(np.sum(np.square(data_소매_유통_div['div_yield']-mu_inv_div)*data_소매_유통_div['market_weight']))
        
        data_소매_유통1=(data_소매_유통_pbr['1/pbr']-mu_inv_pbr)/std_inv_pbr
        data_소매_유통1.name= 'pbr_z'
        data_소매_유통2=(data_소매_유통_per['1/per']-mu_inv_per)/std_inv_per
        data_소매_유통2.name= 'per_z'
        data_소매_유통3=(data_소매_유통_div['div_yield']-mu_inv_div)/std_inv_div
        data_소매_유통3.name= 'div_z'
              
        result_소매_유통 = pd.concat([data_소매_유통, data_소매_유통1, data_소매_유통2, data_소매_유통3], axis = 1)
        
        # np.nanmean : nan 값 포함해서 평균 내기!!
        result_소매_유통 = result_소매_유통.assign(z_score=np.nanmean(result_소매_유통.loc[:,['pbr_z','per_z','div_z']],axis=1))
    #    result_temp = result
    
        
        # z_score > 0 인것이 가치주라고 msci에서 하고있음
        locals()['result_{}'.format(a)] =result_소매_유통[result_소매_유통['z_score'].notnull()]
        a=a+1
        
     #교육서비스 섹터
    if (np.sum(first_data['WICS_MID']=='교육서비스')>0)&(np.sum(sector_mom['CO_NM_x']=='교육서비스')==1):
        data_교육서비스 = first_data[first_data['WICS_MID']=="교육서비스"]
        # per, pbr, div_yield 구할때는 전체 시가총액을 사용,
        # 시총비중 구할떄는 free-float
        data_교육서비스['size_FIF_wisefn']=data_교육서비스['size_FIF_wisefn']/1000    #size 단위 thousand
        data_교육서비스['1/pbr']=data_교육서비스['EQUITY']/data_교육서비스['MARKET_CAP']
        data_교육서비스['1/per']=data_교육서비스['ADJ_NI_12M_FWD']/data_교육서비스['MARKET_CAP']
        data_교육서비스['div_yield']=data_교육서비스['CASH_DIV_COM']/data_교육서비스['MARKET_CAP']
        
        # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
        data_교육서비스 = data_교육서비스.replace([np.inf, -np.inf],np.nan)  
        
        # Null 값 제거
        data_교육서비스_per = data_교육서비스[data_교육서비스['1/per'].notnull()]
        data_교육서비스_pbr = data_교육서비스[data_교육서비스['1/pbr'].notnull()]
        data_교육서비스_div = data_교육서비스[data_교육서비스['div_yield'].notnull()]
    
    
        # 시가총액비중 구함 
        data_교육서비스_pbr_cap = np.sum(data_교육서비스_pbr['size_FIF_wisefn'])
        data_교육서비스_per_cap = np.sum(data_교육서비스_per['size_FIF_wisefn'])
        data_교육서비스_div_cap = np.sum(data_교육서비스_div['size_FIF_wisefn'])
    
        data_교육서비스_pbr = data_교육서비스_pbr.assign(market_weight=data_교육서비스_pbr['size_FIF_wisefn']/data_교육서비스_pbr_cap)
        data_교육서비스_per = data_교육서비스_per.assign(market_weight=data_교육서비스_per['size_FIF_wisefn']/data_교육서비스_per_cap)
        data_교육서비스_div = data_교육서비스_div.assign(market_weight=data_교육서비스_div['size_FIF_wisefn']/data_교육서비스_div_cap)
        
        # 시총가중 평균 
        mu_inv_pbr=np.sum(data_교육서비스_pbr['1/pbr']*data_교육서비스_pbr['market_weight'])
        mu_inv_per=np.sum(data_교육서비스_per['1/per']*data_교육서비스_per['market_weight'])
        mu_inv_div=np.sum(data_교육서비스_div['div_yield']*data_교육서비스_div['market_weight'])
        
        # 시총 가중 표준편자
        std_inv_pbr=np.sqrt(np.sum(np.square(data_교육서비스_pbr['1/pbr']-mu_inv_pbr)*data_교육서비스_pbr['market_weight']))
        std_inv_per=np.sqrt(np.sum(np.square(data_교육서비스_per['1/per']-mu_inv_per)*data_교육서비스_per['market_weight']))
        std_inv_div=np.sqrt(np.sum(np.square(data_교육서비스_div['div_yield']-mu_inv_div)*data_교육서비스_div['market_weight']))
        
        data_교육서비스1=(data_교육서비스_pbr['1/pbr']-mu_inv_pbr)/std_inv_pbr
        data_교육서비스1.name= 'pbr_z'
        data_교육서비스2=(data_교육서비스_per['1/per']-mu_inv_per)/std_inv_per
        data_교육서비스2.name= 'per_z'
        data_교육서비스3=(data_교육서비스_div['div_yield']-mu_inv_div)/std_inv_div
        data_교육서비스3.name= 'div_z'
              
        result_교육서비스 = pd.concat([data_교육서비스, data_교육서비스1, data_교육서비스2, data_교육서비스3], axis = 1)
        
        # np.nanmean : nan 값 포함해서 평균 내기!!
        result_교육서비스 = result_교육서비스.assign(z_score=np.nanmean(result_교육서비스.loc[:,['pbr_z','per_z','div_z']],axis=1))
    #    result_temp = result
    
        
        # z_score > 0 인것이 가치주라고 msci에서 하고있음
        locals()['result_{}'.format(a)] =result_교육서비스[result_교육서비스['z_score'].notnull()]
        a=a+1
    
     #식품과기본식료품소매 섹터
    if (np.sum(first_data['WICS_MID']=='식품과기본식료품소매')>0)&(np.sum(sector_mom['CO_NM_x']=='식품과기본식료품소매')==1):
        data_식품과기본식료품소매 = first_data[first_data['WICS_MID']=="식품과기본식료품소매"]
        # per, pbr, div_yield 구할때는 전체 시가총액을 사용,
        # 시총비중 구할떄는 free-float
        data_식품과기본식료품소매['size_FIF_wisefn']=data_식품과기본식료품소매['size_FIF_wisefn']/1000    #size 단위 thousand
        data_식품과기본식료품소매['1/pbr']=data_식품과기본식료품소매['EQUITY']/data_식품과기본식료품소매['MARKET_CAP']
        data_식품과기본식료품소매['1/per']=data_식품과기본식료품소매['ADJ_NI_12M_FWD']/data_식품과기본식료품소매['MARKET_CAP']
        data_식품과기본식료품소매['div_yield']=data_식품과기본식료품소매['CASH_DIV_COM']/data_식품과기본식료품소매['MARKET_CAP']
        
        # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
        data_식품과기본식료품소매 = data_식품과기본식료품소매.replace([np.inf, -np.inf],np.nan)  
        
        # Null 값 제거
        data_식품과기본식료품소매_per = data_식품과기본식료품소매[data_식품과기본식료품소매['1/per'].notnull()]
        data_식품과기본식료품소매_pbr = data_식품과기본식료품소매[data_식품과기본식료품소매['1/pbr'].notnull()]
        data_식품과기본식료품소매_div = data_식품과기본식료품소매[data_식품과기본식료품소매['div_yield'].notnull()]
    
    
        # 시가총액비중 구함 
        data_식품과기본식료품소매_pbr_cap = np.sum(data_식품과기본식료품소매_pbr['size_FIF_wisefn'])
        data_식품과기본식료품소매_per_cap = np.sum(data_식품과기본식료품소매_per['size_FIF_wisefn'])
        data_식품과기본식료품소매_div_cap = np.sum(data_식품과기본식료품소매_div['size_FIF_wisefn'])
    
        data_식품과기본식료품소매_pbr = data_식품과기본식료품소매_pbr.assign(market_weight=data_식품과기본식료품소매_pbr['size_FIF_wisefn']/data_식품과기본식료품소매_pbr_cap)
        data_식품과기본식료품소매_per = data_식품과기본식료품소매_per.assign(market_weight=data_식품과기본식료품소매_per['size_FIF_wisefn']/data_식품과기본식료품소매_per_cap)
        data_식품과기본식료품소매_div = data_식품과기본식료품소매_div.assign(market_weight=data_식품과기본식료품소매_div['size_FIF_wisefn']/data_식품과기본식료품소매_div_cap)
        
        # 시총가중 평균 
        mu_inv_pbr=np.sum(data_식품과기본식료품소매_pbr['1/pbr']*data_식품과기본식료품소매_pbr['market_weight'])
        mu_inv_per=np.sum(data_식품과기본식료품소매_per['1/per']*data_식품과기본식료품소매_per['market_weight'])
        mu_inv_div=np.sum(data_식품과기본식료품소매_div['div_yield']*data_식품과기본식료품소매_div['market_weight'])
        
        # 시총 가중 표준편자
        std_inv_pbr=np.sqrt(np.sum(np.square(data_식품과기본식료품소매_pbr['1/pbr']-mu_inv_pbr)*data_식품과기본식료품소매_pbr['market_weight']))
        std_inv_per=np.sqrt(np.sum(np.square(data_식품과기본식료품소매_per['1/per']-mu_inv_per)*data_식품과기본식료품소매_per['market_weight']))
        std_inv_div=np.sqrt(np.sum(np.square(data_식품과기본식료품소매_div['div_yield']-mu_inv_div)*data_식품과기본식료품소매_div['market_weight']))
        
        data_식품과기본식료품소매1=(data_식품과기본식료품소매_pbr['1/pbr']-mu_inv_pbr)/std_inv_pbr
        data_식품과기본식료품소매1.name= 'pbr_z'
        data_식품과기본식료품소매2=(data_식품과기본식료품소매_per['1/per']-mu_inv_per)/std_inv_per
        data_식품과기본식료품소매2.name= 'per_z'
        data_식품과기본식료품소매3=(data_식품과기본식료품소매_div['div_yield']-mu_inv_div)/std_inv_div
        data_식품과기본식료품소매3.name= 'div_z'
              
        result_식품과기본식료품소매 = pd.concat([data_식품과기본식료품소매, data_식품과기본식료품소매1, data_식품과기본식료품소매2, data_식품과기본식료품소매3], axis = 1)
        
        # np.nanmean : nan 값 포함해서 평균 내기!!
        result_식품과기본식료품소매 = result_식품과기본식료품소매.assign(z_score=np.nanmean(result_식품과기본식료품소매.loc[:,['pbr_z','per_z','div_z']],axis=1))
    #    result_temp = result
    
        
        # z_score > 0 인것이 가치주라고 msci에서 하고있음
        locals()['result_{}'.format(a)] =result_식품과기본식료품소매[result_식품과기본식료품소매['z_score'].notnull()]
        a=a+1
    
     #식품,음료,담배 섹터
    if (np.sum(first_data['WICS_MID']=='식품_음료_담배')>0)&(np.sum(sector_mom['CO_NM_x']=='식품_음료_담배')==1):
        data_식품_음료_담배 = first_data[first_data['WICS_MID']=="식품_음료_담배"]
        # per, pbr, div_yield 구할때는 전체 시가총액을 사용,
        # 시총비중 구할떄는 free-float
        data_식품_음료_담배['size_FIF_wisefn']=data_식품_음료_담배['size_FIF_wisefn']/1000    #size 단위 thousand
        data_식품_음료_담배['1/pbr']=data_식품_음료_담배['EQUITY']/data_식품_음료_담배['MARKET_CAP']
        data_식품_음료_담배['1/per']=data_식품_음료_담배['ADJ_NI_12M_FWD']/data_식품_음료_담배['MARKET_CAP']
        data_식품_음료_담배['div_yield']=data_식품_음료_담배['CASH_DIV_COM']/data_식품_음료_담배['MARKET_CAP']
        
        # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
        data_식품_음료_담배 = data_식품_음료_담배.replace([np.inf, -np.inf],np.nan)  
        
        # Null 값 제거
        data_식품_음료_담배_per = data_식품_음료_담배[data_식품_음료_담배['1/per'].notnull()]
        data_식품_음료_담배_pbr = data_식품_음료_담배[data_식품_음료_담배['1/pbr'].notnull()]
        data_식품_음료_담배_div = data_식품_음료_담배[data_식품_음료_담배['div_yield'].notnull()]
    
    
        # 시가총액비중 구함 
        data_식품_음료_담배_pbr_cap = np.sum(data_식품_음료_담배_pbr['size_FIF_wisefn'])
        data_식품_음료_담배_per_cap = np.sum(data_식품_음료_담배_per['size_FIF_wisefn'])
        data_식품_음료_담배_div_cap = np.sum(data_식품_음료_담배_div['size_FIF_wisefn'])
    
        data_식품_음료_담배_pbr = data_식품_음료_담배_pbr.assign(market_weight=data_식품_음료_담배_pbr['size_FIF_wisefn']/data_식품_음료_담배_pbr_cap)
        data_식품_음료_담배_per = data_식품_음료_담배_per.assign(market_weight=data_식품_음료_담배_per['size_FIF_wisefn']/data_식품_음료_담배_per_cap)
        data_식품_음료_담배_div = data_식품_음료_담배_div.assign(market_weight=data_식품_음료_담배_div['size_FIF_wisefn']/data_식품_음료_담배_div_cap)
        
        # 시총가중 평균 
        mu_inv_pbr=np.sum(data_식품_음료_담배_pbr['1/pbr']*data_식품_음료_담배_pbr['market_weight'])
        mu_inv_per=np.sum(data_식품_음료_담배_per['1/per']*data_식품_음료_담배_per['market_weight'])
        mu_inv_div=np.sum(data_식품_음료_담배_div['div_yield']*data_식품_음료_담배_div['market_weight'])
        
        # 시총 가중 표준편자
        std_inv_pbr=np.sqrt(np.sum(np.square(data_식품_음료_담배_pbr['1/pbr']-mu_inv_pbr)*data_식품_음료_담배_pbr['market_weight']))
        std_inv_per=np.sqrt(np.sum(np.square(data_식품_음료_담배_per['1/per']-mu_inv_per)*data_식품_음료_담배_per['market_weight']))
        std_inv_div=np.sqrt(np.sum(np.square(data_식품_음료_담배_div['div_yield']-mu_inv_div)*data_식품_음료_담배_div['market_weight']))
        
        data_식품_음료_담배1=(data_식품_음료_담배_pbr['1/pbr']-mu_inv_pbr)/std_inv_pbr
        data_식품_음료_담배1.name= 'pbr_z'
        data_식품_음료_담배2=(data_식품_음료_담배_per['1/per']-mu_inv_per)/std_inv_per
        data_식품_음료_담배2.name= 'per_z'
        data_식품_음료_담배3=(data_식품_음료_담배_div['div_yield']-mu_inv_div)/std_inv_div
        data_식품_음료_담배3.name= 'div_z'
              
        result_식품_음료_담배 = pd.concat([data_식품_음료_담배, data_식품_음료_담배1, data_식품_음료_담배2, data_식품_음료_담배3], axis = 1)
        
        # np.nanmean : nan 값 포함해서 평균 내기!!
        result_식품_음료_담배 = result_식품_음료_담배.assign(z_score=np.nanmean(result_식품_음료_담배.loc[:,['pbr_z','per_z','div_z']],axis=1))
    #    result_temp = result
    
        
        # z_score > 0 인것이 가치주라고 msci에서 하고있음
        locals()['result_{}'.format(a)] =result_식품_음료_담배[result_식품_음료_담배['z_score'].notnull()]
        a=a+1
    
     #가정용품과개인용품 섹터
    if (np.sum(first_data['WICS_MID']=='가정용품과개인용품')>0)&(np.sum(sector_mom['CO_NM_x']=='가정용품과개인용품')==1):
        data_가정용품과개인용품 = first_data[first_data['WICS_MID']=="가정용품과개인용품"]
        # per, pbr, div_yield 구할때는 전체 시가총액을 사용,
        # 시총비중 구할떄는 free-float
        data_가정용품과개인용품['size_FIF_wisefn']=data_가정용품과개인용품['size_FIF_wisefn']/1000    #size 단위 thousand
        data_가정용품과개인용품['1/pbr']=data_가정용품과개인용품['EQUITY']/data_가정용품과개인용품['MARKET_CAP']
        data_가정용품과개인용품['1/per']=data_가정용품과개인용품['ADJ_NI_12M_FWD']/data_가정용품과개인용품['MARKET_CAP']
        data_가정용품과개인용품['div_yield']=data_가정용품과개인용품['CASH_DIV_COM']/data_가정용품과개인용품['MARKET_CAP']
        
        # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
        data_가정용품과개인용품 = data_가정용품과개인용품.replace([np.inf, -np.inf],np.nan)  
        
        # Null 값 제거
        data_가정용품과개인용품_per = data_가정용품과개인용품[data_가정용품과개인용품['1/per'].notnull()]
        data_가정용품과개인용품_pbr = data_가정용품과개인용품[data_가정용품과개인용품['1/pbr'].notnull()]
        data_가정용품과개인용품_div = data_가정용품과개인용품[data_가정용품과개인용품['div_yield'].notnull()]
    
    
        # 시가총액비중 구함 
        data_가정용품과개인용품_pbr_cap = np.sum(data_가정용품과개인용품_pbr['size_FIF_wisefn'])
        data_가정용품과개인용품_per_cap = np.sum(data_가정용품과개인용품_per['size_FIF_wisefn'])
        data_가정용품과개인용품_div_cap = np.sum(data_가정용품과개인용품_div['size_FIF_wisefn'])
    
        data_가정용품과개인용품_pbr = data_가정용품과개인용품_pbr.assign(market_weight=data_가정용품과개인용품_pbr['size_FIF_wisefn']/data_가정용품과개인용품_pbr_cap)
        data_가정용품과개인용품_per = data_가정용품과개인용품_per.assign(market_weight=data_가정용품과개인용품_per['size_FIF_wisefn']/data_가정용품과개인용품_per_cap)
        data_가정용품과개인용품_div = data_가정용품과개인용품_div.assign(market_weight=data_가정용품과개인용품_div['size_FIF_wisefn']/data_가정용품과개인용품_div_cap)
        
        # 시총가중 평균 
        mu_inv_pbr=np.sum(data_가정용품과개인용품_pbr['1/pbr']*data_가정용품과개인용품_pbr['market_weight'])
        mu_inv_per=np.sum(data_가정용품과개인용품_per['1/per']*data_가정용품과개인용품_per['market_weight'])
        mu_inv_div=np.sum(data_가정용품과개인용품_div['div_yield']*data_가정용품과개인용품_div['market_weight'])
        
        # 시총 가중 표준편자
        std_inv_pbr=np.sqrt(np.sum(np.square(data_가정용품과개인용품_pbr['1/pbr']-mu_inv_pbr)*data_가정용품과개인용품_pbr['market_weight']))
        std_inv_per=np.sqrt(np.sum(np.square(data_가정용품과개인용품_per['1/per']-mu_inv_per)*data_가정용품과개인용품_per['market_weight']))
        std_inv_div=np.sqrt(np.sum(np.square(data_가정용품과개인용품_div['div_yield']-mu_inv_div)*data_가정용품과개인용품_div['market_weight']))
        
        data_가정용품과개인용품1=(data_가정용품과개인용품_pbr['1/pbr']-mu_inv_pbr)/std_inv_pbr
        data_가정용품과개인용품1.name= 'pbr_z'
        data_가정용품과개인용품2=(data_가정용품과개인용품_per['1/per']-mu_inv_per)/std_inv_per
        data_가정용품과개인용품2.name= 'per_z'
        data_가정용품과개인용품3=(data_가정용품과개인용품_div['div_yield']-mu_inv_div)/std_inv_div
        data_가정용품과개인용품3.name= 'div_z'
              
        result_가정용품과개인용품 = pd.concat([data_가정용품과개인용품, data_가정용품과개인용품1, data_가정용품과개인용품2, data_가정용품과개인용품3], axis = 1)
        
        # np.nanmean : nan 값 포함해서 평균 내기!!
        result_가정용품과개인용품 = result_가정용품과개인용품.assign(z_score=np.nanmean(result_가정용품과개인용품.loc[:,['pbr_z','per_z','div_z']],axis=1))
    #    result_temp = result
    
        
        # z_score > 0 인것이 가치주라고 msci에서 하고있음
        locals()['result_{}'.format(a)] =result_가정용품과개인용품[result_가정용품과개인용품['z_score'].notnull()]
        a=a+1
    
     #건강관리장비와서비스 섹터
    if (np.sum(first_data['WICS_MID']=='건강관리장비와서비스')>0)&(np.sum(sector_mom['CO_NM_x']=='건강관리장비와서비스')==1):
        data_건강관리장비와서비스 = first_data[first_data['WICS_MID']=="건강관리장비와서비스"]
        # per, pbr, div_yield 구할때는 전체 시가총액을 사용,
        # 시총비중 구할떄는 free-float
        data_건강관리장비와서비스['size_FIF_wisefn']=data_건강관리장비와서비스['size_FIF_wisefn']/1000    #size 단위 thousand
        data_건강관리장비와서비스['1/pbr']=data_건강관리장비와서비스['EQUITY']/data_건강관리장비와서비스['MARKET_CAP']
        data_건강관리장비와서비스['1/per']=data_건강관리장비와서비스['ADJ_NI_12M_FWD']/data_건강관리장비와서비스['MARKET_CAP']
        data_건강관리장비와서비스['div_yield']=data_건강관리장비와서비스['CASH_DIV_COM']/data_건강관리장비와서비스['MARKET_CAP']
        
        # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
        data_건강관리장비와서비스 = data_건강관리장비와서비스.replace([np.inf, -np.inf],np.nan)  
        
        # Null 값 제거
        data_건강관리장비와서비스_per = data_건강관리장비와서비스[data_건강관리장비와서비스['1/per'].notnull()]
        data_건강관리장비와서비스_pbr = data_건강관리장비와서비스[data_건강관리장비와서비스['1/pbr'].notnull()]
        data_건강관리장비와서비스_div = data_건강관리장비와서비스[data_건강관리장비와서비스['div_yield'].notnull()]
    
    
        # 시가총액비중 구함 
        data_건강관리장비와서비스_pbr_cap = np.sum(data_건강관리장비와서비스_pbr['size_FIF_wisefn'])
        data_건강관리장비와서비스_per_cap = np.sum(data_건강관리장비와서비스_per['size_FIF_wisefn'])
        data_건강관리장비와서비스_div_cap = np.sum(data_건강관리장비와서비스_div['size_FIF_wisefn'])
    
        data_건강관리장비와서비스_pbr = data_건강관리장비와서비스_pbr.assign(market_weight=data_건강관리장비와서비스_pbr['size_FIF_wisefn']/data_건강관리장비와서비스_pbr_cap)
        data_건강관리장비와서비스_per = data_건강관리장비와서비스_per.assign(market_weight=data_건강관리장비와서비스_per['size_FIF_wisefn']/data_건강관리장비와서비스_per_cap)
        data_건강관리장비와서비스_div = data_건강관리장비와서비스_div.assign(market_weight=data_건강관리장비와서비스_div['size_FIF_wisefn']/data_건강관리장비와서비스_div_cap)
        
        # 시총가중 평균 
        mu_inv_pbr=np.sum(data_건강관리장비와서비스_pbr['1/pbr']*data_건강관리장비와서비스_pbr['market_weight'])
        mu_inv_per=np.sum(data_건강관리장비와서비스_per['1/per']*data_건강관리장비와서비스_per['market_weight'])
        mu_inv_div=np.sum(data_건강관리장비와서비스_div['div_yield']*data_건강관리장비와서비스_div['market_weight'])
        
        # 시총 가중 표준편자
        std_inv_pbr=np.sqrt(np.sum(np.square(data_건강관리장비와서비스_pbr['1/pbr']-mu_inv_pbr)*data_건강관리장비와서비스_pbr['market_weight']))
        std_inv_per=np.sqrt(np.sum(np.square(data_건강관리장비와서비스_per['1/per']-mu_inv_per)*data_건강관리장비와서비스_per['market_weight']))
        std_inv_div=np.sqrt(np.sum(np.square(data_건강관리장비와서비스_div['div_yield']-mu_inv_div)*data_건강관리장비와서비스_div['market_weight']))
        
        data_건강관리장비와서비스1=(data_건강관리장비와서비스_pbr['1/pbr']-mu_inv_pbr)/std_inv_pbr
        data_건강관리장비와서비스1.name= 'pbr_z'
        data_건강관리장비와서비스2=(data_건강관리장비와서비스_per['1/per']-mu_inv_per)/std_inv_per
        data_건강관리장비와서비스2.name= 'per_z'
        data_건강관리장비와서비스3=(data_건강관리장비와서비스_div['div_yield']-mu_inv_div)/std_inv_div
        data_건강관리장비와서비스3.name= 'div_z'
              
        result_건강관리장비와서비스 = pd.concat([data_건강관리장비와서비스, data_건강관리장비와서비스1, data_건강관리장비와서비스2, data_건강관리장비와서비스3], axis = 1)
        
        # np.nanmean : nan 값 포함해서 평균 내기!!
        result_건강관리장비와서비스 = result_건강관리장비와서비스.assign(z_score=np.nanmean(result_건강관리장비와서비스.loc[:,['pbr_z','per_z','div_z']],axis=1))
    #    result_temp = result
    
        
        # z_score > 0 인것이 가치주라고 msci에서 하고있음
        locals()['result_{}'.format(a)] =result_건강관리장비와서비스[result_건강관리장비와서비스['z_score'].notnull()]
        a=a+1
    
     #제약과생물공학 섹터
    if (np.sum(first_data['WICS_MID']=='제약과생물공학')>0)&(np.sum(sector_mom['CO_NM_x']=='제약과생물공학')==1):
        data_제약과생물공학 = first_data[first_data['WICS_MID']=="제약과생물공학"]
        # per, pbr, div_yield 구할때는 전체 시가총액을 사용,
        # 시총비중 구할떄는 free-float
        data_제약과생물공학['size_FIF_wisefn']=data_제약과생물공학['size_FIF_wisefn']/1000    #size 단위 thousand
        data_제약과생물공학['1/pbr']=data_제약과생물공학['EQUITY']/data_제약과생물공학['MARKET_CAP']
        data_제약과생물공학['1/per']=data_제약과생물공학['ADJ_NI_12M_FWD']/data_제약과생물공학['MARKET_CAP']
        data_제약과생물공학['div_yield']=data_제약과생물공학['CASH_DIV_COM']/data_제약과생물공학['MARKET_CAP']
        
        # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
        data_제약과생물공학 = data_제약과생물공학.replace([np.inf, -np.inf],np.nan)  
        
        # Null 값 제거
        data_제약과생물공학_per = data_제약과생물공학[data_제약과생물공학['1/per'].notnull()]
        data_제약과생물공학_pbr = data_제약과생물공학[data_제약과생물공학['1/pbr'].notnull()]
        data_제약과생물공학_div = data_제약과생물공학[data_제약과생물공학['div_yield'].notnull()]
    
    
        # 시가총액비중 구함 
        data_제약과생물공학_pbr_cap = np.sum(data_제약과생물공학_pbr['size_FIF_wisefn'])
        data_제약과생물공학_per_cap = np.sum(data_제약과생물공학_per['size_FIF_wisefn'])
        data_제약과생물공학_div_cap = np.sum(data_제약과생물공학_div['size_FIF_wisefn'])
    
        data_제약과생물공학_pbr = data_제약과생물공학_pbr.assign(market_weight=data_제약과생물공학_pbr['size_FIF_wisefn']/data_제약과생물공학_pbr_cap)
        data_제약과생물공학_per = data_제약과생물공학_per.assign(market_weight=data_제약과생물공학_per['size_FIF_wisefn']/data_제약과생물공학_per_cap)
        data_제약과생물공학_div = data_제약과생물공학_div.assign(market_weight=data_제약과생물공학_div['size_FIF_wisefn']/data_제약과생물공학_div_cap)
        
        # 시총가중 평균 
        mu_inv_pbr=np.sum(data_제약과생물공학_pbr['1/pbr']*data_제약과생물공학_pbr['market_weight'])
        mu_inv_per=np.sum(data_제약과생물공학_per['1/per']*data_제약과생물공학_per['market_weight'])
        mu_inv_div=np.sum(data_제약과생물공학_div['div_yield']*data_제약과생물공학_div['market_weight'])
        
        # 시총 가중 표준편자
        std_inv_pbr=np.sqrt(np.sum(np.square(data_제약과생물공학_pbr['1/pbr']-mu_inv_pbr)*data_제약과생물공학_pbr['market_weight']))
        std_inv_per=np.sqrt(np.sum(np.square(data_제약과생물공학_per['1/per']-mu_inv_per)*data_제약과생물공학_per['market_weight']))
        std_inv_div=np.sqrt(np.sum(np.square(data_제약과생물공학_div['div_yield']-mu_inv_div)*data_제약과생물공학_div['market_weight']))
        
        data_제약과생물공학1=(data_제약과생물공학_pbr['1/pbr']-mu_inv_pbr)/std_inv_pbr
        data_제약과생물공학1.name= 'pbr_z'
        data_제약과생물공학2=(data_제약과생물공학_per['1/per']-mu_inv_per)/std_inv_per
        data_제약과생물공학2.name= 'per_z'
        data_제약과생물공학3=(data_제약과생물공학_div['div_yield']-mu_inv_div)/std_inv_div
        data_제약과생물공학3.name= 'div_z'
              
        result_제약과생물공학 = pd.concat([data_제약과생물공학, data_제약과생물공학1, data_제약과생물공학2, data_제약과생물공학3], axis = 1)
        
        # np.nanmean : nan 값 포함해서 평균 내기!!
        result_제약과생물공학 = result_제약과생물공학.assign(z_score=np.nanmean(result_제약과생물공학.loc[:,['pbr_z','per_z','div_z']],axis=1))
    #    result_temp = result
    
        
        # z_score > 0 인것이 가치주라고 msci에서 하고있음
        locals()['result_{}'.format(a)] =result_제약과생물공학[result_제약과생물공학['z_score'].notnull()]
        a=a+1
   
     #은행 섹터
    if (np.sum(first_data['WICS_MID']=='은행')>0)&(np.sum(sector_mom['CO_NM_x']=='은행')==1):
        data_은행 = first_data[first_data['WICS_MID']=="은행"]
        # per, pbr, div_yield 구할때는 전체 시가총액을 사용,
        # 시총비중 구할떄는 free-float
        data_은행['size_FIF_wisefn']=data_은행['size_FIF_wisefn']/1000    #size 단위 thousand
        data_은행['1/pbr']=data_은행['EQUITY']/data_은행['MARKET_CAP']
        data_은행['1/per']=data_은행['ADJ_NI_12M_FWD']/data_은행['MARKET_CAP']
        data_은행['div_yield']=data_은행['CASH_DIV_COM']/data_은행['MARKET_CAP']
        
        # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
        data_은행 = data_은행.replace([np.inf, -np.inf],np.nan)  
        
        # Null 값 제거
        data_은행_per = data_은행[data_은행['1/per'].notnull()]
        data_은행_pbr = data_은행[data_은행['1/pbr'].notnull()]
        data_은행_div = data_은행[data_은행['div_yield'].notnull()]
    
    
        # 시가총액비중 구함 
        data_은행_pbr_cap = np.sum(data_은행_pbr['size_FIF_wisefn'])
        data_은행_per_cap = np.sum(data_은행_per['size_FIF_wisefn'])
        data_은행_div_cap = np.sum(data_은행_div['size_FIF_wisefn'])
    
        data_은행_pbr = data_은행_pbr.assign(market_weight=data_은행_pbr['size_FIF_wisefn']/data_은행_pbr_cap)
        data_은행_per = data_은행_per.assign(market_weight=data_은행_per['size_FIF_wisefn']/data_은행_per_cap)
        data_은행_div = data_은행_div.assign(market_weight=data_은행_div['size_FIF_wisefn']/data_은행_div_cap)
        
        # 시총가중 평균 
        mu_inv_pbr=np.sum(data_은행_pbr['1/pbr']*data_은행_pbr['market_weight'])
        mu_inv_per=np.sum(data_은행_per['1/per']*data_은행_per['market_weight'])
        mu_inv_div=np.sum(data_은행_div['div_yield']*data_은행_div['market_weight'])
        
        # 시총 가중 표준편자
        std_inv_pbr=np.sqrt(np.sum(np.square(data_은행_pbr['1/pbr']-mu_inv_pbr)*data_은행_pbr['market_weight']))
        std_inv_per=np.sqrt(np.sum(np.square(data_은행_per['1/per']-mu_inv_per)*data_은행_per['market_weight']))
        std_inv_div=np.sqrt(np.sum(np.square(data_은행_div['div_yield']-mu_inv_div)*data_은행_div['market_weight']))
        
        data_은행1=(data_은행_pbr['1/pbr']-mu_inv_pbr)/std_inv_pbr
        data_은행1.name= 'pbr_z'
        data_은행2=(data_은행_per['1/per']-mu_inv_per)/std_inv_per
        data_은행2.name= 'per_z'
        data_은행3=(data_은행_div['div_yield']-mu_inv_div)/std_inv_div
        data_은행3.name= 'div_z'
              
        result_은행 = pd.concat([data_은행, data_은행1, data_은행2, data_은행3], axis = 1)
        
        # np.nanmean : nan 값 포함해서 평균 내기!!
        result_은행 = result_은행.assign(z_score=np.nanmean(result_은행.loc[:,['pbr_z','per_z','div_z']],axis=1))
    #    result_temp = result
    
        
        # z_score > 0 인것이 가치주라고 msci에서 하고있음
        locals()['result_{}'.format(a)] =result_은행[result_은행['z_score'].notnull()]
        a=a+1
    
     #증권 섹터
    if (np.sum(first_data['WICS_MID']=='증권')>0)&(np.sum(sector_mom['CO_NM_x']=='증권')==1):
        data_증권 = first_data[first_data['WICS_MID']=="증권"]
        # per, pbr, div_yield 구할때는 전체 시가총액을 사용,
        # 시총비중 구할떄는 free-float
        data_증권['size_FIF_wisefn']=data_증권['size_FIF_wisefn']/1000    #size 단위 thousand
        data_증권['1/pbr']=data_증권['EQUITY']/data_증권['MARKET_CAP']
        data_증권['1/per']=data_증권['ADJ_NI_12M_FWD']/data_증권['MARKET_CAP']
        data_증권['div_yield']=data_증권['CASH_DIV_COM']/data_증권['MARKET_CAP']
        
        # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
        data_증권 = data_증권.replace([np.inf, -np.inf],np.nan)  
        
        # Null 값 제거
        data_증권_per = data_증권[data_증권['1/per'].notnull()]
        data_증권_pbr = data_증권[data_증권['1/pbr'].notnull()]
        data_증권_div = data_증권[data_증권['div_yield'].notnull()]
    
    
        # 시가총액비중 구함 
        data_증권_pbr_cap = np.sum(data_증권_pbr['size_FIF_wisefn'])
        data_증권_per_cap = np.sum(data_증권_per['size_FIF_wisefn'])
        data_증권_div_cap = np.sum(data_증권_div['size_FIF_wisefn'])
    
        data_증권_pbr = data_증권_pbr.assign(market_weight=data_증권_pbr['size_FIF_wisefn']/data_증권_pbr_cap)
        data_증권_per = data_증권_per.assign(market_weight=data_증권_per['size_FIF_wisefn']/data_증권_per_cap)
        data_증권_div = data_증권_div.assign(market_weight=data_증권_div['size_FIF_wisefn']/data_증권_div_cap)
        
        # 시총가중 평균 
        mu_inv_pbr=np.sum(data_증권_pbr['1/pbr']*data_증권_pbr['market_weight'])
        mu_inv_per=np.sum(data_증권_per['1/per']*data_증권_per['market_weight'])
        mu_inv_div=np.sum(data_증권_div['div_yield']*data_증권_div['market_weight'])
        
        # 시총 가중 표준편자
        std_inv_pbr=np.sqrt(np.sum(np.square(data_증권_pbr['1/pbr']-mu_inv_pbr)*data_증권_pbr['market_weight']))
        std_inv_per=np.sqrt(np.sum(np.square(data_증권_per['1/per']-mu_inv_per)*data_증권_per['market_weight']))
        std_inv_div=np.sqrt(np.sum(np.square(data_증권_div['div_yield']-mu_inv_div)*data_증권_div['market_weight']))
        
        data_증권1=(data_증권_pbr['1/pbr']-mu_inv_pbr)/std_inv_pbr
        data_증권1.name= 'pbr_z'
        data_증권2=(data_증권_per['1/per']-mu_inv_per)/std_inv_per
        data_증권2.name= 'per_z'
        data_증권3=(data_증권_div['div_yield']-mu_inv_div)/std_inv_div
        data_증권3.name= 'div_z'
              
        result_증권 = pd.concat([data_증권, data_증권1, data_증권2, data_증권3], axis = 1)
        
        # np.nanmean : nan 값 포함해서 평균 내기!!
        result_증권 = result_증권.assign(z_score=np.nanmean(result_증권.loc[:,['pbr_z','per_z','div_z']],axis=1))
    #    result_temp = result
    
        
        # z_score > 0 인것이 가치주라고 msci에서 하고있음
        locals()['result_{}'.format(a)] =result_증권[result_증권['z_score'].notnull()]
        a=a+1
    
     #다각화된금융 섹터
    if (np.sum(first_data['WICS_MID']=='다각화된금융')>0)&(np.sum(sector_mom['CO_NM_x']=='다각화된금융')==1):
        data_다각화된금융 = first_data[first_data['WICS_MID']=="다각화된금융"]
        # per, pbr, div_yield 구할때는 전체 시가총액을 사용,
        # 시총비중 구할떄는 free-float
        data_다각화된금융['size_FIF_wisefn']=data_다각화된금융['size_FIF_wisefn']/1000    #size 단위 thousand
        data_다각화된금융['1/pbr']=data_다각화된금융['EQUITY']/data_다각화된금융['MARKET_CAP']
        data_다각화된금융['1/per']=data_다각화된금융['ADJ_NI_12M_FWD']/data_다각화된금융['MARKET_CAP']
        data_다각화된금융['div_yield']=data_다각화된금융['CASH_DIV_COM']/data_다각화된금융['MARKET_CAP']
        
        # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
        data_다각화된금융 = data_다각화된금융.replace([np.inf, -np.inf],np.nan)  
        
        # Null 값 제거
        data_다각화된금융_per = data_다각화된금융[data_다각화된금융['1/per'].notnull()]
        data_다각화된금융_pbr = data_다각화된금융[data_다각화된금융['1/pbr'].notnull()]
        data_다각화된금융_div = data_다각화된금융[data_다각화된금융['div_yield'].notnull()]
    
    
        # 시가총액비중 구함 
        data_다각화된금융_pbr_cap = np.sum(data_다각화된금융_pbr['size_FIF_wisefn'])
        data_다각화된금융_per_cap = np.sum(data_다각화된금융_per['size_FIF_wisefn'])
        data_다각화된금융_div_cap = np.sum(data_다각화된금융_div['size_FIF_wisefn'])
    
        data_다각화된금융_pbr = data_다각화된금융_pbr.assign(market_weight=data_다각화된금융_pbr['size_FIF_wisefn']/data_다각화된금융_pbr_cap)
        data_다각화된금융_per = data_다각화된금융_per.assign(market_weight=data_다각화된금융_per['size_FIF_wisefn']/data_다각화된금융_per_cap)
        data_다각화된금융_div = data_다각화된금융_div.assign(market_weight=data_다각화된금융_div['size_FIF_wisefn']/data_다각화된금융_div_cap)
        
        # 시총가중 평균 
        mu_inv_pbr=np.sum(data_다각화된금융_pbr['1/pbr']*data_다각화된금융_pbr['market_weight'])
        mu_inv_per=np.sum(data_다각화된금융_per['1/per']*data_다각화된금융_per['market_weight'])
        mu_inv_div=np.sum(data_다각화된금융_div['div_yield']*data_다각화된금융_div['market_weight'])
        
        # 시총 가중 표준편자
        std_inv_pbr=np.sqrt(np.sum(np.square(data_다각화된금융_pbr['1/pbr']-mu_inv_pbr)*data_다각화된금융_pbr['market_weight']))
        std_inv_per=np.sqrt(np.sum(np.square(data_다각화된금융_per['1/per']-mu_inv_per)*data_다각화된금융_per['market_weight']))
        std_inv_div=np.sqrt(np.sum(np.square(data_다각화된금융_div['div_yield']-mu_inv_div)*data_다각화된금융_div['market_weight']))
        
        data_다각화된금융1=(data_다각화된금융_pbr['1/pbr']-mu_inv_pbr)/std_inv_pbr
        data_다각화된금융1.name= 'pbr_z'
        data_다각화된금융2=(data_다각화된금융_per['1/per']-mu_inv_per)/std_inv_per
        data_다각화된금융2.name= 'per_z'
        data_다각화된금융3=(data_다각화된금융_div['div_yield']-mu_inv_div)/std_inv_div
        data_다각화된금융3.name= 'div_z'
              
        result_다각화된금융 = pd.concat([data_다각화된금융, data_다각화된금융1, data_다각화된금융2, data_다각화된금융3], axis = 1)
        
        # np.nanmean : nan 값 포함해서 평균 내기!!
        result_다각화된금융 = result_다각화된금융.assign(z_score=np.nanmean(result_다각화된금융.loc[:,['pbr_z','per_z','div_z']],axis=1))
    #    result_temp = result
    
        
        # z_score > 0 인것이 가치주라고 msci에서 하고있음
        locals()['result_{}'.format(a)] =result_다각화된금융[result_다각화된금융['z_score'].notnull()]
        a=a+1
    
     #보험 섹터
    if (np.sum(first_data['WICS_MID']=='보험')>0)&(np.sum(sector_mom['CO_NM_x']=='보험')==1):
        data_보험 = first_data[first_data['WICS_MID']=="보험"]
        # per, pbr, div_yield 구할때는 전체 시가총액을 사용,
        # 시총비중 구할떄는 free-float
        data_보험['size_FIF_wisefn']=data_보험['size_FIF_wisefn']/1000    #size 단위 thousand
        data_보험['1/pbr']=data_보험['EQUITY']/data_보험['MARKET_CAP']
        data_보험['1/per']=data_보험['ADJ_NI_12M_FWD']/data_보험['MARKET_CAP']
        data_보험['div_yield']=data_보험['CASH_DIV_COM']/data_보험['MARKET_CAP']
        
        # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
        data_보험 = data_보험.replace([np.inf, -np.inf],np.nan)  
        
        # Null 값 제거
        data_보험_per = data_보험[data_보험['1/per'].notnull()]
        data_보험_pbr = data_보험[data_보험['1/pbr'].notnull()]
        data_보험_div = data_보험[data_보험['div_yield'].notnull()]
    
    
        # 시가총액비중 구함 
        data_보험_pbr_cap = np.sum(data_보험_pbr['size_FIF_wisefn'])
        data_보험_per_cap = np.sum(data_보험_per['size_FIF_wisefn'])
        data_보험_div_cap = np.sum(data_보험_div['size_FIF_wisefn'])
    
        data_보험_pbr = data_보험_pbr.assign(market_weight=data_보험_pbr['size_FIF_wisefn']/data_보험_pbr_cap)
        data_보험_per = data_보험_per.assign(market_weight=data_보험_per['size_FIF_wisefn']/data_보험_per_cap)
        data_보험_div = data_보험_div.assign(market_weight=data_보험_div['size_FIF_wisefn']/data_보험_div_cap)
        
        # 시총가중 평균 
        mu_inv_pbr=np.sum(data_보험_pbr['1/pbr']*data_보험_pbr['market_weight'])
        mu_inv_per=np.sum(data_보험_per['1/per']*data_보험_per['market_weight'])
        mu_inv_div=np.sum(data_보험_div['div_yield']*data_보험_div['market_weight'])
        
        # 시총 가중 표준편자
        std_inv_pbr=np.sqrt(np.sum(np.square(data_보험_pbr['1/pbr']-mu_inv_pbr)*data_보험_pbr['market_weight']))
        std_inv_per=np.sqrt(np.sum(np.square(data_보험_per['1/per']-mu_inv_per)*data_보험_per['market_weight']))
        std_inv_div=np.sqrt(np.sum(np.square(data_보험_div['div_yield']-mu_inv_div)*data_보험_div['market_weight']))
        
        data_보험1=(data_보험_pbr['1/pbr']-mu_inv_pbr)/std_inv_pbr
        data_보험1.name= 'pbr_z'
        data_보험2=(data_보험_per['1/per']-mu_inv_per)/std_inv_per
        data_보험2.name= 'per_z'
        data_보험3=(data_보험_div['div_yield']-mu_inv_div)/std_inv_div
        data_보험3.name= 'div_z'
              
        result_보험 = pd.concat([data_보험, data_보험1, data_보험2, data_보험3], axis = 1)
        
        # np.nanmean : nan 값 포함해서 평균 내기!!
        result_보험 = result_보험.assign(z_score=np.nanmean(result_보험.loc[:,['pbr_z','per_z','div_z']],axis=1))
    #    result_temp = result
    
        
        # z_score > 0 인것이 가치주라고 msci에서 하고있음
        locals()['result_{}'.format(a)] =result_보험[result_보험['z_score'].notnull()]
        a=a+1
   
     #부동산 섹터
    if (np.sum(first_data['WICS_MID']=='부동산')>0)&(np.sum(sector_mom['CO_NM_x']=='부동산')==1):
        data_부동산 = first_data[first_data['WICS_MID']=="부동산"]
        # per, pbr, div_yield 구할때는 전체 시가총액을 사용,
        # 시총비중 구할떄는 free-float
        data_부동산['size_FIF_wisefn']=data_부동산['size_FIF_wisefn']/1000    #size 단위 thousand
        data_부동산['1/pbr']=data_부동산['EQUITY']/data_부동산['MARKET_CAP']
        data_부동산['1/per']=data_부동산['ADJ_NI_12M_FWD']/data_부동산['MARKET_CAP']
        data_부동산['div_yield']=data_부동산['CASH_DIV_COM']/data_부동산['MARKET_CAP']
        
        # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
        data_부동산 = data_부동산.replace([np.inf, -np.inf],np.nan)  
        
        # Null 값 제거
        data_부동산_per = data_부동산[data_부동산['1/per'].notnull()]
        data_부동산_pbr = data_부동산[data_부동산['1/pbr'].notnull()]
        data_부동산_div = data_부동산[data_부동산['div_yield'].notnull()]
    
    
        # 시가총액비중 구함 
        data_부동산_pbr_cap = np.sum(data_부동산_pbr['size_FIF_wisefn'])
        data_부동산_per_cap = np.sum(data_부동산_per['size_FIF_wisefn'])
        data_부동산_div_cap = np.sum(data_부동산_div['size_FIF_wisefn'])
    
        data_부동산_pbr = data_부동산_pbr.assign(market_weight=data_부동산_pbr['size_FIF_wisefn']/data_부동산_pbr_cap)
        data_부동산_per = data_부동산_per.assign(market_weight=data_부동산_per['size_FIF_wisefn']/data_부동산_per_cap)
        data_부동산_div = data_부동산_div.assign(market_weight=data_부동산_div['size_FIF_wisefn']/data_부동산_div_cap)
        
        # 시총가중 평균 
        mu_inv_pbr=np.sum(data_부동산_pbr['1/pbr']*data_부동산_pbr['market_weight'])
        mu_inv_per=np.sum(data_부동산_per['1/per']*data_부동산_per['market_weight'])
        mu_inv_div=np.sum(data_부동산_div['div_yield']*data_부동산_div['market_weight'])
        
        # 시총 가중 표준편자
        std_inv_pbr=np.sqrt(np.sum(np.square(data_부동산_pbr['1/pbr']-mu_inv_pbr)*data_부동산_pbr['market_weight']))
        std_inv_per=np.sqrt(np.sum(np.square(data_부동산_per['1/per']-mu_inv_per)*data_부동산_per['market_weight']))
        std_inv_div=np.sqrt(np.sum(np.square(data_부동산_div['div_yield']-mu_inv_div)*data_부동산_div['market_weight']))
        
        data_부동산1=(data_부동산_pbr['1/pbr']-mu_inv_pbr)/std_inv_pbr
        data_부동산1.name= 'pbr_z'
        data_부동산2=(data_부동산_per['1/per']-mu_inv_per)/std_inv_per
        data_부동산2.name= 'per_z'
        data_부동산3=(data_부동산_div['div_yield']-mu_inv_div)/std_inv_div
        data_부동산3.name= 'div_z'
              
        result_부동산 = pd.concat([data_부동산, data_부동산1, data_부동산2, data_부동산3], axis = 1)
        
        # np.nanmean : nan 값 포함해서 평균 내기!!
        result_부동산 = result_부동산.assign(z_score=np.nanmean(result_부동산.loc[:,['pbr_z','per_z','div_z']],axis=1))
    #    result_temp = result
    
        
        # z_score > 0 인것이 가치주라고 msci에서 하고있음
        locals()['result_{}'.format(a)] =result_부동산[result_부동산['z_score'].notnull()]
        a=a+1
    
     #기타금융서비스 섹터
    if (np.sum(first_data['WICS_MID']=='기타금융서비스')>0)&(np.sum(sector_mom['CO_NM_x']=='기타금융서비스')==1):
        data_기타금융서비스 = first_data[first_data['WICS_MID']=="기타금융서비스"]
        # per, pbr, div_yield 구할때는 전체 시가총액을 사용,
        # 시총비중 구할떄는 free-float
        data_기타금융서비스['size_FIF_wisefn']=data_기타금융서비스['size_FIF_wisefn']/1000    #size 단위 thousand
        data_기타금융서비스['1/pbr']=data_기타금융서비스['EQUITY']/data_기타금융서비스['MARKET_CAP']
        data_기타금융서비스['1/per']=data_기타금융서비스['ADJ_NI_12M_FWD']/data_기타금융서비스['MARKET_CAP']
        data_기타금융서비스['div_yield']=data_기타금융서비스['CASH_DIV_COM']/data_기타금융서비스['MARKET_CAP']
        
        # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
        data_기타금융서비스 = data_기타금융서비스.replace([np.inf, -np.inf],np.nan)  
        
        # Null 값 제거
        data_기타금융서비스_per = data_기타금융서비스[data_기타금융서비스['1/per'].notnull()]
        data_기타금융서비스_pbr = data_기타금융서비스[data_기타금융서비스['1/pbr'].notnull()]
        data_기타금융서비스_div = data_기타금융서비스[data_기타금융서비스['div_yield'].notnull()]
    
    
        # 시가총액비중 구함 
        data_기타금융서비스_pbr_cap = np.sum(data_기타금융서비스_pbr['size_FIF_wisefn'])
        data_기타금융서비스_per_cap = np.sum(data_기타금융서비스_per['size_FIF_wisefn'])
        data_기타금융서비스_div_cap = np.sum(data_기타금융서비스_div['size_FIF_wisefn'])
    
        data_기타금융서비스_pbr = data_기타금융서비스_pbr.assign(market_weight=data_기타금융서비스_pbr['size_FIF_wisefn']/data_기타금융서비스_pbr_cap)
        data_기타금융서비스_per = data_기타금융서비스_per.assign(market_weight=data_기타금융서비스_per['size_FIF_wisefn']/data_기타금융서비스_per_cap)
        data_기타금융서비스_div = data_기타금융서비스_div.assign(market_weight=data_기타금융서비스_div['size_FIF_wisefn']/data_기타금융서비스_div_cap)
        
        # 시총가중 평균 
        mu_inv_pbr=np.sum(data_기타금융서비스_pbr['1/pbr']*data_기타금융서비스_pbr['market_weight'])
        mu_inv_per=np.sum(data_기타금융서비스_per['1/per']*data_기타금융서비스_per['market_weight'])
        mu_inv_div=np.sum(data_기타금융서비스_div['div_yield']*data_기타금융서비스_div['market_weight'])
        
        # 시총 가중 표준편자
        std_inv_pbr=np.sqrt(np.sum(np.square(data_기타금융서비스_pbr['1/pbr']-mu_inv_pbr)*data_기타금융서비스_pbr['market_weight']))
        std_inv_per=np.sqrt(np.sum(np.square(data_기타금융서비스_per['1/per']-mu_inv_per)*data_기타금융서비스_per['market_weight']))
        std_inv_div=np.sqrt(np.sum(np.square(data_기타금융서비스_div['div_yield']-mu_inv_div)*data_기타금융서비스_div['market_weight']))
        
        data_기타금융서비스1=(data_기타금융서비스_pbr['1/pbr']-mu_inv_pbr)/std_inv_pbr
        data_기타금융서비스1.name= 'pbr_z'
        data_기타금융서비스2=(data_기타금융서비스_per['1/per']-mu_inv_per)/std_inv_per
        data_기타금융서비스2.name= 'per_z'
        data_기타금융서비스3=(data_기타금융서비스_div['div_yield']-mu_inv_div)/std_inv_div
        data_기타금융서비스3.name= 'div_z'
              
        result_기타금융서비스 = pd.concat([data_기타금융서비스, data_기타금융서비스1, data_기타금융서비스2, data_기타금융서비스3], axis = 1)
        
        # np.nanmean : nan 값 포함해서 평균 내기!!
        result_기타금융서비스 = result_기타금융서비스.assign(z_score=np.nanmean(result_기타금융서비스.loc[:,['pbr_z','per_z','div_z']],axis=1))
    #    result_temp = result
    
        
        # z_score > 0 인것이 가치주라고 msci에서 하고있음
        locals()['result_{}'.format(a)] =result_기타금융서비스[result_기타금융서비스['z_score'].notnull()]
        a=a+1
    
     #소프트웨어와서비스 섹터
    if (np.sum(first_data['WICS_MID']=='소프트웨어와서비스')>0)&(np.sum(sector_mom['CO_NM_x']=='소프트웨어와서비스')==1):
        data_소프트웨어와서비스 = first_data[first_data['WICS_MID']=="소프트웨어와서비스"]
        # per, pbr, div_yield 구할때는 전체 시가총액을 사용,
        # 시총비중 구할떄는 free-float
        data_소프트웨어와서비스['size_FIF_wisefn']=data_소프트웨어와서비스['size_FIF_wisefn']/1000    #size 단위 thousand
        data_소프트웨어와서비스['1/pbr']=data_소프트웨어와서비스['EQUITY']/data_소프트웨어와서비스['MARKET_CAP']
        data_소프트웨어와서비스['1/per']=data_소프트웨어와서비스['ADJ_NI_12M_FWD']/data_소프트웨어와서비스['MARKET_CAP']
        data_소프트웨어와서비스['div_yield']=data_소프트웨어와서비스['CASH_DIV_COM']/data_소프트웨어와서비스['MARKET_CAP']
        
        # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
        data_소프트웨어와서비스 = data_소프트웨어와서비스.replace([np.inf, -np.inf],np.nan)  
        
        # Null 값 제거
        data_소프트웨어와서비스_per = data_소프트웨어와서비스[data_소프트웨어와서비스['1/per'].notnull()]
        data_소프트웨어와서비스_pbr = data_소프트웨어와서비스[data_소프트웨어와서비스['1/pbr'].notnull()]
        data_소프트웨어와서비스_div = data_소프트웨어와서비스[data_소프트웨어와서비스['div_yield'].notnull()]
    
    
        # 시가총액비중 구함 
        data_소프트웨어와서비스_pbr_cap = np.sum(data_소프트웨어와서비스_pbr['size_FIF_wisefn'])
        data_소프트웨어와서비스_per_cap = np.sum(data_소프트웨어와서비스_per['size_FIF_wisefn'])
        data_소프트웨어와서비스_div_cap = np.sum(data_소프트웨어와서비스_div['size_FIF_wisefn'])
    
        data_소프트웨어와서비스_pbr = data_소프트웨어와서비스_pbr.assign(market_weight=data_소프트웨어와서비스_pbr['size_FIF_wisefn']/data_소프트웨어와서비스_pbr_cap)
        data_소프트웨어와서비스_per = data_소프트웨어와서비스_per.assign(market_weight=data_소프트웨어와서비스_per['size_FIF_wisefn']/data_소프트웨어와서비스_per_cap)
        data_소프트웨어와서비스_div = data_소프트웨어와서비스_div.assign(market_weight=data_소프트웨어와서비스_div['size_FIF_wisefn']/data_소프트웨어와서비스_div_cap)
        
        # 시총가중 평균 
        mu_inv_pbr=np.sum(data_소프트웨어와서비스_pbr['1/pbr']*data_소프트웨어와서비스_pbr['market_weight'])
        mu_inv_per=np.sum(data_소프트웨어와서비스_per['1/per']*data_소프트웨어와서비스_per['market_weight'])
        mu_inv_div=np.sum(data_소프트웨어와서비스_div['div_yield']*data_소프트웨어와서비스_div['market_weight'])
        
        # 시총 가중 표준편자
        std_inv_pbr=np.sqrt(np.sum(np.square(data_소프트웨어와서비스_pbr['1/pbr']-mu_inv_pbr)*data_소프트웨어와서비스_pbr['market_weight']))
        std_inv_per=np.sqrt(np.sum(np.square(data_소프트웨어와서비스_per['1/per']-mu_inv_per)*data_소프트웨어와서비스_per['market_weight']))
        std_inv_div=np.sqrt(np.sum(np.square(data_소프트웨어와서비스_div['div_yield']-mu_inv_div)*data_소프트웨어와서비스_div['market_weight']))
        
        data_소프트웨어와서비스1=(data_소프트웨어와서비스_pbr['1/pbr']-mu_inv_pbr)/std_inv_pbr
        data_소프트웨어와서비스1.name= 'pbr_z'
        data_소프트웨어와서비스2=(data_소프트웨어와서비스_per['1/per']-mu_inv_per)/std_inv_per
        data_소프트웨어와서비스2.name= 'per_z'
        data_소프트웨어와서비스3=(data_소프트웨어와서비스_div['div_yield']-mu_inv_div)/std_inv_div
        data_소프트웨어와서비스3.name= 'div_z'
              
        result_소프트웨어와서비스 = pd.concat([data_소프트웨어와서비스, data_소프트웨어와서비스1, data_소프트웨어와서비스2, data_소프트웨어와서비스3], axis = 1)
        
        # np.nanmean : nan 값 포함해서 평균 내기!!
        result_소프트웨어와서비스 = result_소프트웨어와서비스.assign(z_score=np.nanmean(result_소프트웨어와서비스.loc[:,['pbr_z','per_z','div_z']],axis=1))
    #    result_temp = result
    
        
        # z_score > 0 인것이 가치주라고 msci에서 하고있음
        locals()['result_{}'.format(a)] =result_소프트웨어와서비스[result_소프트웨어와서비스['z_score'].notnull()]
        a=a+1
    
     #기술하드웨어와장비 섹터
    if (np.sum(first_data['WICS_MID']=='기술하드웨어와장비')>0)&(np.sum(sector_mom['CO_NM_x']=='기술하드웨어와장비')==1):
        data_기술하드웨어와장비 = first_data[first_data['WICS_MID']=="기술하드웨어와장비"]
        # per, pbr, div_yield 구할때는 전체 시가총액을 사용,
        # 시총비중 구할떄는 free-float
        data_기술하드웨어와장비['size_FIF_wisefn']=data_기술하드웨어와장비['size_FIF_wisefn']/1000    #size 단위 thousand
        data_기술하드웨어와장비['1/pbr']=data_기술하드웨어와장비['EQUITY']/data_기술하드웨어와장비['MARKET_CAP']
        data_기술하드웨어와장비['1/per']=data_기술하드웨어와장비['ADJ_NI_12M_FWD']/data_기술하드웨어와장비['MARKET_CAP']
        data_기술하드웨어와장비['div_yield']=data_기술하드웨어와장비['CASH_DIV_COM']/data_기술하드웨어와장비['MARKET_CAP']
        
        # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
        data_기술하드웨어와장비 = data_기술하드웨어와장비.replace([np.inf, -np.inf],np.nan)  
        
        # Null 값 제거
        data_기술하드웨어와장비_per = data_기술하드웨어와장비[data_기술하드웨어와장비['1/per'].notnull()]
        data_기술하드웨어와장비_pbr = data_기술하드웨어와장비[data_기술하드웨어와장비['1/pbr'].notnull()]
        data_기술하드웨어와장비_div = data_기술하드웨어와장비[data_기술하드웨어와장비['div_yield'].notnull()]
    
    
        # 시가총액비중 구함 
        data_기술하드웨어와장비_pbr_cap = np.sum(data_기술하드웨어와장비_pbr['size_FIF_wisefn'])
        data_기술하드웨어와장비_per_cap = np.sum(data_기술하드웨어와장비_per['size_FIF_wisefn'])
        data_기술하드웨어와장비_div_cap = np.sum(data_기술하드웨어와장비_div['size_FIF_wisefn'])
    
        data_기술하드웨어와장비_pbr = data_기술하드웨어와장비_pbr.assign(market_weight=data_기술하드웨어와장비_pbr['size_FIF_wisefn']/data_기술하드웨어와장비_pbr_cap)
        data_기술하드웨어와장비_per = data_기술하드웨어와장비_per.assign(market_weight=data_기술하드웨어와장비_per['size_FIF_wisefn']/data_기술하드웨어와장비_per_cap)
        data_기술하드웨어와장비_div = data_기술하드웨어와장비_div.assign(market_weight=data_기술하드웨어와장비_div['size_FIF_wisefn']/data_기술하드웨어와장비_div_cap)
        
        # 시총가중 평균 
        mu_inv_pbr=np.sum(data_기술하드웨어와장비_pbr['1/pbr']*data_기술하드웨어와장비_pbr['market_weight'])
        mu_inv_per=np.sum(data_기술하드웨어와장비_per['1/per']*data_기술하드웨어와장비_per['market_weight'])
        mu_inv_div=np.sum(data_기술하드웨어와장비_div['div_yield']*data_기술하드웨어와장비_div['market_weight'])
        
        # 시총 가중 표준편자
        std_inv_pbr=np.sqrt(np.sum(np.square(data_기술하드웨어와장비_pbr['1/pbr']-mu_inv_pbr)*data_기술하드웨어와장비_pbr['market_weight']))
        std_inv_per=np.sqrt(np.sum(np.square(data_기술하드웨어와장비_per['1/per']-mu_inv_per)*data_기술하드웨어와장비_per['market_weight']))
        std_inv_div=np.sqrt(np.sum(np.square(data_기술하드웨어와장비_div['div_yield']-mu_inv_div)*data_기술하드웨어와장비_div['market_weight']))
        
        data_기술하드웨어와장비1=(data_기술하드웨어와장비_pbr['1/pbr']-mu_inv_pbr)/std_inv_pbr
        data_기술하드웨어와장비1.name= 'pbr_z'
        data_기술하드웨어와장비2=(data_기술하드웨어와장비_per['1/per']-mu_inv_per)/std_inv_per
        data_기술하드웨어와장비2.name= 'per_z'
        data_기술하드웨어와장비3=(data_기술하드웨어와장비_div['div_yield']-mu_inv_div)/std_inv_div
        data_기술하드웨어와장비3.name= 'div_z'
              
        result_기술하드웨어와장비 = pd.concat([data_기술하드웨어와장비, data_기술하드웨어와장비1, data_기술하드웨어와장비2, data_기술하드웨어와장비3], axis = 1)
        
        # np.nanmean : nan 값 포함해서 평균 내기!!
        result_기술하드웨어와장비 = result_기술하드웨어와장비.assign(z_score=np.nanmean(result_기술하드웨어와장비.loc[:,['pbr_z','per_z','div_z']],axis=1))
    #    result_temp = result
    
        
        # z_score > 0 인것이 가치주라고 msci에서 하고있음
        locals()['result_{}'.format(a)] =result_기술하드웨어와장비[result_기술하드웨어와장비['z_score'].notnull()]
        a=a+1
    
     #반도체와반도체장비 섹터
    if (np.sum(first_data['WICS_MID']=='반도체와반도체장비')>0)&(np.sum(sector_mom['CO_NM_x']=='반도체와반도체장비')==1):
        data_반도체와반도체장비 = first_data[first_data['WICS_MID']=="반도체와반도체장비"]
        # per, pbr, div_yield 구할때는 전체 시가총액을 사용,
        # 시총비중 구할떄는 free-float
        data_반도체와반도체장비['size_FIF_wisefn']=data_반도체와반도체장비['size_FIF_wisefn']/1000    #size 단위 thousand
        data_반도체와반도체장비['1/pbr']=data_반도체와반도체장비['EQUITY']/data_반도체와반도체장비['MARKET_CAP']
        data_반도체와반도체장비['1/per']=data_반도체와반도체장비['ADJ_NI_12M_FWD']/data_반도체와반도체장비['MARKET_CAP']
        data_반도체와반도체장비['div_yield']=data_반도체와반도체장비['CASH_DIV_COM']/data_반도체와반도체장비['MARKET_CAP']
        
        # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
        data_반도체와반도체장비 = data_반도체와반도체장비.replace([np.inf, -np.inf],np.nan)  
        
        # Null 값 제거
        data_반도체와반도체장비_per = data_반도체와반도체장비[data_반도체와반도체장비['1/per'].notnull()]
        data_반도체와반도체장비_pbr = data_반도체와반도체장비[data_반도체와반도체장비['1/pbr'].notnull()]
        data_반도체와반도체장비_div = data_반도체와반도체장비[data_반도체와반도체장비['div_yield'].notnull()]
    
    
        # 시가총액비중 구함 
        data_반도체와반도체장비_pbr_cap = np.sum(data_반도체와반도체장비_pbr['size_FIF_wisefn'])
        data_반도체와반도체장비_per_cap = np.sum(data_반도체와반도체장비_per['size_FIF_wisefn'])
        data_반도체와반도체장비_div_cap = np.sum(data_반도체와반도체장비_div['size_FIF_wisefn'])
    
        data_반도체와반도체장비_pbr = data_반도체와반도체장비_pbr.assign(market_weight=data_반도체와반도체장비_pbr['size_FIF_wisefn']/data_반도체와반도체장비_pbr_cap)
        data_반도체와반도체장비_per = data_반도체와반도체장비_per.assign(market_weight=data_반도체와반도체장비_per['size_FIF_wisefn']/data_반도체와반도체장비_per_cap)
        data_반도체와반도체장비_div = data_반도체와반도체장비_div.assign(market_weight=data_반도체와반도체장비_div['size_FIF_wisefn']/data_반도체와반도체장비_div_cap)
        
        # 시총가중 평균 
        mu_inv_pbr=np.sum(data_반도체와반도체장비_pbr['1/pbr']*data_반도체와반도체장비_pbr['market_weight'])
        mu_inv_per=np.sum(data_반도체와반도체장비_per['1/per']*data_반도체와반도체장비_per['market_weight'])
        mu_inv_div=np.sum(data_반도체와반도체장비_div['div_yield']*data_반도체와반도체장비_div['market_weight'])
        
        # 시총 가중 표준편자
        std_inv_pbr=np.sqrt(np.sum(np.square(data_반도체와반도체장비_pbr['1/pbr']-mu_inv_pbr)*data_반도체와반도체장비_pbr['market_weight']))
        std_inv_per=np.sqrt(np.sum(np.square(data_반도체와반도체장비_per['1/per']-mu_inv_per)*data_반도체와반도체장비_per['market_weight']))
        std_inv_div=np.sqrt(np.sum(np.square(data_반도체와반도체장비_div['div_yield']-mu_inv_div)*data_반도체와반도체장비_div['market_weight']))
        
        data_반도체와반도체장비1=(data_반도체와반도체장비_pbr['1/pbr']-mu_inv_pbr)/std_inv_pbr
        data_반도체와반도체장비1.name= 'pbr_z'
        data_반도체와반도체장비2=(data_반도체와반도체장비_per['1/per']-mu_inv_per)/std_inv_per
        data_반도체와반도체장비2.name= 'per_z'
        data_반도체와반도체장비3=(data_반도체와반도체장비_div['div_yield']-mu_inv_div)/std_inv_div
        data_반도체와반도체장비3.name= 'div_z'
              
        result_반도체와반도체장비 = pd.concat([data_반도체와반도체장비, data_반도체와반도체장비1, data_반도체와반도체장비2, data_반도체와반도체장비3], axis = 1)
        
        # np.nanmean : nan 값 포함해서 평균 내기!!
        result_반도체와반도체장비 = result_반도체와반도체장비.assign(z_score=np.nanmean(result_반도체와반도체장비.loc[:,['pbr_z','per_z','div_z']],axis=1))
    #    result_temp = result
    
        
        # z_score > 0 인것이 가치주라고 msci에서 하고있음
        locals()['result_{}'.format(a)] =result_반도체와반도체장비[result_반도체와반도체장비['z_score'].notnull()]
        a=a+1
    
     #전자와 전기제품 섹터
    if (np.sum(first_data['WICS_MID']=='전자와 전기제품')>0)&(np.sum(sector_mom['CO_NM_x']=='전자와 전기제품')==1):
        data_전자와_전기제품 = first_data[first_data['WICS_MID']=="전자와 전기제품"]
        # per, pbr, div_yield 구할때는 전체 시가총액을 사용,
        # 시총비중 구할떄는 free-float
        data_전자와_전기제품['size_FIF_wisefn']=data_전자와_전기제품['size_FIF_wisefn']/1000    #size 단위 thousand
        data_전자와_전기제품['1/pbr']=data_전자와_전기제품['EQUITY']/data_전자와_전기제품['MARKET_CAP']
        data_전자와_전기제품['1/per']=data_전자와_전기제품['ADJ_NI_12M_FWD']/data_전자와_전기제품['MARKET_CAP']
        data_전자와_전기제품['div_yield']=data_전자와_전기제품['CASH_DIV_COM']/data_전자와_전기제품['MARKET_CAP']
        
        # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
        data_전자와_전기제품 = data_전자와_전기제품.replace([np.inf, -np.inf],np.nan)  
        
        # Null 값 제거
        data_전자와_전기제품_per = data_전자와_전기제품[data_전자와_전기제품['1/per'].notnull()]
        data_전자와_전기제품_pbr = data_전자와_전기제품[data_전자와_전기제품['1/pbr'].notnull()]
        data_전자와_전기제품_div = data_전자와_전기제품[data_전자와_전기제품['div_yield'].notnull()]
    
    
        # 시가총액비중 구함 
        data_전자와_전기제품_pbr_cap = np.sum(data_전자와_전기제품_pbr['size_FIF_wisefn'])
        data_전자와_전기제품_per_cap = np.sum(data_전자와_전기제품_per['size_FIF_wisefn'])
        data_전자와_전기제품_div_cap = np.sum(data_전자와_전기제품_div['size_FIF_wisefn'])
    
        data_전자와_전기제품_pbr = data_전자와_전기제품_pbr.assign(market_weight=data_전자와_전기제품_pbr['size_FIF_wisefn']/data_전자와_전기제품_pbr_cap)
        data_전자와_전기제품_per = data_전자와_전기제품_per.assign(market_weight=data_전자와_전기제품_per['size_FIF_wisefn']/data_전자와_전기제품_per_cap)
        data_전자와_전기제품_div = data_전자와_전기제품_div.assign(market_weight=data_전자와_전기제품_div['size_FIF_wisefn']/data_전자와_전기제품_div_cap)
        
        # 시총가중 평균 
        mu_inv_pbr=np.sum(data_전자와_전기제품_pbr['1/pbr']*data_전자와_전기제품_pbr['market_weight'])
        mu_inv_per=np.sum(data_전자와_전기제품_per['1/per']*data_전자와_전기제품_per['market_weight'])
        mu_inv_div=np.sum(data_전자와_전기제품_div['div_yield']*data_전자와_전기제품_div['market_weight'])
        
        # 시총 가중 표준편자
        std_inv_pbr=np.sqrt(np.sum(np.square(data_전자와_전기제품_pbr['1/pbr']-mu_inv_pbr)*data_전자와_전기제품_pbr['market_weight']))
        std_inv_per=np.sqrt(np.sum(np.square(data_전자와_전기제품_per['1/per']-mu_inv_per)*data_전자와_전기제품_per['market_weight']))
        std_inv_div=np.sqrt(np.sum(np.square(data_전자와_전기제품_div['div_yield']-mu_inv_div)*data_전자와_전기제품_div['market_weight']))
        
        data_전자와_전기제품1=(data_전자와_전기제품_pbr['1/pbr']-mu_inv_pbr)/std_inv_pbr
        data_전자와_전기제품1.name= 'pbr_z'
        data_전자와_전기제품2=(data_전자와_전기제품_per['1/per']-mu_inv_per)/std_inv_per
        data_전자와_전기제품2.name= 'per_z'
        data_전자와_전기제품3=(data_전자와_전기제품_div['div_yield']-mu_inv_div)/std_inv_div
        data_전자와_전기제품3.name= 'div_z'
              
        result_전자와_전기제품 = pd.concat([data_전자와_전기제품, data_전자와_전기제품1, data_전자와_전기제품2, data_전자와_전기제품3], axis = 1)
        
        # np.nanmean : nan 값 포함해서 평균 내기!!
        result_전자와_전기제품 = result_전자와_전기제품.assign(z_score=np.nanmean(result_전자와_전기제품.loc[:,['pbr_z','per_z','div_z']],axis=1))
    #    result_temp = result
    
        
        # z_score > 0 인것이 가치주라고 msci에서 하고있음
        locals()['result_{}'.format(a)] =result_전자와_전기제품[result_전자와_전기제품['z_score'].notnull()]
        a=a+1
    
     #디스플레이 섹터
    if (np.sum(first_data['WICS_MID']=='디스플레이')>0)&(np.sum(sector_mom['CO_NM_x']=='디스플레이')==1):
        data_디스플레이 = first_data[first_data['WICS_MID']=="디스플레이"]
        # per, pbr, div_yield 구할때는 전체 시가총액을 사용,
        # 시총비중 구할떄는 free-float
        data_디스플레이['size_FIF_wisefn']=data_디스플레이['size_FIF_wisefn']/1000    #size 단위 thousand
        data_디스플레이['1/pbr']=data_디스플레이['EQUITY']/data_디스플레이['MARKET_CAP']
        data_디스플레이['1/per']=data_디스플레이['ADJ_NI_12M_FWD']/data_디스플레이['MARKET_CAP']
        data_디스플레이['div_yield']=data_디스플레이['CASH_DIV_COM']/data_디스플레이['MARKET_CAP']
        
        # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
        data_디스플레이 = data_디스플레이.replace([np.inf, -np.inf],np.nan)  
        
        # Null 값 제거
        data_디스플레이_per = data_디스플레이[data_디스플레이['1/per'].notnull()]
        data_디스플레이_pbr = data_디스플레이[data_디스플레이['1/pbr'].notnull()]
        data_디스플레이_div = data_디스플레이[data_디스플레이['div_yield'].notnull()]
    
    
        # 시가총액비중 구함 
        data_디스플레이_pbr_cap = np.sum(data_디스플레이_pbr['size_FIF_wisefn'])
        data_디스플레이_per_cap = np.sum(data_디스플레이_per['size_FIF_wisefn'])
        data_디스플레이_div_cap = np.sum(data_디스플레이_div['size_FIF_wisefn'])
    
        data_디스플레이_pbr = data_디스플레이_pbr.assign(market_weight=data_디스플레이_pbr['size_FIF_wisefn']/data_디스플레이_pbr_cap)
        data_디스플레이_per = data_디스플레이_per.assign(market_weight=data_디스플레이_per['size_FIF_wisefn']/data_디스플레이_per_cap)
        data_디스플레이_div = data_디스플레이_div.assign(market_weight=data_디스플레이_div['size_FIF_wisefn']/data_디스플레이_div_cap)
        
        # 시총가중 평균 
        mu_inv_pbr=np.sum(data_디스플레이_pbr['1/pbr']*data_디스플레이_pbr['market_weight'])
        mu_inv_per=np.sum(data_디스플레이_per['1/per']*data_디스플레이_per['market_weight'])
        mu_inv_div=np.sum(data_디스플레이_div['div_yield']*data_디스플레이_div['market_weight'])
        
        # 시총 가중 표준편자
        std_inv_pbr=np.sqrt(np.sum(np.square(data_디스플레이_pbr['1/pbr']-mu_inv_pbr)*data_디스플레이_pbr['market_weight']))
        std_inv_per=np.sqrt(np.sum(np.square(data_디스플레이_per['1/per']-mu_inv_per)*data_디스플레이_per['market_weight']))
        std_inv_div=np.sqrt(np.sum(np.square(data_디스플레이_div['div_yield']-mu_inv_div)*data_디스플레이_div['market_weight']))
        
        data_디스플레이1=(data_디스플레이_pbr['1/pbr']-mu_inv_pbr)/std_inv_pbr
        data_디스플레이1.name= 'pbr_z'
        data_디스플레이2=(data_디스플레이_per['1/per']-mu_inv_per)/std_inv_per
        data_디스플레이2.name= 'per_z'
        data_디스플레이3=(data_디스플레이_div['div_yield']-mu_inv_div)/std_inv_div
        data_디스플레이3.name= 'div_z'
              
        result_디스플레이 = pd.concat([data_디스플레이, data_디스플레이1, data_디스플레이2, data_디스플레이3], axis = 1)
        
        # np.nanmean : nan 값 포함해서 평균 내기!!
        result_디스플레이 = result_디스플레이.assign(z_score=np.nanmean(result_디스플레이.loc[:,['pbr_z','per_z','div_z']],axis=1))
    #    result_temp = result
    
        
        # z_score > 0 인것이 가치주라고 msci에서 하고있음
        locals()['result_{}'.format(a)] =result_디스플레이[result_디스플레이['z_score'].notnull()]
        a=a+1
    
     #통신서비스 섹터
    if (np.sum(first_data['WICS_MID']=='통신서비스')>0)&(np.sum(sector_mom['CO_NM_x']=='통신서비스')==1):
        data_통신서비스 = first_data[first_data['WICS_MID']=="통신서비스"]
        # per, pbr, div_yield 구할때는 전체 시가총액을 사용,
        # 시총비중 구할떄는 free-float
        data_통신서비스['size_FIF_wisefn']=data_통신서비스['size_FIF_wisefn']/1000    #size 단위 thousand
        data_통신서비스['1/pbr']=data_통신서비스['EQUITY']/data_통신서비스['MARKET_CAP']
        data_통신서비스['1/per']=data_통신서비스['ADJ_NI_12M_FWD']/data_통신서비스['MARKET_CAP']
        data_통신서비스['div_yield']=data_통신서비스['CASH_DIV_COM']/data_통신서비스['MARKET_CAP']
        
        # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
        data_통신서비스 = data_통신서비스.replace([np.inf, -np.inf],np.nan)  
        
        # Null 값 제거
        data_통신서비스_per = data_통신서비스[data_통신서비스['1/per'].notnull()]
        data_통신서비스_pbr = data_통신서비스[data_통신서비스['1/pbr'].notnull()]
        data_통신서비스_div = data_통신서비스[data_통신서비스['div_yield'].notnull()]
    
    
        # 시가총액비중 구함 
        data_통신서비스_pbr_cap = np.sum(data_통신서비스_pbr['size_FIF_wisefn'])
        data_통신서비스_per_cap = np.sum(data_통신서비스_per['size_FIF_wisefn'])
        data_통신서비스_div_cap = np.sum(data_통신서비스_div['size_FIF_wisefn'])
    
        data_통신서비스_pbr = data_통신서비스_pbr.assign(market_weight=data_통신서비스_pbr['size_FIF_wisefn']/data_통신서비스_pbr_cap)
        data_통신서비스_per = data_통신서비스_per.assign(market_weight=data_통신서비스_per['size_FIF_wisefn']/data_통신서비스_per_cap)
        data_통신서비스_div = data_통신서비스_div.assign(market_weight=data_통신서비스_div['size_FIF_wisefn']/data_통신서비스_div_cap)
        
        # 시총가중 평균 
        mu_inv_pbr=np.sum(data_통신서비스_pbr['1/pbr']*data_통신서비스_pbr['market_weight'])
        mu_inv_per=np.sum(data_통신서비스_per['1/per']*data_통신서비스_per['market_weight'])
        mu_inv_div=np.sum(data_통신서비스_div['div_yield']*data_통신서비스_div['market_weight'])
        
        # 시총 가중 표준편자
        std_inv_pbr=np.sqrt(np.sum(np.square(data_통신서비스_pbr['1/pbr']-mu_inv_pbr)*data_통신서비스_pbr['market_weight']))
        std_inv_per=np.sqrt(np.sum(np.square(data_통신서비스_per['1/per']-mu_inv_per)*data_통신서비스_per['market_weight']))
        std_inv_div=np.sqrt(np.sum(np.square(data_통신서비스_div['div_yield']-mu_inv_div)*data_통신서비스_div['market_weight']))
        
        data_통신서비스1=(data_통신서비스_pbr['1/pbr']-mu_inv_pbr)/std_inv_pbr
        data_통신서비스1.name= 'pbr_z'
        data_통신서비스2=(data_통신서비스_per['1/per']-mu_inv_per)/std_inv_per
        data_통신서비스2.name= 'per_z'
        data_통신서비스3=(data_통신서비스_div['div_yield']-mu_inv_div)/std_inv_div
        data_통신서비스3.name= 'div_z'
              
        result_통신서비스 = pd.concat([data_통신서비스, data_통신서비스1, data_통신서비스2, data_통신서비스3], axis = 1)
        
        # np.nanmean : nan 값 포함해서 평균 내기!!
        result_통신서비스 = result_통신서비스.assign(z_score=np.nanmean(result_통신서비스.loc[:,['pbr_z','per_z','div_z']],axis=1))
    #    result_temp = result
    
        
        # z_score > 0 인것이 가치주라고 msci에서 하고있음
        locals()['result_{}'.format(a)] =result_통신서비스[result_통신서비스['z_score'].notnull()]
        a=a+1
    
     #유틸리티 섹터
    if (np.sum(first_data['WICS_MID']=='유틸리티')>0)&(np.sum(sector_mom['CO_NM_x']=='유틸리티')==1):
        data_유틸리티 = first_data[first_data['WICS_MID']=="유틸리티"]
        # per, pbr, div_yield 구할때는 전체 시가총액을 사용,
        # 시총비중 구할떄는 free-float
        data_유틸리티['size_FIF_wisefn']=data_유틸리티['size_FIF_wisefn']/1000    #size 단위 thousand
        data_유틸리티['1/pbr']=data_유틸리티['EQUITY']/data_유틸리티['MARKET_CAP']
        data_유틸리티['1/per']=data_유틸리티['ADJ_NI_12M_FWD']/data_유틸리티['MARKET_CAP']
        data_유틸리티['div_yield']=data_유틸리티['CASH_DIV_COM']/data_유틸리티['MARKET_CAP']
        
        # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
        data_유틸리티 = data_유틸리티.replace([np.inf, -np.inf],np.nan)  
        
        # Null 값 제거
        data_유틸리티_per = data_유틸리티[data_유틸리티['1/per'].notnull()]
        data_유틸리티_pbr = data_유틸리티[data_유틸리티['1/pbr'].notnull()]
        data_유틸리티_div = data_유틸리티[data_유틸리티['div_yield'].notnull()]
    
    
        # 시가총액비중 구함 
        data_유틸리티_pbr_cap = np.sum(data_유틸리티_pbr['size_FIF_wisefn'])
        data_유틸리티_per_cap = np.sum(data_유틸리티_per['size_FIF_wisefn'])
        data_유틸리티_div_cap = np.sum(data_유틸리티_div['size_FIF_wisefn'])
    
        data_유틸리티_pbr = data_유틸리티_pbr.assign(market_weight=data_유틸리티_pbr['size_FIF_wisefn']/data_유틸리티_pbr_cap)
        data_유틸리티_per = data_유틸리티_per.assign(market_weight=data_유틸리티_per['size_FIF_wisefn']/data_유틸리티_per_cap)
        data_유틸리티_div = data_유틸리티_div.assign(market_weight=data_유틸리티_div['size_FIF_wisefn']/data_유틸리티_div_cap)
        
        # 시총가중 평균 
        mu_inv_pbr=np.sum(data_유틸리티_pbr['1/pbr']*data_유틸리티_pbr['market_weight'])
        mu_inv_per=np.sum(data_유틸리티_per['1/per']*data_유틸리티_per['market_weight'])
        mu_inv_div=np.sum(data_유틸리티_div['div_yield']*data_유틸리티_div['market_weight'])
        
        # 시총 가중 표준편자
        std_inv_pbr=np.sqrt(np.sum(np.square(data_유틸리티_pbr['1/pbr']-mu_inv_pbr)*data_유틸리티_pbr['market_weight']))
        std_inv_per=np.sqrt(np.sum(np.square(data_유틸리티_per['1/per']-mu_inv_per)*data_유틸리티_per['market_weight']))
        std_inv_div=np.sqrt(np.sum(np.square(data_유틸리티_div['div_yield']-mu_inv_div)*data_유틸리티_div['market_weight']))
        
        data_유틸리티1=(data_유틸리티_pbr['1/pbr']-mu_inv_pbr)/std_inv_pbr
        data_유틸리티1.name= 'pbr_z'
        data_유틸리티2=(data_유틸리티_per['1/per']-mu_inv_per)/std_inv_per
        data_유틸리티2.name= 'per_z'
        data_유틸리티3=(data_유틸리티_div['div_yield']-mu_inv_div)/std_inv_div
        data_유틸리티3.name= 'div_z'
              
        result_유틸리티 = pd.concat([data_유틸리티, data_유틸리티1, data_유틸리티2, data_유틸리티3], axis = 1)
        
        # np.nanmean : nan 값 포함해서 평균 내기!!
        result_유틸리티 = result_유틸리티.assign(z_score=np.nanmean(result_유틸리티.loc[:,['pbr_z','per_z','div_z']],axis=1))
    #    result_temp = result
    
        
        # z_score > 0 인것이 가치주라고 msci에서 하고있음
        locals()['result_{}'.format(a)] =result_유틸리티[result_유틸리티['z_score'].notnull()]
        a=a+1
        
    for y in range(2,a):    
        result_1 = pd.concat([result_1,locals()['result_{}'.format(y)]],axis=0,join='inner')
   
    
    result = result_1
    result=result.assign(rnk=result['z_score'].rank(method='first',ascending=False)) 
    
    samsung['1/pbr'] = 0
    samsung['1/per'] = 0
    samsung['div_yield'] = 0
    samsung['pbr_z'] = 0
    samsung['per_z'] = 0
    samsung['div_z'] = 0
    samsung['z_score'] = 0
    samsung['rnk'] = 0
    
    result = pd.concat([result,samsung])
    #이게 위에 있었떠니 삼성전자 두번 들어가는것도... 으..
    #drop_duplicate()에서 subset='name'을 넣으면 name이 같은것들은 사라짐
    #여기서 default 값은 처음 하나는 살아남는다는것
    #삼성에서 이상한값에 다 0 을 넣어서 원래 값과 달랐기 때문에 subset 이없으면
    #제거가 안됬다.
    #keep='last'로 해야 rnk = 0인게 살아남음.....
    result = result.drop_duplicates(subset='CO_NM', keep='last')
    result = result[result['rnk']<50]
    
    sum_data = pd.merge(target_data,result,on='GICODE') # 3개월치 수익률을 구하기 위해 3개월 후 존재하는 data에 현재 data를 붙임
    sum_data['3M_RETURN'] = sum_data['ADJ_PRC_x']/sum_data['ADJ_PRC_y'] # 3개월동안의 종목 수익률
    
    #월별 수익률을 구해보
    first_data = first_data.loc[:,['TRD_DATE','GICODE','ADJ_PRC']]
    for i in range(past_month+1,cur_month): # 3개월치의 월별 수익률을 구하기 위해선 4개의 price 데이터가 필요한데 2개밖에 없으니 2개를 더 받아온다.
        second_data = raw_data[raw_data['TRD_DATE']==month_date.iloc[i,0]]  #월별 데이터를 받아와서
        second_data = second_data.loc[:,['TRD_DATE','GICODE','ADJ_PRC']]   # 간단하게 만든다음
        first_data = pd.merge(first_data,second_data,on='GICODE')   # first_data와 합친다
    
    first_data['1ST_RETURN'] =  first_data['ADJ_PRC_y']/ first_data['ADJ_PRC_x']   #0->1 , 즉 첫 한개월간의 수익률
    first_data['2ND_RETURN'] =  first_data['ADJ_PRC']/ first_data['ADJ_PRC_y']# 1->2 한달이후 한달간 수익률
    first_data = first_data.loc[:,['GICODE','1ST_RETURN','2ND_RETURN']] #데이터를 간단하게 만들어준다음
    sum_data = pd.merge(sum_data,first_data,on='GICODE') # 기존 data와 합친다.
    sum_data['2M_CUM_RETURN'] = sum_data['1ST_RETURN'] * sum_data['2ND_RETURN'] 
    
   
    
    quarter_data[[3*n,3*n+1,3*n+2]] = result.iloc[:,[0,1,7]].reset_index(drop=True)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    