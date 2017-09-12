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
        self.col_num = len(kospi_month)
        self.kospi_month = pd.DataFrame(kospi_month).transpose().reset_index(drop=True)
        self.diff_12m_monthly = pd.DataFrame(np.zeros((1,self.col_num-11)))
        
        
    def rolling_12month_return_3factor(self,i,j,z):
        self.factor_name = [i,j,z]
        for i in range(self.col_num-11):
            self.diff_12m_monthly.iloc[0,i]=np.prod(self.return_month_data_costed.iloc[0,i:i+12])-np.prod(self.kospi_month.iloc[1,i:i+12])
        
        ir_20010228 = 2*(np.mean(self.return_diff.iloc[0,:])-np.mean(self.kospi_quarter.transpose().iloc[1,:]))/np.std(self.return_diff.iloc[0,:]-self.kospi_quarter.transpose().iloc[1,:])        
        ir_20080228 = 2*(np.mean(self.return_diff.iloc[0,28:])-np.mean(self.kospi_quarter.transpose().iloc[1,28:]))/np.std(self.return_diff.iloc[0,28:]-self.kospi_quarter.transpose().iloc[1,28:])        
        self.factor_name = [self.factor_name, ir_20010228, ir_20080228]
        plt.figure(1)   
        plt.grid(True)
        plt.plot(self.diff_12m_monthly.iloc[0,84:].transpose())    
        plt.title(self.factor_name)
        return plt.show()
    
    def rolling_12month_return_4factor(self,i,j,z,p):
        self.factor_name = [i,j,z,p]
        for i in range(self.col_num-11):
            self.diff_12m_monthly.iloc[0,i]=np.prod(self.return_month_data_costed.iloc[0,i:i+12])-np.prod(self.kospi_month.iloc[1,i:i+12])
            
        ir_20010228 = 2*(np.mean(self.return_diff.iloc[0,:])-np.mean(self.kospi_quarter.transpose().iloc[1,:]))/np.std(self.return_diff.iloc[0,:]-self.kospi_quarter.transpose().iloc[1,:])        
        ir_20080228 = 2*(np.mean(self.return_diff.iloc[0,28:])-np.mean(self.kospi_quarter.transpose().iloc[1,28:]))/np.std(self.return_diff.iloc[0,28:]-self.kospi_quarter.transpose().iloc[1,28:])        
        self.factor_name = [self.factor_name, ir_20010228, ir_20080228]
        plt.figure(1)   
        plt.grid(True)
        plt.plot(self.diff_12m_monthly.iloc[0,84:].transpose())    
        plt.title(self.factor_name)
        return plt.show()
    
    def rolling_12month_return_5factor(self,i,j,z,p,k):
        self.factor_name = [i,j,z,p,k]
        for i in range(self.col_num-11):
            self.diff_12m_monthly.iloc[0,i]=np.prod(self.return_month_data_costed.iloc[0,i:i+12])-np.prod(self.kospi_month.iloc[1,i:i+12])
        
        ir_20010228 = 2*(np.mean(self.return_diff.iloc[0,:])-np.mean(self.kospi_quarter.transpose().iloc[1,:]))/np.std(self.return_diff.iloc[0,:]-self.kospi_quarter.transpose().iloc[1,:])        
        ir_20080228 = 2*(np.mean(self.return_diff.iloc[0,28:])-np.mean(self.kospi_quarter.transpose().iloc[1,28:]))/np.std(self.return_diff.iloc[0,28:]-self.kospi_quarter.transpose().iloc[1,28:])        
        self.factor_name = [self.factor_name, ir_20010228, ir_20080228]
        plt.figure(1)   
        plt.grid(True)
        plt.plot(self.diff_12m_monthly.iloc[0,84:].transpose())    
        plt.title(self.factor_name)
        return plt.show()
    