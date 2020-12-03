# -*- coding: utf-8 -*-
from jqdatasdk import *
from index_analysis import index_data_operation
from datetime import timedelta, date
import pandas as pd
import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt


class IndexAnalyze(object):
    def __init__(self, data_source):
        mpl.rcParams[u'font.sans-serif'] = ['SimHei']
        mpl.rcParams['axes.unicode_minus'] = False
        mpl.use('TkAgg')

        self.__report_root = './report/'
        self.__params_root = './params/'
        self.__df_index = pd.read_csv('%sindex_list.csv' % self.__params_root, dtype=str)
        self.__data_source = data_source
        if self.__data_source == 'jqdata':
            auth('18500150123', 'YanTeng881128')
            self.__data_root = './data/'
            self.__index_data_operation = index_data_operation.JqdataUpdater(self.__df_index, self.__data_root)

    def index_data_update_2_csv(self, init=False):
        self.__index_data_operation.update_pe_pb_2_csv(init=init)

    # four selling point in total. 95% PE as the first - selling 1/4; 98% PE as the second - selling 1/4;
    # MAX PE as the third - selling 1/4
    def daily_pe_pb_report(self, cal_method=2, date_str=None):
        df_pe = self.__index_data_operation.build_historical_pe(cal_method)
        df_pb = self.__index_data_operation.build_historical_pb(cal_method)
        df_pe.index = pd.to_datetime(df_pe.index)
        df_pb.index = pd.to_datetime(df_pb.index)
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

        for code in self.__df_index['index_code']:
            pe_ratio = round(
                len(df_pe[code][df_pe[code] < df_pe.iloc[-1][code]]) / float(len(df_pe[code].dropna())) * 100,
                2)
            pb_ratio = round(
                len(df_pb[code][df_pb[code] < df_pb.iloc[-1][code]]) / float(len(df_pb[code].dropna())) * 100,
                2)
            pe_results.append([self.__index_data_operation.get_index_name_from_index_code(code),  # 名称
                               float(self.__ffloat(df_pe.iloc[-1][code])),  # 市盈率
                               pe_ratio,  # 百分位
                               self.__ffloat(df_pe_desc.loc['min', code]),  # PE MIN
                               self.__ffloat(df_pe_desc.loc['10%', code]),  # PE 10%
                               self.__ffloat(df_pe_desc.loc['25%', code]),  # PE 25%
                               self.__ffloat(df_pe_desc.loc['50%', code]),  # PE 50%
                               self.__ffloat(df_pe_desc.loc['75%', code]),  # PE 75%
                               self.__ffloat(df_pe_desc.loc['90%', code]),  # PE 90%
                               self.__ffloat(df_pe_desc.loc['95%', code]),  # PE 95% sell 1/4
                               self.__ffloat(df_pe_desc.loc['98%', code]),  # PE 98% sell 1/3
                               self.__ffloat(df_pe_desc.loc['max', code]),  # PE MAX sell 1/2
                               self.__ffloat(df_pb.iloc[-1][code]),  # 市净率
                               pb_ratio,  # PB百分位
                               self.__ffloat(df_pb_desc.loc['min', code]),  # PB MIN
                               self.__ffloat(df_pb_desc.loc['10%', code]),  # PB 10%
                               self.__ffloat(df_pb_desc.loc['25%', code]),  # PB 25%
                               self.__ffloat(df_pb_desc.loc['50%', code]),  # PB 50%
                               self.__ffloat(df_pb_desc.loc['75%', code]),  # PB 75%
                               self.__ffloat(df_pb_desc.loc['90%', code]),  # PB 90%
                               self.__ffloat(df_pb_desc.loc['95%', code]),  # PB 95%
                               self.__ffloat(df_pb_desc.loc['98%', code]),  # PB 98%
                               self.__ffloat(df_pb_desc.loc['max', code]),  # PB MAX
                               df_pe[code].dropna().index[0].date().strftime('%Y')
                               ])

            pe_code_list.append(self.__index_data_operation.get_index_name_from_index_code(code))

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
            'PE'] * 100).apply(self.__ffloat)
        df_target_selling['PE% To 98%'] = ((df_target_selling['PE 98%'] - df_target_selling['PE']) / df_target_selling[
            'PE'] * 100).apply(self.__ffloat)
        df_target_selling['PE% To MAX'] = ((df_target_selling['PE MAX'] - df_target_selling['PE']) / df_target_selling[
            'PE'] * 100).apply(self.__ffloat)
        df_target_selling.rename(columns={'PE 95%': 'PE 1st S-1/4-95%',
                                          'PE 98%': 'PE 2nd S-1/3-98%',
                                          'PE MAX': 'PE 3rd S-1/2-MAX'}, inplace=True)
        df_target_selling['PB% To 95%'] = ((df_target_selling['PB 95%'] - df_target_selling['PB']) / df_target_selling[
            'PB'] * 100).apply(self.__ffloat)
        df_target_selling['PB% To 98%'] = ((df_target_selling['PB 98%'] - df_target_selling['PB']) / df_target_selling[
            'PB'] * 100).apply(self.__ffloat)
        df_target_selling['PB% To MAX'] = ((df_target_selling['PB MAX'] - df_target_selling['PB']) / df_target_selling[
            'PB'] * 100).apply(self.__ffloat)
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

    def cal_index_corr(self, index_list=None):
        if index_list is None:
            index_list = list(self.__df_index['index_code'])
        df_price = self.__index_data_operation.build_historical_price()
        df_price = df_price[index_list].dropna(how='all')
        for idx in df_price.columns:
            df_price.rename(columns={idx: self.__index_data_operation.get_index_name_from_index_code(idx)},
                            inplace=True)
        df_pe_corr = df_price.corr()
        return df_pe_corr

    def get_index_pe_pb_by_date(self, date, index_list=None):
        if index_list is None:
            index_list = list(self.__df_index['index_code'])
        return self.__index_data_operation.get_index_list_pe_pb_date(date, index_list)

    def build_single_index_price_pe_pb(self, index_code, cal_method=2):
        df_pe = self.__index_data_operation.build_historical_pe(cal_method)[[index_code]]
        df_pe.rename(columns={index_code: 'PE'}, inplace=True)
        df_pb = self.__index_data_operation.build_historical_pb(cal_method)[[index_code]]
        df_pb.rename(columns={index_code: 'PB'}, inplace=True)
        df_price = self.__index_data_operation.build_historical_price()[[index_code]]
        df_price.rename(columns={index_code: 'price'}, inplace=True)
        df_result = pd.concat([df_price, df_pe, df_pb], axis=1).dropna(how='all')
        return df_result

    # plot single index's two data(pe vs pb / pe vs price / pb vs price)
    def plot_single_index_price_pe_pb(self, index_code, select=['PE', 'PB'], cal_method=2):
        df_result = self.build_single_index_price_pe_pb(index_code, cal_method)
        ax1 = df_result[select[0]].plot(color='red', rot=45,
                                        title='%s %s and %s' % (
                                            self.__index_data_operation.get_index_name_from_index_code(index_code),
                                            select[0], select[1]), grid=True)
        ax2 = ax1.twinx()
        df_result[select[1]].plot(ax=ax2)
        # ask matplotlib for the plotted objects and their labels
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc=0)
        plt.show()

    def plot_single_index_different_pe_method(self, index_code):
        df_pe = self.__index_data_operation.build_historical_pe()
        jiaquan = '%s - 加权' % self.__index_data_operation.get_index_name_from_index_code(index_code)
        dengquan = '%s - 等权' % self.__index_data_operation.get_index_name_from_index_code(index_code)
        zhongweishu = '%s - 中位数' % self.__index_data_operation.get_index_name_from_index_code(index_code)
        pingjun = '%s - 平均' % self.__index_data_operation.get_index_name_from_index_code(index_code)
        df_pe = df_pe[[jiaquan, dengquan, zhongweishu, pingjun]].dropna(how='any')
        df_pe.plot(rot=45, grid=True)
        plt.title('Index all kinds of PE Plot')
        plt.show()

    def plot_single_index_different_pb_method(self, index_code):
        df_pb = self.__index_data_operation.build_historical_pb()
        jiaquan = '%s - 加权' % self.__index_data_operation.get_index_name_from_index_code(index_code)
        dengquan = '%s - 等权' % self.__index_data_operation.get_index_name_from_index_code(index_code)
        zhongweishu = '%s - 中位数' % self.__index_data_operation.get_index_name_from_index_code(index_code)
        pingjun = '%s - 平均' % self.__index_data_operation.get_index_name_from_index_code(index_code)
        df_pb = df_pb[[jiaquan, dengquan, zhongweishu, pingjun]].dropna(how='any')
        df_pb.plot(rot=45, grid=True)
        plt.title('Index all kinds of PB Plot')
        plt.show()

    def plot_pe_report(self, index_list=None, cal_method=2):
        df_pe = self.__index_data_operation.build_historical_pe(cal_method)
        if index_list is not None:
            df_pe = df_pe[index_list]
        df_pe = df_pe.dropna(how='all')
        for idx_code in df_pe.columns:
            df_pe.rename(columns={idx_code: self.__index_data_operation.get_index_name_from_index_code(idx_code)},
                         inplace=True)
        df_pe.plot(rot=45, grid=True)
        plt.title('Index PE Plot')
        plt.show()

    def plot_pb_report(self, index_list=None, cal_method=2):
        df_pb = self.__index_data_operation.build_historical_pb(cal_method)
        if index_list is not None:
            df_pb = df_pb[index_list]
        df_pb = df_pb.dropna(how='all')
        for idx_code in df_pb.columns:
            df_pb.rename(columns={idx_code: self.__index_data_operation.get_index_name_from_index_code(idx_code)},
                         inplace=True)
        df_pb.plot(rot=45, grid=True)
        plt.title('Index PB Plot')
        plt.show()

    def plot_pe_hist(self, index_code, cal_method=2):
        df_pe = self.__index_data_operation.build_historical_pe(cal_method)
        df_pe = df_pe[[index_code]].dropna(how='any')
        df_pe.hist(column=df_pe.columns[0], bins=round(df_pe.count()[0] / 8))
        plt.title(
            '%s PE Histogram - Current PE is %.2f' % (self.__index_data_operation.get_index_name_from_index_code(
                df_pe.columns[0]),
                                                      df_pe.iloc[-1, 0]))
        plt.show()

    def plot_pb_hist(self, index_code, cal_method=2):
        df_pb = self.__index_data_operation.build_historical_pb(cal_method)
        df_pb = df_pb[[index_code]].dropna(how='any')
        df_pb.hist(column=df_pb.columns[0], bins=round(df_pb.count()[0] / 8))
        plt.title(
            '%s PE Histogram - Current PB is %.2f' % (self.__index_data_operation.get_index_name_from_index_code(
                df_pb.columns[0]),
                                                      df_pb.iloc[-1, 0]))
        plt.show()

    def plot_pe_bin(self, index_code, cal_method=2, interval=20):
        df_pe = self.__index_data_operation.build_historical_pe(cal_method)
        df_pe = df_pe[[index_code]].dropna(how='any')
        df_pe_desc = df_pe.describe()
        bins = []
        pe_max = df_pe_desc.loc['max', index_code]
        pe_min = df_pe_desc.loc['min', index_code]
        sub_max_min = pe_max - pe_min
        for i in range(interval):
            increment = i * (1 / interval)
            bins.append(self.__ffloat(sub_max_min * increment + pe_min))
        bins.append(pe_max)
        score_cat = pd.cut(df_pe[index_code], bins)
        pe_bin = pd.value_counts(score_cat)
        pe_bin = pe_bin.sort_index()
        pe_bin.plot(kind='bar', rot=75)
        plt.title('%s PE Bins Report - Current PE is %.2f' % (
            self.__index_data_operation.get_index_name_from_index_code(df_pe.columns[0]),
            df_pe.iloc[-1, 0]))
        plt.show()

    def plot_pb_bin(self, index_code, cal_method=2, interval=20):
        df_pb = self.__index_data_operation.build_historical_pb(cal_method)
        df_pb = df_pb[[index_code]].dropna(how='any')
        df_pb_desc = df_pb.describe()
        bins = []
        pb_max = df_pb_desc.loc['max', index_code]
        pb_min = df_pb_desc.loc['min', index_code]
        sub_max_min = pb_max - pb_min
        for i in range(interval):
            increment = i * (1 / interval)
            bins.append(self.__ffloat(sub_max_min * increment + pb_min))
        bins.append(pb_max)
        score_cat = pd.cut(df_pb[index_code], bins)
        pb_bin = pd.value_counts(score_cat)
        pb_bin = pb_bin.sort_index()
        pb_bin.plot(kind='bar', rot=75)
        plt.title('%s PB Bins Report - Current PE is %.2f' % (
            self.__index_data_operation.get_index_name_from_index_code(df_pb.columns[0]),
            df_pb.iloc[-1, 0]))
        plt.show()

    @staticmethod
    def __ffloat(data_in):
        return float('%.2f' % data_in)
