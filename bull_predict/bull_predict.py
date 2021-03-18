from datetime import date, timedelta

import xalpha as xa
import pandas as pd
import tushare as ts

'''
市场热度判断不同方法
'''


def turnover_rate(ts_pro):
    yesterday = date.today() - timedelta(1)
    df_sample = ts_pro.index_dailybasic(trade_date=yesterday.strftime("%Y%m%d"),
                                        fields='ts_code,trade_date,turnover_rate_f')
    code_list = df_sample['ts_code'].tolist()
    code_info_basic = ts_pro.index_dailybasic(
        ts_code='000001.SH',
        fields='ts_code,trade_date,turnover_rate_f'
    )
    result_df = code_info_basic[['trade_date', 'turnover_rate_f']]
    result_df.rename(columns={'turnover_rate_f': '000001.SH'}, inplace=True)
    code_list.remove('000001.SH')

    for code in code_list:
        code_info = ts_pro.index_dailybasic(ts_code=code, fields='trade_date,turnover_rate_f')
        if len(code_info) > 0:
            result_df = pd.merge(
                result_df,
                code_info.loc[:, ['trade_date', 'turnover_rate_f']],
                how='left',
                on='trade_date'
            )
            result_df.rename(columns={'turnover_rate_f': code}, inplace=True)
    result_df['turnover_rate_f_median'] = result_df.median(axis=1, skipna=True)
    result_df['turnover_rate_f_mean'] = result_df.mean(axis=1, skipna=True)
    return result_df.sort_values(by='trade_date', ascending=True).reset_index(drop=True)


if __name__ == '__main__':
    ts_pro = ts.pro_api('602e5ad960d66ab8b1f3c13b4fd746f5323ff808b0820768b02c6da3')
    turnover_rate(ts_pro)
    pass
