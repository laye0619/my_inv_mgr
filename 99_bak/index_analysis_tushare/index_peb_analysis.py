from datetime import timedelta

import pandas as pd
import utility
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.rcParams[u'font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False
mpl.use('TkAgg')


def build_historical_price(idx_list):
    first_time = True
    df_price = pd.DataFrame()
    first_time = True
    price_column_str = 'price'
    for idx in idx_list:
        df = pd.read_csv('%s/index_pe_pb/%s_pe_pb.csv' % (
            utility.DATA_ROOT, utility.convert_code_2_csvfilename(utility.back_2_original_code(idx))), index_col=0)
        df.index.name = 'DATE'
        if first_time:
            df_price = df[[price_column_str]]
            df_price.rename(columns={price_column_str: idx}, inplace=True)
            first_time = False
        else:
            df_price = pd.concat([df_price, df[[price_column_str]]], axis=1)
            df_price.rename(columns={price_column_str: idx}, inplace=True)
    return df_price


# cal_method = 1: 整体法，市值加权
# cal_method = 2: 等权，亏损置零
# cal_method = 3: 中位数，无需预处理
# cal_method = 4: 算数平均，取分位数95%置信区间
# Be default, cal_method = None: get all of the method
def build_historical_pe(idx_list, cal_method=None):
    first_time = True
    df_pe = pd.DataFrame()
    first_time = True
    pe_column_str = ''
    pe_name = ''

    if cal_method is None:
        for idx in idx_list:
            df = pd.read_csv('%s/index_pe_pb/%s_pe_pb.csv' % (
                utility.DATA_ROOT, utility.convert_code_2_csvfilename(utility.back_2_original_code(idx))), index_col=0)
            df.index.name = 'DATE'
            idx_name = utility.get_name_from_ori_code(utility.back_2_original_code(idx))
            if first_time:
                df_pe = df[['pe1', 'pe2', 'pe3', 'pe4']]
                df_pe.rename(columns={'pe1': idx_name + ' - 加权',
                                      'pe2': idx_name + ' - 等权',
                                      'pe3': idx_name + ' - 中位数',
                                      'pe4': idx_name + ' - 平均'}, inplace=True)
                first_time = False
            else:
                df_pe = pd.concat([df_pe, df[['pe1', 'pe2', 'pe3', 'pe4']]], axis=1)
                df_pe.rename(columns={'pe1': idx_name + ' - 加权',
                                      'pe2': idx_name + ' - 等权',
                                      'pe3': idx_name + ' - 中位数',
                                      'pe4': idx_name + ' - 平均'}, inplace=True)
        return df_pe

    if cal_method == 1:
        pe_column_str = 'pe1'
        pe_name = '加权'
    elif cal_method == 2:
        pe_column_str = 'pe2'
        pe_name = '等权'
    elif cal_method == 3:
        pe_column_str = 'pe3'
        pe_name = '中位数'
    elif cal_method == 4:
        pe_column_str = 'pe4'
        pe_name = '平均'

    for idx in idx_list:
        df = pd.read_csv('%s/index_pe_pb/%s_pe_pb.csv' % (
            utility.DATA_ROOT, utility.convert_code_2_csvfilename(utility.back_2_original_code(idx))), index_col=0)
        df.index.name = 'DATE'
        if first_time:
            df_pe = df[[pe_column_str]]
            df_pe.rename(columns={pe_column_str: idx}, inplace=True)
            first_time = False
        else:
            df_pe = pd.concat([df_pe, df[[pe_column_str]]], axis=1)
            df_pe.rename(columns={pe_column_str: idx}, inplace=True)

    return df_pe


# cal_method = 1: 整体法，市值加权
# cal_method = 2: 等权，亏损置零
# cal_method = 3: 中位数，无需预处理
# cal_method = 4: 算数平均，取分位数95%置信区间
# Be default, cal_method = None: get all of the method
def build_historical_pb(idx_list, cal_method=None):
    df_pb = pd.DataFrame()
    first_time = True
    pb_column_str = ''
    pb_name = ''

    if cal_method is None:
        for idx in idx_list:
            df = pd.read_csv('%s/index_pe_pb/%s_pe_pb.csv' % (
                utility.DATA_ROOT, utility.convert_code_2_csvfilename(utility.back_2_original_code(idx))), index_col=0)
            df.index.name = 'DATE'
            idx_name = utility.get_name_from_ori_code(utility.back_2_original_code(idx))
            if first_time:
                df_pb = df[['pb1', 'pb2', 'pb3', 'pb4']]
                df_pb.rename(columns={'pb1': idx_name + ' - 加权',
                                      'pb2': idx_name + ' - 等权',
                                      'pb3': idx_name + ' - 中位数',
                                      'pb4': idx_name + ' - 平均'}, inplace=True)
                first_time = False
            else:
                df_pb = pd.concat([df_pb, df[['pb1', 'pb2', 'pb3', 'pb4']]], axis=1)
                df_pb.rename(columns={'pb1': idx_name + ' - 加权',
                                      'pb2': idx_name + ' - 等权',
                                      'pb3': idx_name + ' - 中位数',
                                      'pb4': idx_name + ' - 平均'}, inplace=True)
        return df_pb

    if cal_method == 1:
        pb_column_str = 'pb1'
        pb_name = '加权'
    elif cal_method == 2:
        pb_column_str = 'pb2'
        pb_name = '等权'
    elif cal_method == 3:
        pb_column_str = 'pb3'
        pb_name = '中位数'
    elif cal_method == 4:
        pb_column_str = 'pb4'
        pb_name = '平均'

    for idx in idx_list:
        df = pd.read_csv('%s/index_pe_pb/%s_pe_pb.csv' % (
            utility.DATA_ROOT, utility.convert_code_2_csvfilename(utility.back_2_original_code(idx))), index_col=0)
        df.index.name = 'DATE'
        if first_time:
            df_pb = df[[pb_column_str]]
            df_pb.rename(columns={pb_column_str: idx}, inplace=True)
            first_time = False
        else:
            df_pb = pd.concat([df_pb, df[[pb_column_str]]], axis=1)
            df_pb.rename(columns={pb_column_str: idx}, inplace=True)

    return df_pb


# four selling point in total. 95% PE as the first - selling 1/4; 98% PE as the second - selling 1/4;
# MAX PE as the third - selling 1/4
def daily_pe_pb_report(idx_list, cal_method=2, date_str=None):
    df_pe = build_historical_pe(idx_list, cal_method)
    df_pb = build_historical_pb(idx_list, cal_method)
    df_pe.index = pd.to_datetime(df_pe.index, format="%Y%m%d")
    df_pb.index = pd.to_datetime(df_pb.index, format="%Y%m%d")
    if date_str is None:
        df_pe = df_pe[df_pe.iloc[-1].name.date() - timedelta(365 * 10):]  # 最长十年的数据
        df_pb = df_pb[df_pb.iloc[-1].name.date() - timedelta(365 * 10):]  # 最长十年的数据
    else:
        df_pe = df_pe[df_pe.loc[pd.to_datetime(date_str)].name.date() - timedelta(365 * 10):df_pe.loc[
            pd.to_datetime(date_str)].name.date()]  # 最长十年的数据
        df_pb = df_pb[df_pb.loc[pd.to_datetime(date_str)].name.date() - timedelta(365 * 10):df_pb.loc[
            pd.to_datetime(date_str)].name.date()]  # 最长十年的数据
    df_pe_desc = df_pe.describe(percentiles=[.1, .25, .5, .75, .9, .95, .98])
    df_pb_desc = df_pb.describe(percentiles=[.1, .25, .5, .75, .9, .95, .98])
    pe_results = []
    pe_code_list = []

    for code in idx_list:
        pe_ratio = round(
            len(df_pe[code][df_pe[code] < df_pe.iloc[-1][code]]) / float(len(df_pe[code].dropna())) * 100,
            2)
        pb_ratio = round(
            len(df_pb[code][df_pb[code] < df_pb.iloc[-1][code]]) / float(len(df_pb[code].dropna())) * 100,
            2)
        pe_results.append([utility.get_name_from_ori_code(utility.back_2_original_code(code)),  # 名称
                           float(__ffloat(df_pe.iloc[-1][code])),  # 市盈率
                           pe_ratio,  # 百分位
                           __ffloat(df_pe_desc.loc['min', code]),  # PE MIN
                           __ffloat(df_pe_desc.loc['10%', code]),  # PE 10%
                           __ffloat(df_pe_desc.loc['25%', code]),  # PE 25%
                           __ffloat(df_pe_desc.loc['50%', code]),  # PE 50%
                           __ffloat(df_pe_desc.loc['75%', code]),  # PE 75%
                           __ffloat(df_pe_desc.loc['90%', code]),  # PE 90%
                           __ffloat(df_pe_desc.loc['95%', code]),  # PE 95% sell 1/4
                           __ffloat(df_pe_desc.loc['98%', code]),  # PE 98% sell 1/3
                           __ffloat(df_pe_desc.loc['max', code]),  # PE MAX sell 1/2
                           __ffloat(df_pb.iloc[-1][code]),  # 市净率
                           pb_ratio,  # PB百分位
                           __ffloat(df_pb_desc.loc['min', code]),  # PB MIN
                           __ffloat(df_pb_desc.loc['10%', code]),  # PB 10%
                           __ffloat(df_pb_desc.loc['25%', code]),  # PB 25%
                           __ffloat(df_pb_desc.loc['50%', code]),  # PB 50%
                           __ffloat(df_pb_desc.loc['75%', code]),  # PB 75%
                           __ffloat(df_pb_desc.loc['90%', code]),  # PB 90%
                           __ffloat(df_pb_desc.loc['95%', code]),  # PB 95%
                           __ffloat(df_pb_desc.loc['98%', code]),  # PB 98%
                           __ffloat(df_pb_desc.loc['max', code]),  # PB MAX
                           df_pe[code].dropna().index[0].date().strftime('%Y')
                           ])

        pe_code_list.append(utility.get_name_from_ori_code(utility.back_2_original_code(code)))

    date_str = df_pe.iloc[-1].name.strftime("%Y-%m-%d")
    pe_columns = [u'名称',
                  u'PE', u'PE百分位', u'PE MIN', u'PE 10%', u'PE 25%',
                  u'PE 50%', u'PE 75%', u'PE 90%', u'PE 95%', u'PE 98%', u'PE MAX',
                  u'PB', u'PB百分位', u'PB MIN', u'PB 10%', u'PB 25%',
                  u'PB 50%', u'PB 75%', u'PB 90%', u'PB 95%', u'PB 98%', u'PB MAX',
                  u'起始年份']
    df_daily_report = pd.DataFrame(data=pe_results, index=pe_code_list, columns=pe_columns)
    df_daily_report.index = df_daily_report[u'名称']
    del df_daily_report[u'名称']
    df_daily_report.index.name = date_str

    df_target_selling = df_daily_report[['PE', 'PE百分位', 'PE 95%', 'PE 98%', 'PE MAX',
                                         'PB', 'PB百分位', 'PB 95%', 'PB 98%', 'PB MAX']]
    df_target_selling['PE% To 95%'] = ((df_target_selling['PE 95%'] - df_target_selling['PE']) / df_target_selling[
        'PE'] * 100).apply(__ffloat)
    df_target_selling['PE% To 98%'] = ((df_target_selling['PE 98%'] - df_target_selling['PE']) / df_target_selling[
        'PE'] * 100).apply(__ffloat)
    df_target_selling['PE% To MAX'] = ((df_target_selling['PE MAX'] - df_target_selling['PE']) / df_target_selling[
        'PE'] * 100).apply(__ffloat)
    df_target_selling.rename(columns={'PE 95%': 'PE 1st S-1/4-95%',
                                      'PE 98%': 'PE 2nd S-1/3-98%',
                                      'PE MAX': 'PE 3rd S-1/2-MAX'}, inplace=True)
    df_target_selling['PB% To 95%'] = ((df_target_selling['PB 95%'] - df_target_selling['PB']) / df_target_selling[
        'PB'] * 100).apply(__ffloat)
    df_target_selling['PB% To 98%'] = ((df_target_selling['PB 98%'] - df_target_selling['PB']) / df_target_selling[
        'PB'] * 100).apply(__ffloat)
    df_target_selling['PB% To MAX'] = ((df_target_selling['PB MAX'] - df_target_selling['PB']) / df_target_selling[
        'PB'] * 100).apply(__ffloat)
    df_target_selling.rename(columns={'PB 95%': 'PB 1st S-1/4-95%',
                                      'PB 98%': 'PB 2nd S-1/3-98%',
                                      'PB MAX': 'PB 3rd S-1/2-MAX'}, inplace=True)
    df_target_selling = df_target_selling[
        ['PE', 'PE百分位', 'PE 1st S-1/4-95%', 'PE% To 95%',
         'PE 2nd S-1/3-98%', 'PE% To 98%', 'PE 3rd S-1/2-MAX', 'PE% To MAX',
         'PB', 'PB百分位', 'PB 1st S-1/4-95%', 'PB% To 95%',
         'PB 2nd S-1/3-98%', 'PB% To 98%', 'PB 3rd S-1/2-MAX', 'PB% To MAX',
         ]]
    return df_daily_report, df_target_selling


def cal_index_corr(index_list):
    df_price = build_historical_price(index_list)
    df_price = df_price[index_list].dropna(how='all')
    for idx in df_price.columns:
        df_price.rename(columns={idx: utility.get_name_from_ori_code(utility.back_2_original_code(idx))},
                        inplace=True)
    df_pe_corr = df_price.corr()
    return df_pe_corr


def get_index_pe_pb_by_date(index_list, date, cal_method=2):
    result_df = pd.DataFrame()
    for idx in index_list:
        df = pd.read_csv('%s/index_pe_pb/%s_pe_pb.csv' % (
            utility.DATA_ROOT, utility.convert_code_2_csvfilename(utility.back_2_original_code(idx))), index_col=0)
        df = df.loc[int(date), ['pe%s' % cal_method, 'pb%s' % cal_method]]
        df['index_code'] = idx
        result_df = result_df.append(df, ignore_index=True)
    return result_df


def build_single_index_price_pe_pb(index_code, cal_method=2):
    df_pe = build_historical_pe([index_code], cal_method)[[index_code]]
    df_pe.rename(columns={index_code: 'PE'}, inplace=True)
    df_pb = build_historical_pb([index_code], cal_method)[[index_code]]
    df_pb.rename(columns={index_code: 'PB'}, inplace=True)
    df_price = build_historical_price([index_code])[[index_code]]
    df_price.rename(columns={index_code: 'price'}, inplace=True)
    df_result = pd.concat([df_price, df_pe, df_pb], axis=1).dropna(how='all')
    return df_result


# plot single index's two data(pe vs pb / pe vs price / pb vs price)
def plot_single_index_price_pe_pb(index_code, select=['PE', 'PB'], cal_method=2):
    df_result = build_single_index_price_pe_pb(index_code, cal_method)
    df_result.index = pd.to_datetime(df_result.index, format="%Y%m%d")
    ax1 = df_result[select[0]].plot(color='red', rot=45,
                                    title='%s %s and %s' % (
                                        utility.get_name_from_ori_code(utility.back_2_original_code(index_code)),
                                        select[0], select[1]), grid=True)
    ax2 = ax1.twinx()
    df_result[select[1]].plot(ax=ax2)
    # ask matplotlib for the plotted objects and their labels
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc=0)
    plt.show()


def plot_single_index_different_pe_method(index_code):
    df_pe = build_historical_pe([index_code])
    df_pe.index = pd.to_datetime(df_pe.index, format="%Y%m%d")
    jiaquan = '%s - 加权' % utility.get_name_from_ori_code(utility.back_2_original_code(index_code))
    dengquan = '%s - 等权' % utility.get_name_from_ori_code(utility.back_2_original_code(index_code))
    zhongweishu = '%s - 中位数' % utility.get_name_from_ori_code(utility.back_2_original_code(index_code))
    pingjun = '%s - 平均' % utility.get_name_from_ori_code(utility.back_2_original_code(index_code))
    df_pe = df_pe[[jiaquan, dengquan, zhongweishu, pingjun]].dropna(how='any')
    df_pe.plot(rot=45, grid=True)
    plt.title('Index all kinds of PE Plot')
    plt.show()


def plot_single_index_different_pb_method(index_code):
    df_pb = build_historical_pb([index_code])
    df_pb.index = pd.to_datetime(df_pb.index, format="%Y%m%d")
    jiaquan = '%s - 加权' % utility.get_name_from_ori_code(utility.back_2_original_code(index_code))
    dengquan = '%s - 等权' % utility.get_name_from_ori_code(utility.back_2_original_code(index_code))
    zhongweishu = '%s - 中位数' % utility.get_name_from_ori_code(utility.back_2_original_code(index_code))
    pingjun = '%s - 平均' % utility.get_name_from_ori_code(utility.back_2_original_code(index_code))
    df_pb = df_pb[[jiaquan, dengquan, zhongweishu, pingjun]].dropna(how='any')
    df_pb.plot(rot=45, grid=True)
    plt.title('Index all kinds of PB Plot')
    plt.show()


def plot_pe_report(index_list, cal_method=2):
    df_pe = build_historical_pe(index_list, cal_method)
    df_pe.index = pd.to_datetime(df_pe.index, format="%Y%m%d")
    df_pe = df_pe[index_list]
    df_pe = df_pe.dropna(how='all')
    for idx_code in df_pe.columns:
        df_pe.rename(columns={idx_code: utility.get_name_from_ori_code(utility.back_2_original_code(idx_code))},
                     inplace=True)
    df_pe.plot(rot=45, grid=True)
    plt.title('Index PE Plot')
    plt.show()


def plot_pb_report(index_list, cal_method=2):
    df_pb = build_historical_pb(index_list, cal_method)
    df_pb.index = pd.to_datetime(df_pb.index, format="%Y%m%d")
    df_pb = df_pb[index_list]
    df_pb = df_pb.dropna(how='all')
    for idx_code in df_pb.columns:
        df_pb.rename(columns={idx_code: utility.get_name_from_ori_code(utility.back_2_original_code(idx_code))},
                     inplace=True)
    df_pb.plot(rot=45, grid=True)
    plt.title('Index PB Plot')
    plt.show()


def plot_pe_hist(index_code, cal_method=2):
    df_pe = build_historical_pe([index_code], cal_method)
    df_pe.index = pd.to_datetime(df_pe.index, format="%Y%m%d")
    df_pe = df_pe[[index_code]].dropna(how='any')
    df_pe.hist(column=df_pe.columns[0], bins=round(df_pe.count()[0] / 8))
    plt.title('%s PE Histogram - Current PE is %.2f' % (
        utility.get_name_from_ori_code(utility.back_2_original_code(df_pe.columns[0])), df_pe.iloc[-1, 0]))
    plt.show()


def plot_pb_hist(index_code, cal_method=2):
    df_pb = build_historical_pb([index_code], cal_method)
    df_pb.index = pd.to_datetime(df_pb.index, format="%Y%m%d")
    df_pb = df_pb[[index_code]].dropna(how='any')
    df_pb.hist(column=df_pb.columns[0], bins=round(df_pb.count()[0] / 8))
    plt.title('%s PE Histogram - Current PB is %.2f' % (
        utility.get_name_from_ori_code(utility.back_2_original_code(df_pb.columns[0])), df_pb.iloc[-1, 0]))
    plt.show()


def plot_pe_bin(index_code, cal_method=2, interval=20):
    df_pe = build_historical_pe([index_code], cal_method)
    df_pe.index = pd.to_datetime(df_pe.index, format="%Y%m%d")
    df_pe = df_pe[[index_code]].dropna(how='any')
    df_pe_desc = df_pe.describe()
    bins = []
    pe_max = df_pe_desc.loc['max', index_code]
    pe_min = df_pe_desc.loc['min', index_code]
    sub_max_min = pe_max - pe_min
    for i in range(interval):
        increment = i * (1 / interval)
        bins.append(__ffloat(sub_max_min * increment + pe_min))
    bins.append(pe_max)
    score_cat = pd.cut(df_pe[index_code], bins)
    pe_bin = pd.value_counts(score_cat)
    pe_bin = pe_bin.sort_index()
    pe_bin.plot(kind='bar', rot=75)
    plt.title('%s PE Bins Report - Current PE is %.2f' % (utility.get_name_from_ori_code(df.columns[0]), df.iloc[-1, 0]))
    plt.show()


def plot_pb_bin(index_code, cal_method=2, interval=20):
    df_pb = build_historical_pb([index_code], cal_method)
    df_pb.index = pd.to_datetime(df_pb.index, format="%Y%m%d")
    df_pb = df_pb[[index_code]].dropna(how='any')
    df_pb_desc = df_pb.describe()
    bins = []
    pb_max = df_pb_desc.loc['max', index_code]
    pb_min = df_pb_desc.loc['min', index_code]
    sub_max_min = pb_max - pb_min
    for i in range(interval):
        increment = i * (1 / interval)
        bins.append(__ffloat(sub_max_min * increment + pb_min))
    bins.append(pb_max)
    score_cat = pd.cut(df_pb[index_code], bins)
    pb_bin = pd.value_counts(score_cat)
    pb_bin = pb_bin.sort_index()
    pb_bin.plot(kind='bar', rot=75)
    plt.title('%s PB Bins Report - Current PB is %.2f' % (
        utility.get_name_from_ori_code(utility.back_2_original_code(df_pb.columns[0])),
        df_pb.iloc[-1, 0]))
    plt.show()


def __ffloat(data_in):
    return float('%.2f' % data_in)


if __name__ == '__main__':
    plot_pb_bin('000905.SH')
    pass
