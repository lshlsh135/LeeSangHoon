# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 15:35:00 2017

@author: SH-NoteBook
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt




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
        
        ir_20010228 = round(2*(np.mean(return_diff.iloc[0,:])-np.mean(kospi_quarter.transpose().iloc[1,:]))/np.std(return_diff.iloc[0,:]-kospi_quarter.transpose().iloc[1,:]),2)        
        ir_20080228 = round(2*(np.mean(return_diff.iloc[0,28:])-np.mean(kospi_quarter.transpose().iloc[1,28:]))/np.std(return_diff.iloc[0,28:]-kospi_quarter.transpose().iloc[1,28:]),2)        
        winrate_20080228=round((np.cumsum(diff_12m_monthly.iloc[0,84:]>0)/len(diff_12m_monthly.iloc[0,84:])).loc[len(diff_12m_monthly.columns)-1],3)
        winrate_20010228=round((np.cumsum(diff_12m_monthly.iloc[0,:]>0)/len(diff_12m_monthly.iloc[0,:])).loc[len(diff_12m_monthly.columns)-1],3)
        
        title_20010228 = [factor_name, 'ir_20010228='+str(ir_20010228), 'winrate_20010228='+str(winrate_20010228)  ]
        title_20080228 = [factor_name, 'ir_20080228='+str(ir_20080228), 'winrate_20080228='+str(winrate_20080228)  ]
        
        plt.figure(1)           
        plt.subplot(211)
        plt.plot(diff_12m_monthly.iloc[0,84:].transpose())   
        plt.grid(True)
        plt.title(title_20080228)
        plt.subplot(212)
        plt.plot(diff_12m_monthly.transpose())    
        plt.grid(True)
        plt.title(title_20010228)
        plt.tight_layout()  # 아랫 그림의 제목과 윗 그림의 x축이 겹치는걸 방지해
        factor_name = [factor_name, 'ir_20010228='+str(ir_20010228), 'ir_20080228='+str(ir_20080228), 'winrate_20080228='+str(winrate_20080228),'winrate_20010228='+str(winrate_20010228)]
        plt.savefig(str(factor_name)+'.jpg')
        return plt.show()
    
    def rolling_12month_return_4factor(self,i,j,z,p):
        factor_name = [i,j,z,p]
        for i in range(col_num-11):
            diff_12m_monthly.iloc[0,i]=np.prod(return_month_data_costed.iloc[0,i:i+12])-np.prod(kospi_month.iloc[1,i:i+12])
            
        ir_20010228 = round(2*(np.mean(return_diff.iloc[0,:])-np.mean(kospi_quarter.transpose().iloc[1,:]))/np.std(return_diff.iloc[0,:]-kospi_quarter.transpose().iloc[1,:]),2)        
        ir_20080228 = round(2*(np.mean(return_diff.iloc[0,28:])-np.mean(kospi_quarter.transpose().iloc[1,28:]))/np.std(return_diff.iloc[0,28:]-kospi_quarter.transpose().iloc[1,28:]),2)        
        winrate_20080228=round((np.cumsum(diff_12m_monthly.iloc[0,84:]>0)/len(diff_12m_monthly.iloc[0,84:])).loc[len(diff_12m_monthly.columns)-1],3)
        winrate_20010228=round((np.cumsum(diff_12m_monthly.iloc[0,:]>0)/len(diff_12m_monthly.iloc[0,:])).loc[len(diff_12m_monthly.columns)-1],3)
        
        title_20010228 = [factor_name, 'ir_20010228='+str(ir_20010228), 'winrate_20010228='+str(winrate_20010228)  ]
        title_20080228 = [factor_name, 'ir_20080228='+str(ir_20080228), 'winrate_20080228='+str(winrate_20080228)  ]
        
        plt.figure(1)           
        plt.subplot(211)
        plt.plot(diff_12m_monthly.iloc[0,84:].transpose())   
        plt.grid(True)
        plt.title(title_20080228)
        plt.subplot(212)
        plt.plot(diff_12m_monthly.transpose())    
        plt.grid(True)
        plt.title(title_20010228)
        plt.tight_layout()  # 아랫 그림의 제목과 윗 그림의 x축이 겹치는걸 방지해
        factor_name = [factor_name, 'ir_20010228='+str(ir_20010228), 'ir_20080228='+str(ir_20080228), 'winrate_20080228='+str(winrate_20080228),'winrate_20010228='+str(winrate_20010228)]
        plt.savefig(str(factor_name)+'.jpg')
        return plt.show()
    
    def rolling_12month_return_5factor(self,i,j,z,p,k):
        factor_name = [i,j,z,p,k]
        for i in range(col_num-11):
            diff_12m_monthly.iloc[0,i]=np.prod(return_month_data_costed.iloc[0,i:i+12])-np.prod(kospi_month.iloc[1,i:i+12])
        
        ir_20010228 = round(2*(np.mean(return_diff.iloc[0,:])-np.mean(kospi_quarter.transpose().iloc[1,:]))/np.std(return_diff.iloc[0,:]-kospi_quarter.transpose().iloc[1,:]),2)        
        ir_20080228 = round(2*(np.mean(return_diff.iloc[0,28:])-np.mean(kospi_quarter.transpose().iloc[1,28:]))/np.std(return_diff.iloc[0,28:]-kospi_quarter.transpose().iloc[1,28:]),2)        
        winrate_20080228=round((np.cumsum(diff_12m_monthly.iloc[0,84:]>0)/len(diff_12m_monthly.iloc[0,84:])).loc[len(diff_12m_monthly.columns)-1],3)
        winrate_20010228=round((np.cumsum(diff_12m_monthly.iloc[0,:]>0)/len(diff_12m_monthly.iloc[0,:])).loc[len(diff_12m_monthly.columns)-1],3)
        
        title_20010228 = [factor_name, 'ir_20010228='+str(ir_20010228), 'winrate_20010228='+str(winrate_20010228)  ]
        title_20080228 = [factor_name, 'ir_20080228='+str(ir_20080228), 'winrate_20080228='+str(winrate_20080228)  ]
        
        plt.figure(1)           
        plt.subplot(211)
        plt.plot(diff_12m_monthly.iloc[0,84:].transpose())   
        plt.grid(True)
        plt.title(title_20080228)
        plt.subplot(212)
        plt.plot(diff_12m_monthly.transpose())    
        plt.grid(True)
        plt.title(title_20010228)
        plt.tight_layout()  # 아랫 그림의 제목과 윗 그림의 x축이 겹치는걸 방지해
        factor_name = [factor_name, 'ir_20010228='+str(ir_20010228), 'ir_20080228='+str(ir_20080228), 'winrate_20080228='+str(winrate_20080228),'winrate_20010228='+str(winrate_20010228)]
        plt.savefig(str(factor_name)+'.jpg')
        return plt.show()
    
    