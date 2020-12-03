from abc import ABCMeta, abstractmethod, ABC
import os
import pandas as pd

from datetime import timedelta, date
import datetime, time
from io import BytesIO
from jqdatasdk import *
from numpy import sqrt, mean, NaN
from scipy.stats import mstats


class IndexDataUpdate(metaclass=ABCMeta):  # 抽象类（接口类）
    @abstractmethod
    def update_pe_pb_2_csv(self): pass

    @abstractmethod
    def build_historical_price(self): pass

    @abstractmethod
    def build_historical_pe(self): pass

    @abstractmethod
    def build_historical_pb(self): pass

    def get_index_name_from_index_code(self): pass


class JqdataUpdater(IndexDataUpdate):
    def __init__(self, df_index, data_root):
        self.__df_index = df_index
        self.__data_root = data_root
        self.convert_jqdata_index_code()

    # convert index code from jqdata format to normal
    @staticmethod
    def __convert_code(code):
        if code.endswith('XSHG'):
            return 'sh' + code[0:6]
        elif code.endswith('XSHE'):
            return 'sz' + code[0:6]

    @staticmethod
    def __get_idx_components(idx, day):
        securities_lst = [
            u'000166.XSHE', u'000686.XSHE', u'000712.XSHE', u'000728.XSHE', u'000750.XSHE', u'000776.XSHE',
            u'000783.XSHE', u'000987.XSHE', u'002500.XSHE', u'002670.XSHE', u'002673.XSHE', u'002736.XSHE',
            u'002797.XSHE', u'600030.XSHG', u'600061.XSHG', u'600109.XSHG', u'600369.XSHG', u'600837.XSHG',
            u'600909.XSHG', u'600958.XSHG', u'600999.XSHG', u'601099.XSHG', u'601198.XSHG', u'601211.XSHG',
            u'601375.XSHG', u'601377.XSHG', u'601555.XSHG', u'601688.XSHG', u'601788.XSHG', u'601881.XSHG',
            u'601901.XSHG']
        bank_lst = [
            u'000001.XSHE', u'002142.XSHE', u'002807.XSHE', u'002839.XSHE', u'600000.XSHG', u'600015.XSHG',
            u'600016.XSHG', u'600036.XSHG', u'600919.XSHG', u'600926.XSHG', u'601009.XSHG', u'601166.XSHG',
            u'601169.XSHG', u'601229.XSHG', u'601288.XSHG', u'601328.XSHG', u'601398.XSHG', u'601818.XSHG',
            u'601939.XSHG', u'601988.XSHG', u'601997.XSHG', u'601998.XSHG']
        if type(day) is date:
            day = pd.Timestamp(day)
        if idx in ['399986.XSHE', '399975.XSHE', '000852.XSHG']:
            all_df = get_all_securities(['stock'], day)
            if day > pd.Timestamp("2011-08-02"):
                all_df = all_df[all_df.index.isin(get_index_stocks('000985.XSHG', day))]  # 中证全指过滤
            if idx == '399986.XSHE' and day < pd.Timestamp("2015-05-19"):  # 中证银行
                df = all_df[all_df.index.isin(bank_lst)]
            elif idx == '399975.XSHE' and day < pd.Timestamp("2015-05-19"):  # 中证证券
                df = all_df[all_df.index.isin(securities_lst)]
            elif idx == '000852.XSHG' and day < pd.Timestamp("2014-10-17"):  # 中证1000
                stocks_800 = get_index_stocks('000906.XSHG', day)
                df = all_df[~all_df.index.isin(stocks_800)]  # 剔除中证800
                df = get_fundamentals(query(
                    valuation.code, valuation.circulating_market_cap
                ).filter(
                    valuation.code.in_(df.index.tolist())
                ).order_by(valuation.circulating_market_cap.desc()).limit(1000)).dropna().set_index('code')
            else:
                return get_index_stocks(idx, day)
            return df.index.tolist()
        return get_index_stocks(idx, day)

    @staticmethod
    def __pd_read_csv(data_path, flag=False):
        # flag:是否使用read_file函数
        if flag is True:
            file_content = read_file(data_path)
        else:
            file_content = open(data_path, 'rb').read()
        df = pd.read_csv(BytesIO(file_content))
        df.index = pd.to_datetime(df['Unnamed: 0'])
        del df['Unnamed: 0']
        df.index.name = None
        return df

    def __get_index_list_pe_pb_date(self, date, code_list=None):
        '''指定日期的指数PE_PB'''
        ret_dict = {}
        df_all = get_fundamentals(query(valuation), str(date)[0:10])  # 某日所有股票
        if code_list is None:
            code_list = list(self.__df_index['jqdata_code'])
        for code in code_list:
            stocks = self.__get_idx_components(code, date)
            df = df_all[df_all['code'].isin(stocks)]  # 某个指数
            price = get_price(code, start_date=date, end_date=date, fields='close', panel=False).iloc[0, 0]
            if len(df) > 0:
                # 整体法，市值加权
                df = df[df.pb_ratio != 0]  # 去除0
                df = df[df.pe_ratio != 0]  # 去除0
                pe1 = sum(df.market_cap) / sum(df.market_cap / df.pe_ratio)
                pb1 = sum(df.market_cap) / sum(df.market_cap / df.pb_ratio)
                # 等权，亏损置零
                pe2 = len(df) / sum(1 / df.pe_ratio[df.pe_ratio > 0])
                pb2 = len(df) / sum(1 / df.pb_ratio[df.pb_ratio > 0])
                # 中位数，无需预处理
                pe3 = df.pe_ratio.median()
                pb3 = df.pb_ratio.median()
                # 算数平均，取分位数95%置信区间
                pe4 = mean(mstats.winsorize(df.pe_ratio, limits=0.025))
                pb4 = mean(mstats.winsorize(df.pb_ratio, limits=0.025))

                ret_dict[code] = {'price': price,
                                  'pe1': round(pe1, 2), 'pb1': round(pb1, 2),
                                  'pe2': round(pe2, 2), 'pb2': round(pb2, 2),
                                  'pe3': round(pe3, 2), 'pb3': round(pb3, 2),
                                  'pe4': round(pe4, 2), 'pb4': round(pb4, 2), }
        return ret_dict

    def __get_index_list_pe_pb(self, idx_list=None, start_date=None, end_date=None):
        # 返回字典，key为code，value为dataframe
        # code_list中成立最久的放在最前面
        if start_date is None:
            start_date = date(2005, 1, 4)
        if end_date is None:
            end_date = pd.datetime.today() - timedelta(1)
        if idx_list is None:
            idx_list = list(self.__df_index['jqdata_code'])
        x = get_price(idx_list[0], start_date=start_date, end_date=end_date,
                      frequency='daily', fields='close', panel=False)
        date_list = x.index.tolist()
        index_list_dict = {}
        for code in idx_list:
            index_list_dict[code] = pd.DataFrame(index=date_list, data=NaN,
                                                 columns=['price', 'pe1', 'pb1', 'pe2', 'pb2', 'pe3', 'pb3', 'pe4',
                                                          'pb4'])
        for d in date_list:  # 交易日
            ret_dict = self.__get_index_list_pe_pb_date(d, idx_list)
            for key in ret_dict:
                index_list_dict[key].loc[d]['price'] = ret_dict[key]['price']
                index_list_dict[key].loc[d]['pe1'] = ret_dict[key]['pe1']
                index_list_dict[key].loc[d]['pb1'] = ret_dict[key]['pb1']
                index_list_dict[key].loc[d]['pe2'] = ret_dict[key]['pe2']
                index_list_dict[key].loc[d]['pb2'] = ret_dict[key]['pb2']
                index_list_dict[key].loc[d]['pe3'] = ret_dict[key]['pe3']
                index_list_dict[key].loc[d]['pb3'] = ret_dict[key]['pb3']
                index_list_dict[key].loc[d]['pe4'] = ret_dict[key]['pe4']
                index_list_dict[key].loc[d]['pb4'] = ret_dict[key]['pb4']
        return index_list_dict

    def get_index_list_pe_pb_date(self, date, code_list=None):
        return self.__get_index_list_pe_pb_date(date, code_list)

    def update_pe_pb_2_csv(self, target_date=None, init=False):
        if init:
            print('init')
            df_pe_pb = self.__get_index_list_pe_pb(list(self.__df_index['jqdata_code']))
            for key in df_pe_pb:
                data_path = '%s%s_pe_pb.csv' % (self.__data_root, self.__convert_code(key))
                df_pe_pb[key].dropna().to_csv(data_path)
        else:
            for ori_code in list(self.__df_index['jqdata_code']):
                data_path = '%s%s_pe_pb.csv' % (self.__data_root, self.__convert_code(ori_code))
                if os.path.exists(data_path):  # existed csv file, go update incrementally
                    df = self.__pd_read_csv(data_path)
                    df_pe_pb = pd.DataFrame()
                    start_date = df.iloc[-1].name + timedelta(1)
                    if target_date is None or target_date >= start_date:
                        print('incrementally update pe&pb for %s' % ori_code)
                        df_pe_pb = self.__get_index_list_pe_pb([ori_code], start_date, target_date)
                        for key in df_pe_pb:
                            df = self.__pd_read_csv('%s%s_pe_pb.csv' % (self.__data_root, self.__convert_code(key)))
                            delta_df = df_pe_pb[key][df.iloc[-1].name + timedelta(1):]  # 多个指数数据有可能不同步
                            if len(delta_df) > 0:
                                df_pe_pb[key] = pd.concat([df, delta_df])
                            else:
                                df_pe_pb[key] = df
                else:
                    print('adding new pe&pb for %s' % ori_code)
                    df_pe_pb = self.__get_index_list_pe_pb([ori_code])
                for key in df_pe_pb:
                    data_path = '%s%s_pe_pb.csv' % (self.__data_root, self.__convert_code(key))
                    df_pe_pb[key].dropna().to_csv(data_path)

        print('PE/PB data updated...')

    def build_historical_price(self):
        idx_list = list(self.__df_index['jqdata_code'])
        df_price = pd.DataFrame()
        first_time = True
        price_column_str = 'price'
        for idx in idx_list:
            df = pd.read_csv('%s%s_pe_pb.csv' % (self.__data_root, self.__convert_code(idx)), index_col=0)
            df.index.name = 'DATE'
            if first_time:
                df_price = df[[price_column_str]]
                df_price.rename(columns={price_column_str: self.get_index_code_from_jqdata_code(idx)}, inplace=True)
                first_time = False
            else:
                df_price = pd.concat([df_price, df[[price_column_str]]], axis=1)
                df_price.rename(columns={price_column_str: self.get_index_code_from_jqdata_code(idx)}, inplace=True)
        return df_price

    # cal_method = 1: 整体法，市值加权
    # cal_method = 2: 等权，亏损置零
    # cal_method = 3: 中位数，无需预处理
    # cal_method = 4: 算数平均，取分位数95%置信区间
    # Be default, cal_method = None: get all of the method
    def build_historical_pe(self, cal_method=None):
        idx_list = list(self.__df_index['jqdata_code'])
        df_pe = pd.DataFrame()
        first_time = True
        pe_column_str = ''
        pe_name = ''

        if cal_method is None:
            for idx in idx_list:
                df = pd.read_csv('%s%s_pe_pb.csv' % (self.__data_root, self.__convert_code(idx)), index_col=0)
                df.index.name = 'DATE'
                idx_name = self.__df_index.loc[self.__df_index['jqdata_code'] == idx, 'idx_name'].iloc[0]
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
            df = pd.read_csv('%s%s_pe_pb.csv' % (self.__data_root, self.__convert_code(idx)), index_col=0)
            df.index.name = 'DATE'
            if first_time:
                df_pe = df[[pe_column_str]]
                df_pe.rename(columns={pe_column_str: self.get_index_code_from_jqdata_code(idx)}, inplace=True)
                first_time = False
            else:
                df_pe = pd.concat([df_pe, df[[pe_column_str]]], axis=1)
                df_pe.rename(columns={pe_column_str: self.get_index_code_from_jqdata_code(idx)}, inplace=True)

        return df_pe

    # cal_method = 1: 整体法，市值加权
    # cal_method = 2: 等权，亏损置零
    # cal_method = 3: 中位数，无需预处理
    # cal_method = 4: 算数平均，取分位数95%置信区间
    # Be default, cal_method = None: get all of the method
    def build_historical_pb(self, cal_method=None):
        idx_list = list(self.__df_index['jqdata_code'])
        df_pb = pd.DataFrame()
        first_time = True
        pb_column_str = ''
        pb_name = ''

        if cal_method is None:
            for idx in idx_list:
                df = pd.read_csv('%s%s_pe_pb.csv' % (self.__data_root, self.__convert_code(idx)), index_col=0)
                df.index.name = 'DATE'
                idx_name = self.__df_index.loc[self.__df_index['jqdata_code'] == idx, 'idx_name'].iloc[0]
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
            df = pd.read_csv('%s%s_pe_pb.csv' % (self.__data_root, self.__convert_code(idx)), index_col=0)
            df.index.name = 'DATE'
            if first_time:
                df_pb = df[[pb_column_str]]
                df_pb.rename(columns={pb_column_str: self.get_index_code_from_jqdata_code(idx)}, inplace=True)
                first_time = False
            else:
                df_pb = pd.concat([df_pb, df[[pb_column_str]]], axis=1)
                df_pb.rename(columns={pb_column_str: self.get_index_code_from_jqdata_code(idx)}, inplace=True)

        return df_pb

    def get_index_name_from_index_code(self, code):
        return self.__df_index.loc[self.__df_index['index_code'] == code, 'idx_name'].iloc[0]

    def get_index_code_from_jqdata_code(self, jqdata_code):
        return self.__df_index.loc[self.__df_index['jqdata_code'] == jqdata_code, 'index_code'].iloc[0]

    def convert_jqdata_index_code(self):
        add_list = []
        for index, row in self.__df_index.iterrows():
            str_target = row['index_code'] + ('.XSHG' if row['index_mkt'] == 'SH' else '.XSHE')
            add_list.append(str_target)
        self.__df_index['jqdata_code'] = add_list
