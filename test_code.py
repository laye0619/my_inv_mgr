from abc import abstractmethod, ABCMeta

import utility as ut
import tushare as ts
import xalpha as xa
import matplotlib
import pandas as pd
import utility

# print(ut.DATA_ROOT)
# print(ut.REPORT_ROOT)
# print(ut.PARAMS_ROOT)
#
pro = ts.pro_api('602e5ad960d66ab8b1f3c13b4fd746f5323ff808b0820768b02c6da3')

# df = pd.DataFrame()
# seri = pd.Series(['aa', 'aaa', 'aaaa'])
# df['a'] = seri
# pass


df = pro.index_daily(ts_code='000807.SH')
df_1 = ts.pro_bar(ts_code='000807.SH', api=pro, asset='I', start_date='20180101', end_date='20181231')


pass