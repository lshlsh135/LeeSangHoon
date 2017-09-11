# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 15:35:00 2017

@author: SH-NoteBook
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class return_calculator:
 
    def __init__(self,return_diff,return_month_data_costed,kospi_quarter,kospi_month):
        self.return_diff = return_diff
        self.return_month_data_costed = return_month_data_costed
        self.kospi_quarter = kospi_quarter
        self.kospi_month = pd.DataFrame(kospi_month).transpose().reset_index(drop=True)
        self.col_num = len(kospi_month)
        self.diff_12m_monthly = pd.DataFrame(np.zeros((1,self.col_num-11)))
        
        
    def rolling_12month_return(self):
        for i in range(self.col_num-11):
            self.diff_12m_monthly.iloc[0,i]=np.prod(self.return_month_data_costed.iloc[0,i:i+12])-np.prod(self.kospi_month.iloc[0,i:i+12])

       