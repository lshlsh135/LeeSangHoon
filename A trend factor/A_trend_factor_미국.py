# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 21:33:25 2017

@author: LSH-I7-4790
"""

import pandas as pd
import cx_Oracle


#이거 두개 반드시 선언!
cx0=cx_Oracle.makedsn("localhost",1521,"xe")
connection = cx_Oracle.connect("lshlsh135","2tkdgns2",cx0)


#DATA를 가져온다!!
america_stock_return = pd.read_sql("""select * from america_stock_return""",con=connection)

aa=america_stock_return.head(388).loc[:,'TRD_DATE']
