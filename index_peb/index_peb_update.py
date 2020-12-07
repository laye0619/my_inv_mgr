import calendar
from abc import abstractmethod, ABCMeta

import pandas as pd
from numpy import NaN

import utility
import tushare as ts
from datetime import timedelta, date


class IndexPebUpdate(metaclass=ABCMeta):
    def __init__(self):
        pass

    def update_pe_pb_2_csv(self, index_list, target_date=None, init=False):
        if init:
            print('init')
            df_pe_pb = self._get_index_list_pe_pb(index_list)
            for key in df_pe_pb:
                data_path = '%s/index_pe_pb/%s_pe_pb.csv' % (utility.DATA_ROOT, utility.convert_code_2_csvfilename(key))
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

    def _get_index_list_pe_pb(self, idx_list=None, start_date=None, end_date=None):
        # 返回字典，key为code，value为dataframe
        # code_list中成立最久的放在最前面
        if start_date is None:
            start_date = date(2005, 1, 4)
        if end_date is None:
            end_date = date.today() - timedelta(1)
        if not idx_list:
            return
        date_list = self._get_transaction_date(start_date=start_date, end_date=end_date)
        index_list_dict = {}
        for code in idx_list:
            index_list_dict[code] = pd.DataFrame(index=date_list, data=NaN,
                                                 columns=['price', 'pe1', 'pb1', 'pe2', 'pb2', 'pe3', 'pb3', 'pe4',
                                                          'pb4'])
        for d in date_list:  # 交易日
            ret_dict = self._get_index_list_pe_pb_date(d, idx_list)
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

    def _get_index_list_pe_pb_date(self, date, code_list=None):
        '''指定日期的指数PE_PB'''
        ret_dict = {}
        if not code_list:
            return
        # df_all = get_fundamentals(query(valuation), str(date)[0:10])  # 某日所有股票
        for code in code_list:
            idx_comp_first_day, inx_comp_last_day = self._get_month_1st_last(date)
            stocks = self._get_idx_components(code, idx_comp_first_day.strftime('%Y%m%d'),
                                              inx_comp_last_day.strftime('%Y%m%d'))
            #TODO here
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

    @staticmethod
    def _get_month_1st_last(date_str):
        year = int(date_str[:4])
        month = int(date_str[4:6])

        # 获取当月第一天的星期和当月的总天数
        first_day_week_day, month_range = calendar.monthrange(year, month)

        # 获取当月的第一天
        first_day = date(year=year, month=month, day=1)
        last_day = date(year=year, month=month, day=month_range)
        return first_day, last_day

    @abstractmethod
    def _get_close_price(self, code, start_date, end_date):
        raise NotImplementedError("Please implement your function in your class")

    @abstractmethod
    def _get_transaction_date(self, start_date, end_date):
        raise NotImplementedError("Please implement your function in your class")

    @abstractmethod
    def _get_idx_components(self, code, first_day, last_day):
        raise NotImplementedError("Please implement your function in your class")


class IndexPebUpdateByTushare(IndexPebUpdate):
    def __init__(self):
        super()
        self.pro = ts.pro_api('602e5ad960d66ab8b1f3c13b4fd746f5323ff808b0820768b02c6da3')

    # 隔离数据源
    def _get_close_price(self, code, start_date, end_date):
        return pd.DataFrame()

    def _get_transaction_date(self, start_date, end_date):
        return self.pro.trade_cal(exchange='', start_date=start_date.strftime('%Y%m%d'),
                                  end_date=end_date.strftime('%Y%m%d'),
                                  fields='cal_date', is_open='1').cal_date

    def _get_idx_components(self, code, first_day, last_day):
        return self.pro.index_weight(index_code=code, start_date=first_day, end_date=last_day)


if __name__ == '__main__':
    index_peb_update = IndexPebUpdateByTushare()
    index_peb_update.update_pe_pb_2_csv(['000905.SH'], init=True)
