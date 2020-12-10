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
# pro = ts.pro_api('602e5ad960d66ab8b1f3c13b4fd746f5323ff808b0820768b02c6da3')


index_codes, _ = utility.read_params()
index_codes = index_codes['index_code'].drop_duplicates()
# index_codes = index_codes.replace('000001', '1000004')
# index_codes = index_codes.replace('000985', '1000002')
for index_code in index_codes:
    data_path = '%s/index_peb/%s_peb.csv' % (utility.DATA_ROOT, utility.convert_code_2_csvfilename(index_code))
    df = pd.read_csv(data_path, parse_dates=True)
    df = df.sort_values(by=['date'], ignore_index=True)
    df.to_csv(data_path, index=False)
    pass
