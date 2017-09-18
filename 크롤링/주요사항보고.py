# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 13:32:47 2017

@author: SH-NoteBook
"""

import requests
from pandas.io.json import json_normalize
import json
import pandas as pd
import os
import re
import pandas as pd
import xlrd
import numpy as np

auth = '002090c5e2dbaa01213f95ec7c16903849765293'
target_date = '20170914'
url_tmpl = 'http://dart.fss.or.kr/api/search.json?auth={auth}&start_dt={target_date}&end_dt={target_date}&dsp_tp=B&page_set=500'
url = url_tmpl.format(auth=auth,target_date=target_date)
r = requests.get(url)
jo = json.loads(r.text)
result = json_normalize(jo, 'list')
#E 라는게 코스피랑 코스닥에 상장되지 않은 기업 
result = result[(result['crp_cls']!='E')].reset_index(drop=True)
result['web_address'] = 0
for i in range(len(result)):
    result.loc[i,'web_address'] = 'http://dart.fss.or.kr/dsaf001/main.do?rcpNo='+result.loc[i,'rcp_no']