# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 08:13:34 2017

@author: SH-NoteBook
"""
import numpy as np
import pandas as pd


class return_calculator:
 
    def __init__(self,return_diff,return_month_data_costed,kospi_quarter,kospi_month):
        return_diff = return_diff
        return_month_data_costed = return_month_data_costed
        kospi_quarter = kospi_quarter
        col_num = len(kospi_month)
        kospi_month = pd.DataFrame(kospi_month).transpose().reset_index(drop=True)
        diff_12m_monthly = pd.DataFrame(np.zeros((1,col_num-11)))
        
        
    def rolling_12month_return_3factor(self,i,j,z):
        factor_name = [i,j,z]
        for i in range(col_num-11):
            diff_12m_monthly.iloc[0,i]=np.prod(return_month_data_costed.iloc[0,i:i+12])-np.prod(kospi_month.iloc[1,i:i+12])

        return diff_12m_monthly.iloc[0,84:].transpose().plot(grid=True).set_title(factor_name) #82번째부터가 2008년 2월말부터 투자한것  

 2*(np.mean(locals()['aaa_{}{}{}{}{}'.format(i,j,z,p,k)][1].iloc[0,28:])-np.mean(kospi_quarter.transpose().iloc[1,28:]))/np.std(locals()['aaa_{}{}{}{}{}'.format(i,j,z,p,k)][1].iloc[0,28:]-kospi_quarter.transpose().iloc[1,28:])        
    
    

