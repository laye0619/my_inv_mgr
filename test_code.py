from abc import abstractmethod, ABCMeta

import utility as ut
import tushare as ts
import xalpha as xa
import matplotlib
import pandas as pd
import utility
from pyecharts.charts import Line
import index_peb.lxr_peb_analysis as lxr_peb_analysis

# print(ut.DATA_ROOT)
# print(ut.REPORT_ROOT)
# print(ut.PARAMS_ROOT)

# pro = ts.pro_api('602e5ad960d66ab8b1f3c13b4fd746f5323ff808b0820768b02c6da3')

# f = pro.daily(ts_code='512980.SH', start_date='20190301', end_date='20190331')
# f = ts.pro_bar(ts_code='512980.SH', api=pro, asset='FD', adj='qfq', start_date='20190320', end_date='20190331')

# f = xa.fundinfo('159915')

# fond_list = ['006585',
#              '006060',
#              '008127',
#              '485011',
#              '001406']
#
# for fond in fond_list:
#     fond_info = xa.fundinfo(fond)
#     print(fond_info.name)

df = pd.read_excel('01_params/Inv_Asset_Record.xlsx', sheet_name='E_TransRecord')
pass