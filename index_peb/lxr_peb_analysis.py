import pandas as pd
import utility
import matplotlib.pyplot as plt

index_code = '000905'

file_path = data_path = '%s/index_peb/%s_peb.csv' % (
            utility.DATA_ROOT, utility.convert_code_2_csvfilename(index_code))
df = pd.read_csv(file_path)

# df_pe = df[['date', 'pe_ttm_avg', 'pe_ttm_ew', 'pe_ttm_ewpvo', 'pe_ttm_mcw', 'pe_ttm_median']]
df_pe = df[['date', 'pe_ttm_ew']]

df_pe.index = df_pe['date']
df_pe.index = pd.to_datetime(df_pe.index)

df_pe.plot(rot=45, grid=True)
plt.show()