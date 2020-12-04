import utility as ut
import tushare as ts

print(ut.DATA_ROOT)
print(ut.REPORT_ROOT)
print(ut.PARAMS_ROOT)

pro = ts.pro_api('602e5ad960d66ab8b1f3c13b4fd746f5323ff808b0820768b02c6da3')

df = pro.index_weight(index_code='000905.SH', start_date='20150101', end_date='20150331')

print(df)




