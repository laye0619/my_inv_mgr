from datetime import date, timedelta

import pandas as pd
import utility
import matplotlib.pyplot as plt
import matplotlib as mpl
import tushare as ts
import xalpha as xa
import datetime

mpl.use('TkAgg')
mpl.rcParams[u'font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False


def get_index_peb_percentile(index_code, date_str, period='fs'):
    '''
    某日某指数peb百分比情况
    :param period: fs or y10 or y5
    :param index_code:
    :param date_str:
    :return:
    '''
    column_param = ['avgv', 'cv', 'cvpos', 'maxpv', 'maxv', 'minv', 'q2v', 'q5v', 'q8v']
    row_param = ['pe_ttm_%s_avg_' % period, 'pe_ttm_%s_ewpvo_' % period, 'pe_ttm_%s_ew_' % period,
                 'pe_ttm_%s_median_' % period, 'pe_ttm_%s_mcw_' % period,
                 'pb_%s_avg_' % period, 'pb_%s_ewpvo_' % period, 'pb_%s_ew_' % period, 'pb_%s_median_' % period,
                 'pb_%s_mcw_' % period]
    result_df = pd.DataFrame([], columns=column_param)
    for row in row_param:
        row_df = get_indexes_peb_fields_by_date([index_code], date_str=date_str,
                                                field_list=[row + col_str for col_str in column_param])
        if len(row_df) > 0:
            row_df.columns = column_param
            result_df = result_df.append(row_df.iloc[0])
        result_df.rename(index={index_code: row}, inplace=True)
    result_df = result_df.applymap(__ffloat)

    # 改行名和列名
    result_df.columns = ['平均值', '当前值', '当前分位点', '最大正值', '最大值', '最小值', '20%分位点', '50%分位点', '80%分位点']
    result_df.index = ['PE平均值法', 'PE正数等权', 'PE等权', 'PE中位数', 'PE加权法', 'PB平均值法', 'PB正数等权', 'PB等权', 'PB中位数', 'PB加权法']
    return result_df


def plot_index_peb_percentile(index_code, start_date=None, end_date=None, method_list=None, peb='pe'):
    if method_list is None:
        method_list = ['ewpvo', 'mcw', 'avg', 'ew', 'median']
    p_peb = 'pe_ttm' if peb == 'pe' else 'pb'
    field_list = []
    for method in method_list:
        field_list.append('%s_y10_%s_cvpos' % (p_peb, method))
    df = get_mul_date_peb_fields_by_index(index_code, start_date=start_date, end_date=end_date, field_list=field_list)
    df.rename(columns={'pe_ttm_y10_ewpvo_cvpos': '正数等权',
                       'pe_ttm_y10_mcw_cvpos': '市值加权',
                       'pe_ttm_y10_avg_cvpos': '平均数',
                       'pe_ttm_y10_ew_cvpos': '等权',
                       'pe_ttm_y10_median_cvpos': '中位数'}, inplace=True)
    df.plot(rot=45, grid=True)
    plt.title('Index Percentile - %s' % utility.get_name_from_ori_code(index_code))
    plt.show()


def plot_index_peb_bin(index_code, start_date=None, end_date=None, method='ewpvo', peb='pe', interval=20):
    if peb == 'pe':
        field = 'pe_ttm_' + method
    elif peb == 'pb':
        field = 'pb_' + method
    df = get_indexes_mul_date_by_field([index_code], start_date=start_date, end_date=end_date, field=field)

    df_desc = df.describe()
    bins = []
    pe_max = df_desc.loc['max', index_code]
    pe_min = df_desc.loc['min', index_code]
    sub_max_min = pe_max - pe_min
    for i in range(interval):
        increment = i * (1 / interval)
        bins.append(__ffloat(sub_max_min * increment + pe_min))
    bins.append(pe_max)
    score_cat = pd.cut(df[index_code], bins)
    pe_bin = pd.value_counts(score_cat)
    pe_bin = pe_bin.sort_index()
    pe_bin.plot(kind='bar', rot=75)
    plt.title('%s BIns - %s - Today is %.2f' % (
        utility.get_name_from_ori_code(df.columns[0]), utility.get_cn_desc_from_index_peb_field(field), df.iloc[-1, 0]))
    plt.show()
    pass


def plot_index_peb_hist(index_code, start_date=None, end_date=None, method='ewpvo', peb='pe'):
    '''
    单个指数的hist图 - 指定peb的计算方法
    :param index_code:
    :param start_date:
    :param end_date:
    :param method:
    :param peb:
    :return:
    '''
    if peb == 'pe':
        field = 'pe_ttm_' + method
    elif peb == 'pb':
        field = 'pb_' + method
    df = get_indexes_mul_date_by_field([index_code], start_date=start_date, end_date=end_date, field=field)

    df.hist(column=df.columns[0], bins=round(df.count()[0] / 8))
    plt.title('%s Histogram - %s - Today is %.2f' % (
        utility.get_name_from_ori_code(df.columns[0]), utility.get_cn_desc_from_index_peb_field(field), df.iloc[-1, 0]))
    plt.show()
    pass


def plot_indexes_peb_with_given_method(index_list, start_date=None, end_date=None, method='ewpvo', peb='pe'):
    '''
    不同指数的同一种peb方法作图比较
    :param index_list:
    :param start_date:
    :param end_date:
    :param method:
    :param peb:
    :return:
    '''
    if peb == 'pe':
        field = 'pe_ttm_' + method
    elif peb == 'pb':
        field = 'pb_' + method
    df = get_indexes_mul_date_by_field(index_list, start_date=start_date, end_date=end_date, field=field)
    for col_name in df.columns:
        df.rename(columns={col_name: utility.get_name_from_ori_code(col_name)}, inplace=True)

    df.plot(rot=45, grid=True)
    plt.title('Index %s' % utility.get_cn_desc_from_index_peb_field(field))
    plt.show()


def plot_single_index_peb_with_mul_method(index_code, start_date=None, end_date=None, method=None, peb='pe'):
    '''
    给定的指数不同的peb方法作图比较
    :param end_date:
    :param start_date:
    :param peb:
    :param index_code: 
    :param date: 
    :param method: 
    :return: 
    '''
    if method is None:
        method = ['ew', 'ewpvo', 'mcw', 'median', 'avg']
    if peb == 'pe':
        field_list = ['pe_ttm_' + field for field in method]
    elif peb == 'pb':
        field_list = ['pb_' + field for field in method]
    df = get_mul_date_peb_fields_by_index(start_date=start_date, end_date=end_date, index_code=index_code,
                                          field_list=field_list)

    for col_name in df.columns:
        df.rename(columns={col_name: utility.get_cn_desc_from_index_peb_field(col_name)}, inplace=True)

    df.plot(rot=45, grid=True)
    plt.title('Index %s - %s ' % (index_code, utility.get_name_from_ori_code(index_code)))
    plt.show()


def get_indexes_peb_fields_by_date(index_list, date_str, field_list=None):
    result_df = pd.DataFrame()
    for index_code in index_list:
        df = __read_peb_file(index_code, field_list)
        df['date'] = pd.to_datetime(df['date'])

        df = df.loc[df['date'] <= pd.to_datetime(date_str)]
        if len(df) > 0:
            seri = df.iloc[-1]
            seri.name = index_code
            result_df = result_df.append(seri)
    del result_df['date']
    return result_df


def get_mul_date_peb_fields_by_index(index_code, start_date=None, end_date=None, field_list=None):
    df = __read_peb_file(index_code, field_list)
    df['date'] = pd.to_datetime(df['date'])
    if start_date is not None:
        df = df.loc[df['date'] >= pd.to_datetime(start_date)]
    if end_date is not None:
        df = df.loc[df['date'] <= pd.to_datetime(end_date)]
    df.index = df['date']
    del df['date']
    return df


def get_indexes_mul_date_by_field(index_list, field, start_date=None, end_date=None):
    fired = False
    result_df = __read_peb_file(index_list[0], [field])
    result_df.index = pd.to_datetime(result_df['date'])
    del result_df['date']
    del result_df[field]
    for index_code in index_list:
        df = __read_peb_file(index_code, [field])
        df['date'] = pd.to_datetime(df['date'])
        if start_date is not None:
            df = df.loc[df['date'] >= pd.to_datetime(start_date)]
        if end_date is not None:
            df = df.loc[df['date'] <= pd.to_datetime(end_date)]
        df.index = df['date']
        if len(df) > 0:
            result_df[index_code] = df[field]
    return result_df.dropna(how='all')


def __read_peb_file(index_code, field_list=None):
    file_path = '%s/index_peb/%s_peb.csv' % (
        utility.DATA_ROOT, utility.convert_code_2_csvfilename(index_code))
    df = pd.read_csv(file_path)

    if field_list is None:
        return df
    else:
        if 'date' not in field_list:
            field_list.append('date')
        return df[field_list]


def cal_index_corr(index_list, period=10):
    end_date = date.today() - timedelta(1)
    start_date = end_date - timedelta(period * 365)
    pro = ts.pro_api('602e5ad960d66ab8b1f3c13b4fd746f5323ff808b0820768b02c6da3')
    trade_cal = pro.trade_cal(exchange='', start_date=start_date.strftime('%Y%m%d'),
                              end_date=end_date.strftime('%Y%m%d'), is_open=1).cal_date
    result_df = pd.DataFrame(index=trade_cal)
    for code in index_list:
        df_temp = xa.indexinfo(utility.convert_code_2_xalphacode(code)).price
        df_temp = df_temp[df_temp['date'] >= start_date.strftime('%Y-%m-%d')]
        df_temp = df_temp[df_temp['date'] <= end_date.strftime('%Y-%m-%d')]
        df_temp.index = df_temp['date']
        df_temp.index = pd.to_datetime(df_temp.index).strftime('%Y%m%d')
        df_temp = df_temp['totvalue']
        result_df[code] = df_temp
    result_df.dropna(how='all', inplace=True)
    result_df.columns = [utility.get_name_from_ori_code(c) for c in result_df.columns.values]
    result_df = result_df.corr()
    return result_df


def __ffloat(data_in):
    return float('%.2f' % data_in)


if __name__ == '__main__':
    index_list, _ = utility.read_params()
    index_list = index_list['index_code'].drop_duplicates().tolist()

    # plot_indexes_peb_with_given_method(index_list=index_list,
    #                                    start_date='20120101',
    #                                    end_date=None,
    #                                    method='median',
    #                                    peb='pe')

    # plot_single_index_peb_with_mul_method('000905')

    # plot_index_peb_hist('000905', start_date=None, end_date=None, method='mcw', peb='pb')

    # plot_index_peb_bin('000905', start_date=None, end_date=None, method='ewpvo', peb='pe', interval=30)

    # result = get_index_peb_percentile('000905', date_str='20201211', period='y10')

    # corr_df = cal_index_corr(index_list)

    plot_index_peb_percentile('000905', start_date='20130101', end_date='20201201',
                              method_list=['ewpvo'])
    pass
