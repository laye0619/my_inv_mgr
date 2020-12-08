from abc import abstractmethod, ABCMeta

import utility as ut
import tushare as ts


# print(ut.DATA_ROOT)
# print(ut.REPORT_ROOT)
# print(ut.PARAMS_ROOT)
#
pro = ts.pro_api('602e5ad960d66ab8b1f3c13b4fd746f5323ff808b0820768b02c6da3')

df = pro.index_weight(index_code='399006.SZ', end_date='20201201')

print(df)
