import datetime
import utility
import tushare as ts
from index_peb import lxr_peb_analysis as peb

pro = ts.pro_api('602e5ad960d66ab8b1f3c13b4fd746f5323ff808b0820768b02c6da3')

df_params, _ = utility.read_params()


def t28_signal():
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(50)

    # 处理t28
    p_t28_UP_THRESHOLD = 0.5
    p_t28_DIFF_THRESHOLD = 1.0
    p_t28_PREV = 20

    t28_list = df_params.loc[df_params['strategy'] == 'Tendency28', 'index_code'].tolist()

    df1 = pro.index_daily(ts_code=utility.convert_code_2_tusharecode(t28_list[0]),
                          start_date=start_date.strftime('%Y%m%d'),
                          end_date=end_date.strftime('%Y%m%d'))
    up1 = (df1.iloc[0].close - df1.iloc[p_t28_PREV].close) / df1.iloc[p_t28_PREV].close * 100

    df2 = pro.index_daily(ts_code=utility.convert_code_2_tusharecode(t28_list[1]),
                          start_date=start_date.strftime('%Y%m%d'),
                          end_date=end_date.strftime('%Y%m%d'))
    up2 = (df2.iloc[0].close - df2.iloc[p_t28_PREV].close) / df2.iloc[p_t28_PREV].close * 100

    if up1 < p_t28_UP_THRESHOLD and up2 < p_t28_UP_THRESHOLD:
        print('Today is: %s, T28 operation is: 调仓至货币基金/债券' % datetime.date.today())

    elif up1 > p_t28_UP_THRESHOLD and up1 > up2:
        print('Today is: %s, T28 operation is: 调仓至%s' % (datetime.date.today(), df1.iloc[0].ts_code))

    elif up2 > p_t28_UP_THRESHOLD and up2 > up1:
        print('Today is: %s, T28 operation is: 调仓至%s' % (datetime.date.today(), df2.iloc[0].ts_code))

    print('%s up: %s; %s up: %s' % (
        utility.convert_code_2_tusharecode(t28_list[0]), up1, utility.convert_code_2_tusharecode(t28_list[1]), up2))


def inv_by_pe_pb_signal():
    holding_list = df_params.loc[df_params['is_holding'] == 'Y', 'index_code'].tolist()
    yesterday = datetime.date.today() - datetime.timedelta(1)
    p_inv_by_pe_pb_LOW_THRESHOLD = 0.2  # 买入估值条件阈值
    p_inv_by_pe_pb_HIGH_THRESHOLD = 0.85  # 卖出估值条件阈值
    field_param = 'pe_ttm_y10_median_cvpos'
    df = peb.get_indexes_mul_date_by_field(holding_list,
                                           start_date=(yesterday - datetime.timedelta(20)).strftime('%Y%m%d'),
                                           end_date=yesterday.strftime('%Y%m%d'),
                                           field=field_param).iloc[-1]
    df.index = [utility.get_name_from_ori_code(x) for x in df.index.values]
    print(df)


if __name__ == '__main__':
    inv_by_pe_pb_signal()
