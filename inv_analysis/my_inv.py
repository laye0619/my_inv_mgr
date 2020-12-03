# coding:utf-8
#TODO change data source to tushare
# 我的资产分析类定义
import datetime

# import jqdatasdk as jq
import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FormatStrFormatter
from pandas import DataFrame

mpl.use('TkAgg')


class MyInvestmentAnalysis:
    def __init__(self):
        # jq.auth('18500150123', 'YanTeng881128')
        mpl.rcParams[u'font.sans-serif'] = ['SimHei']
        mpl.rcParams['axes.unicode_minus'] = False

        self.balance_raw_data = DataFrame()
        self.transaction_raw_data = DataFrame()
        self.master_raw_data = DataFrame()

        self.all_category_balance = DataFrame()
        self.all_category_transaction = DataFrame()
        self.master_data = DataFrame()

    def data_preparation(self, excel_path):
        self.__read_data(excel_path)
        self.__data_trim()

    def __read_data(self, excel_path):
        balance_raw_data = pd.read_excel(excel_path, sheet_name='月度资产明细')
        transaction_raw_data = pd.read_excel(excel_path, sheet_name='交易明细（不包括固定收益）')
        master_raw_data = pd.read_excel(excel_path, sheet_name='主数据')
        self.balance_raw_data = balance_raw_data
        self.transaction_raw_data = transaction_raw_data
        self.master_raw_data = master_raw_data

    def __data_trim(self):
        # 数据清理 - 保留所有分类，只显示总额
        all_category_balance = self.balance_raw_data.loc[:, '期间':'项目名称']
        all_category_balance.insert(8, '金额', self.balance_raw_data.iloc[:, -1])

        # 数据清理 - 保留交易信息
        all_category_transaction = self.transaction_raw_data

        # 数据清理 - 只保留主数据部分
        master_data = self.master_raw_data.iloc[:, 0:6]
        master_data.rename(columns=master_data.iloc[0], inplace=True)
        master_data.drop(0, inplace=True)

        self.all_category_balance = all_category_balance
        self.all_category_transaction = all_category_transaction
        self.master_data = master_data

    # 资产总额曲线: 第二个参数：1-一级分类；2-二级分类；3-三级分类；4-四级分类；5-辅助分类; 0-总额（默认）
    def line_by_category_total_amount(self, category_type=0):
        if category_type == 1:
            group_by_period = self.all_category_balance.groupby(['期间', '一级分类']).sum()
            group_by_period = group_by_period.unstack()
            group_by_period.columns = group_by_period.columns.levels[1]

            ax = plt.gca()
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.yaxis.set_major_formatter(FormatStrFormatter('%1.1f'))
            group_by_period.plot(marker='o', title='一级分类资产总额曲线', ax=ax)
            plt.show()
        elif category_type == 2:
            group_by_period = self.all_category_balance.groupby(['期间', '二级分类']).sum()
            group_by_period = group_by_period.unstack()
            group_by_period.columns = group_by_period.columns.levels[1]

            ax = plt.gca()
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.yaxis.set_major_formatter(FormatStrFormatter('%1.1f'))
            group_by_period.plot(marker='o', title='二级分类资产总额曲线', ax=ax)
            plt.show()
        elif category_type == 3:
            group_by_period = self.all_category_balance.groupby(['期间', '三级分类']).sum()
            group_by_period = group_by_period.unstack()
            group_by_period.columns = group_by_period.columns.levels[1]

            ax = plt.gca()
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.yaxis.set_major_formatter(FormatStrFormatter('%1.1f'))
            group_by_period.plot(marker='o', title='三级分类资产总额曲线', ax=ax)
            plt.show()
        elif category_type == 4:
            group_by_period = self.all_category_balance.groupby(['期间', '四级分类']).sum()
            group_by_period = group_by_period.unstack()
            group_by_period.columns = group_by_period.columns.levels[1]

            ax = plt.gca()
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.yaxis.set_major_formatter(FormatStrFormatter('%1.1f'))
            group_by_period.plot(marker='o', title='四级分类资产总额曲线', ax=ax)
            plt.show()
        elif category_type == 5:
            group_by_period = self.all_category_balance.groupby(['期间', '辅助分类']).sum()
            group_by_period = group_by_period.unstack()
            group_by_period.columns = group_by_period.columns.levels[1]

            ax = plt.gca()
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.yaxis.set_major_formatter(FormatStrFormatter('%1.1f'))
            group_by_period.plot(marker='o', title='辅助分类资产总额曲线', ax=ax)
            plt.show()
        else:
            group_by_period = self.all_category_balance.groupby(['期间'])
            df_group_by_period_sum = DataFrame(group_by_period['金额'].sum())

            ax = plt.gca()
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.yaxis.set_major_formatter(FormatStrFormatter('%1.1f'))
            df_group_by_period_sum.plot(marker='o', title='资产总额曲线', ax=ax)
            for index, row in df_group_by_period_sum.iterrows():
                plt.text(index, row['金额'], row['金额'], ha='center', va='bottom')
            plt.show()

    # 最近期间的分类饼状图: 第二个参数：1-一级分类；2-二级分类；3-三级分类；4-四级分类；5-辅助分类(默认);
    def pie_by_category(self, category_type=5):
        if category_type == 1:
            fuzhu_category_by_period_balance = self.all_category_balance.groupby(['期间', '一级分类']).sum()
            fuzhu_category_by_period_balance = fuzhu_category_by_period_balance.unstack()
            fuzhu_category_by_period_balance.columns = fuzhu_category_by_period_balance.columns.levels[1]
            result_df = fuzhu_category_by_period_balance.iloc[-1].dropna()

            result_df.plot(kind='pie', title='一级分类饼状图', autopct='%1.1f%%')
            plt.show()
        elif category_type == 2:
            fuzhu_category_by_period_balance = self.all_category_balance.groupby(['期间', '二级分类']).sum()
            fuzhu_category_by_period_balance = fuzhu_category_by_period_balance.unstack()
            fuzhu_category_by_period_balance.columns = fuzhu_category_by_period_balance.columns.levels[1]

            result_df = fuzhu_category_by_period_balance.iloc[-1].dropna()
            result_df.plot(kind='pie', title='二级分类饼状图', autopct='%1.1f%%')
            plt.show()
        elif category_type == 3:
            fuzhu_category_by_period_balance = self.all_category_balance.groupby(['期间', '三级分类']).sum()
            fuzhu_category_by_period_balance = fuzhu_category_by_period_balance.unstack()
            fuzhu_category_by_period_balance.columns = fuzhu_category_by_period_balance.columns.levels[1]

            result_df = fuzhu_category_by_period_balance.iloc[-1].dropna()
            result_df.plot(kind='pie', title='三级分类饼状图', autopct='%1.1f%%')
            plt.show()
        elif category_type == 4:
            fuzhu_category_by_period_balance = self.all_category_balance.groupby(['期间', '四级分类']).sum()
            fuzhu_category_by_period_balance = fuzhu_category_by_period_balance.unstack()
            fuzhu_category_by_period_balance.columns = fuzhu_category_by_period_balance.columns.levels[1]

            result_df = fuzhu_category_by_period_balance.iloc[-1].dropna()
            result_df.plot(kind='pie', title='四级分类饼状图', autopct='%1.1f%%')
            plt.show()
        else:
            fuzhu_category_by_period_balance = self.all_category_balance.groupby(['期间', '辅助分类']).sum()
            fuzhu_category_by_period_balance = fuzhu_category_by_period_balance.unstack()
            fuzhu_category_by_period_balance.columns = fuzhu_category_by_period_balance.columns.levels[1]

            result_df = fuzhu_category_by_period_balance.iloc[-1].dropna()
            result_df.plot(kind='pie', title='辅助分类饼状图', autopct='%1.1f%%')
            plt.show()

    # 给定期间内，投资项目利润、利润率柱状图
    def calculate_inv_profit_ratio(self, start_date, end_date, profit_calculate_stock_list=None):
        df_profit = self.__build_item_profit_df()
        start_date = datetime.datetime.strptime(start_date, "%Y-%m")
        end_date = datetime.datetime.strptime(end_date, "%Y-%m")
        df_selected_profit = df_profit.loc[df_profit['期间'] >= start_date]
        df_selected_profit = df_selected_profit.loc[df_selected_profit['期间'] <= end_date]

        profit_master_data = DataFrame(self.master_data.iloc[:, 5])
        profit_master_data = profit_master_data.drop_duplicates()

        # 填入对应的期初期末金额
        profit_master_data.insert(len(profit_master_data.columns), '期末金额', np.nan)
        profit_master_data.insert(len(profit_master_data.columns) - 1, '期初金额', np.nan)
        # 期初金额
        for index, row in df_selected_profit.loc[df_selected_profit['期间'] == df_selected_profit.iloc[0, 0]].iterrows():
            profit_master_data.loc[profit_master_data['项目名称'] == row['项目名称'], '期初金额'] = row['期初金额']
        # 期末金额
        for index, row in df_selected_profit.loc[df_selected_profit['期间'] == df_selected_profit.iloc[-1, 0]].iterrows():
            profit_master_data.loc[profit_master_data['项目名称'] == row['项目名称'], '期末金额'] = row['期末金额']

        # 填入本期变动
        profit_master_data.insert(len(profit_master_data.columns) - 1, '本期变动', np.nan)
        period_change_sum = df_selected_profit.groupby(['项目名称']).sum()
        for index, row in period_change_sum.iterrows():
            profit_master_data.loc[profit_master_data['项目名称'] == index, '本期变动'] = row['本期变动']
        # 计算利润及利润率
        profit_master_data.insert(len(profit_master_data.columns), '本期利润',
                                  (profit_master_data.loc[:, '期末金额'] - profit_master_data.loc[:, '期初金额'] -
                                   profit_master_data.loc[:, '本期变动']))
        profit_master_data.insert(len(profit_master_data.columns), '利润率',
                                  (profit_master_data.loc[:, '本期利润'] / profit_master_data.loc[:, '期初金额']))

        # 最终整理数据并返回
        profit_master_data.reset_index(inplace=True, drop=True)
        profit_df = profit_master_data
        profit_df.set_index(["项目名称"], inplace=True)
        profit_df = profit_df.loc[:, '本期利润':'利润率']
        if profit_calculate_stock_list is not None:
            profit_df = profit_df.loc[profit_calculate_stock_list, :]

        profit_df = profit_df.sort_values('利润率', ascending=False)
        profit_df.plot(kind='bar', title='从' + str(start_date) + '至' + str(end_date) + '利润利润率', subplots=True, rot=80,
                       fontsize=7, align='center', alpha=0.8)
        plt.show()

        return profit_df

    # 建立利润计算DF - 每次都重新计算
    def __build_item_profit_df(self):
        profit_master_data = self.master_data.iloc[:, 0:6]
        profit_master_data = profit_master_data.drop_duplicates()
        target_df = profit_master_data

        period_list = self.all_category_balance.loc[:, '期间'].drop_duplicates().tolist()
        profit_master_data.insert(0, '期间', np.nan)

        # 补全期间
        for tempPeriod in period_list:
            profit_df = profit_master_data.fillna(tempPeriod)
            profit_master_data = pd.concat([profit_df, target_df], axis=0)

        profit_master_data.dropna(inplace=True)

        # 填入对应的期初期末金额
        period_category_sum = self.all_category_balance.groupby(['期间', '项目名称']).sum()
        # 填入期初，期末金额
        profit_master_data.insert(len(profit_master_data.columns), '期末金额', np.nan)
        profit_master_data.insert(len(profit_master_data.columns) - 1, '期初金额', np.nan)

        current_period = np.nan
        previous_period = np.nan
        first_time = True
        for index, row in period_category_sum.iterrows():
            if first_time:
                current_period = index[0]
                first_time = False
            profit_master_data.loc[(profit_master_data['期间'] == index[0]) &
                                   (profit_master_data['项目名称'] == index[1]), '期末金额'] = row['金额']

            if current_period != index[0]:
                previous_period = current_period
                current_period = index[0]
            profit_master_data.loc[(profit_master_data['期间'] == index[0]) &
                                   (profit_master_data['项目名称'] == index[1]), '期初金额'] = profit_master_data.loc[
                (profit_master_data['期间'] == previous_period) &
                (profit_master_data['项目名称'] == index[1]), '期末金额']

        # 填入本期变动
        profit_master_data.insert(len(profit_master_data.columns) - 1, '本期变动', np.nan)
        period_category_change_sum = self.all_category_transaction.groupby(['期间', '项目名称']).sum()
        for index, row in period_category_change_sum.iterrows():
            profit_master_data.loc[(profit_master_data['期间'] == index[0]) &
                                   (profit_master_data['项目名称'] == index[1]), '本期变动'] = row['买入／卖出金额']

        profit_master_data.fillna(0, inplace=True)

        # 计算利润及利润率
        profit_master_data.insert(len(profit_master_data.columns), '本期利润',
                                  (profit_master_data.loc[:, '期末金额'] - profit_master_data.loc[:, '期初金额'] -
                                   profit_master_data.loc[:, '本期变动']))
        profit_master_data.insert(len(profit_master_data.columns), '利润率',
                                  (profit_master_data.loc[:, '本期利润'] / profit_master_data.loc[:, '期初金额']))

        # 最终整理数据并返回
        profit_master_data.reset_index(inplace=True, drop=True)
        profit_df = profit_master_data
        return profit_df

    # 建立利润计算DF - 每次都重新计算
    def __build_profit_df(self):
        # 整理masterData，保留利润有意义的部分四级分类：
        # '可转债基金','A股-大股票指数'，'A股-小股票指数','A股-主题指数','成熟市场指数','主动股票基金',
        profit_list = ['可转债基金', 'A股-大股票指数', 'A股-小股票指数',
                       'A股-主题指数', '成熟市场指数', '主动股票基金']
        profit_master_data = self.master_data.iloc[:, 0:5]
        profit_master_data = profit_master_data.drop_duplicates()

        profit_master_data = profit_master_data.loc[self.master_data['四级分类'].isin(profit_list)]

        target_df = profit_master_data
        period_list = self.all_category_balance.loc[:, '期间'].drop_duplicates().tolist()
        profit_master_data.insert(0, '期间', np.nan)

        # 补全期间
        for tempPeriod in period_list:
            profit_df = profit_master_data.fillna(tempPeriod)
            profit_master_data = pd.concat([profit_df, target_df], axis=0)

        profit_master_data.dropna(inplace=True)

        # 填入对应的期初期末金额
        period_category_sum = self.all_category_balance.groupby(['期间', '四级分类']).sum()

        # 填入期初，期末金额
        profit_master_data.insert(len(profit_master_data.columns), '期末金额', np.nan)
        profit_master_data.insert(len(profit_master_data.columns) - 1, '期初金额', np.nan)

        current_period = np.nan
        previous_period = np.nan
        first_time = True
        for index, row in period_category_sum.iterrows():
            if first_time:
                current_period = index[0]
                first_time = False
            profit_master_data.loc[(profit_master_data['期间'] == index[0]) &
                                   (profit_master_data['四级分类'] == index[1]), '期末金额'] = row['金额']

            if current_period != index[0]:
                previous_period = current_period
                current_period = index[0]
            profit_master_data.loc[(profit_master_data['期间'] == index[0]) &
                                   (profit_master_data['四级分类'] == index[1]), '期初金额'] = profit_master_data.loc[
                (profit_master_data['期间'] == previous_period) &
                (profit_master_data['四级分类'] == index[1]), '期末金额']

        # 填入本期变动
        profit_master_data.insert(len(profit_master_data.columns) - 1, '本期变动', np.nan)
        period_category_change_sum = self.all_category_transaction.groupby(['期间', '四级分类']).sum()
        for index, row in period_category_change_sum.iterrows():
            profit_master_data.loc[(profit_master_data['期间'] == index[0]) &
                                   (profit_master_data['四级分类'] == index[1]), '本期变动'] = row['买入／卖出金额']

        profit_master_data.fillna(0, inplace=True)

        # 计算利润及利润率
        profit_master_data.insert(len(profit_master_data.columns), '本期利润',
                                  (profit_master_data.loc[:, '期末金额'] - profit_master_data.loc[:, '期初金额'] -
                                   profit_master_data.loc[:, '本期变动']))
        profit_master_data.insert(len(profit_master_data.columns), '利润率',
                                  (profit_master_data.loc[:, '本期利润'] / profit_master_data.loc[:, '期初金额']))

        # 最终整理数据并返回
        profit_master_data.reset_index(inplace=True, drop=True)
        profit_df = profit_master_data
        return profit_df

    # 分类利润率曲线: 第二个参数：1-一级分类；2-二级分类；3-三级分类；4-四级分类；5-辅助分类; 0-总额（默认）
    def line_profit_by_category(self, category_type=0):
        build_profit_df = self.__build_profit_df()
        if category_type == 1:
            profit_by_category = build_profit_df.groupby(['期间', '一级分类']).sum()
            profit_by_category.loc[:, '利润率'] = profit_by_category.loc[:, '本期利润'] / profit_by_category.loc[:, '期初金额']
            profit_by_category = profit_by_category['利润率']
            profit_by_category = profit_by_category.unstack()

            ax = plt.gca()
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.yaxis.set_major_formatter(FormatStrFormatter('%1.2f'))
            profit_by_category.plot(marker='o', title='一级分类利润曲线', ax=ax)
            plt.show()
        elif category_type == 2:
            profit_by_category = build_profit_df.groupby(['期间', '二级分类']).sum()
            profit_by_category.loc[:, '利润率'] = profit_by_category.loc[:, '本期利润'] / profit_by_category.loc[:, '期初金额']
            profit_by_category = profit_by_category['利润率']
            profit_by_category = profit_by_category.unstack()

            ax = plt.gca()
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.yaxis.set_major_formatter(FormatStrFormatter('%1.2f'))
            profit_by_category.plot(marker='o', title='二级分类利润曲线', ax=ax)
            plt.show()
        elif category_type == 3:
            profit_by_category = build_profit_df.groupby(['期间', '三级分类']).sum()
            profit_by_category.loc[:, '利润率'] = profit_by_category.loc[:, '本期利润'] / profit_by_category.loc[:, '期初金额']
            profit_by_category = profit_by_category['利润率']
            profit_by_category = profit_by_category.unstack()

            ax = plt.gca()
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.yaxis.set_major_formatter(FormatStrFormatter('%1.2f'))
            profit_by_category.plot(marker='o', title='三级分类利润曲线', ax=ax)
            plt.show()
        elif category_type == 4:
            profit_by_category = build_profit_df.groupby(['期间', '四级分类']).sum()
            profit_by_category.loc[:, '利润率'] = profit_by_category.loc[:, '本期利润'] / profit_by_category.loc[:, '期初金额']
            profit_by_category = profit_by_category['利润率']
            profit_by_category = profit_by_category.unstack()

            ax = plt.gca()
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.yaxis.set_major_formatter(FormatStrFormatter('%1.2f'))
            profit_by_category.plot(marker='o', title='四级分类利润曲线', ax=ax)
            plt.show()
        elif category_type == 5:
            profit_by_category = build_profit_df.groupby(['期间', '辅助分类']).sum()
            profit_by_category.loc[:, '利润率'] = profit_by_category.loc[:, '本期利润'] / profit_by_category.loc[:, '期初金额']
            profit_by_category = profit_by_category['利润率']
            profit_by_category = profit_by_category.unstack()

            ax = plt.gca()
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.yaxis.set_major_formatter(FormatStrFormatter('%1.2f'))
            profit_by_category.plot(marker='o', title='辅助分类利润曲线', ax=ax)
            plt.show()
        else:
            profit_by_category = build_profit_df.groupby(['期间']).sum()
            profit_by_category.loc[:, '利润率'] = profit_by_category.loc[:, '本期利润'] / profit_by_category.loc[:, '期初金额']
            profit_by_category = profit_by_category['利润率']

            ax = plt.gca()
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.yaxis.set_major_formatter(FormatStrFormatter('%1.2f'))
            profit_by_category.plot(marker='o', title='总金额利润率曲线', ax=ax)
            plt.show()

            # 返回选定的项目名称按期间余额

    def __build_investment_item_df(self, investment_item_list):
        investment_item_df = self.all_category_balance.loc[
            self.all_category_balance.loc[:, '项目名称'].isin(investment_item_list)]
        investment_item_df.reset_index(inplace=True, drop=True)
        return investment_item_df

    # 打印选定投资项目范围饼状图
    def pie_by_given_investment_item(self, investment_item_list):
        investment_item_df = self.__build_investment_item_df(investment_item_list)
        last_period_investment_item_df = \
            investment_item_df.loc[investment_item_df.loc[:, '期间']
                                   == investment_item_df.iloc[-1].loc['期间']].loc[:, ['项目名称', '金额']]
        last_period_investment_item_df.set_index('项目名称', inplace=True)
        last_period_investment_item_df.fillna(0)

        fig = plt.figure(figsize=(15, 15))
        plt.title(u'选定投资项目饼状图 - 选定总金额：' + str(last_period_investment_item_df['金额'].sum()))
        plt.pie(last_period_investment_item_df['金额'],
                labels=last_period_investment_item_df.index,
                startangle=90,
                shadow=False,
                autopct='%1.1f%%')
        plt.show()

        # 计算比例并添加到DF中
        amount_sum = last_period_investment_item_df['金额'].sum()
        last_period_investment_item_df.insert(len(last_period_investment_item_df.columns), '占比',
                                              last_period_investment_item_df.loc[:, '金额'] / amount_sum)

        last_period_investment_item_df['占比'] = last_period_investment_item_df['占比'].apply(lambda x: format(x, '.2%'))

        last_period_investment_item_df = last_period_investment_item_df.sort_values('占比')
        return last_period_investment_item_df

    # 打印自给定日期起至当前的指数增长率
    @staticmethod
    def analyze_profit(profit_calculate_stock_dict, start_date, end_date):
        # 构建结果df
        df = pd.DataFrame(index=profit_calculate_stock_dict.keys(), columns=[start_date, end_date, "Increment Ratio"])
        for index, row in df.iterrows():
            row[start_date] = \
                jq.get_price(profit_calculate_stock_dict[index], count=1, end_date=start_date, frequency='daily',
                             fields=['close']).iloc[0, 0]
            row[end_date] = \
                jq.get_price(profit_calculate_stock_dict[index], count=1, end_date=end_date, frequency='daily',
                             fields=['close']).iloc[0, 0]
            row["Increment Ratio"] = '{:.2f}%'.format((row[end_date] - row[start_date]) / row[start_date] * 100)
        return df
