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
        kospi_month = pd.DataFrame(kospi_month).transpose().reset_index(drop=True)
        col_num = len(kospi_month)
        diff_12m_monthly = pd.DataFrame(np.zeros((1,col_num-11)))
        
    def rolling_12month_return(self):
        for i in range(col_num-11):
            diff_12m_monthly.iloc[0,i]=np.prod(return_month_data_costed.iloc[0,i:i+12])-np.prod(kospi_month.iloc[0,i:i+12])


cur_mom_row=month_date.loc[month_date['MONTH_DATE']==rebalancing_date.iloc[n,0]].index[0]
            
diff_12m_monthly.iloc[0,82:].transpose().plot(grid=True)
