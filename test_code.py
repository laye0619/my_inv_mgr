import utility as ut
import tushare as ts

print(ut.DATA_ROOT)
print(ut.REPORT_ROOT)
print(ut.PARAMS_ROOT)

pro = ts.pro_api('602e5ad960d66ab8b1f3c13b4fd746f5323ff808b0820768b02c6da3')

df = pro.index_daily(ts_code='399300.SZ', start_date='20180101', end_date='20201010')

print(df)




