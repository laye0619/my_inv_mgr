# 运行我的资产分析

import my_inv
import datetime
import utility

# 数据准备
excelPath = '%s/my_inv_month_end_closing/资产明细表_202011.xlsx' % utility.DATA_ROOT
my_investment_analysis = my_inv.MyInvestmentAnalysis()
my_investment_analysis.data_preparation(excelPath)

# 分析目前比较基准已经有的涨幅
# jq.auth('18500150123', 'YanTeng881128')
profit_calculate_stock_dict = {'沪深300': '000300.SH',
                               '中证500': '000905.SH',
                               '上证50': '000016.SH',
                               '中证红利': '000922.SH',
                               '创业板指': '399006.SZ',
                               '中证养老': '399812.SZ',
                               '全指医药': '000933.SH',
                               '全指消费': '000990.SH',
                               '中证传媒': '399971.SZ',
                               '中证环保': '000827.SH',
                               '证券公司': '399975.SZ',
                               '全指金融': '000992.SH'
                               }

profit_df = my_investment_analysis.analyze_profit(profit_calculate_stock_dict, datetime.date(2019, 3, 1),
                                                  datetime.date(2020, 11, 30))
print(profit_df)

# # 给定期间内，投资项目利润、利润率柱状图
# profit_calculate_stock_list = ['易方达安心回报债券A-110027',
#                                '兴全可转债混合-340001',
#                                'H股ETF-510900',
#                                '50ETF-510050',
#                                '申万沪深300增强-310318',
#                                '富国中证红利-100032',
#                                '创业板100-159915',
#                                '建信/富国中证500指数增强/天弘500增强私募 - 000478/161017',
#                                '传媒ETF-512980',
#                                '广发中证养老-000968',
#                                '广发中证医药-001180',
#                                '广发中证环保-001064',
#                                '易方达证券公司指数分级-502010',
#                                '易方达消费行业股票-110022',
#                                '广发中证全指金融地产-001469',
#                                '恒生ETF-159920',
#                                '德国30-513030/000614',
#                                'SAP德国股票-OwnSAP',
#                                '汇添富价值精选混合-519069',
#                                '中欧价值发现混合-166005',
#                                '华宝油气-162411']
# df_result = my_investment_analysis.calculate_inv_profit_ratio('2020-08', '2020-08', profit_calculate_stock_list)
# print(df_result)


# # 股票占比分析
# investment_item_list = ['50ETF-510050', 'H股ETF-510900', '中欧价值发现混合-166005',
#                         '传媒ETF-512980', '兴全可转债混合-340001', '创业板100-159915',
#                         '富国中证红利-100032', '广发中证全指金融地产-001469', '广发中证养老-000968',
#                         '广发中证医药-001180', '广发中证环保-001064',
#                         '建信/富国中证500指数增强/天弘500增强私募 - 000478/161017', '招商股票+现金',
#                         '易方达安心回报债券A-110027', '易方达消费行业股票-110022', '易方达证券公司指数分级-502010',
#                         '汇添富价值精选混合-519069', '申万沪深300增强-310318', '华宝油气-162411']
#
# df_result = my_investment_analysis.pie_by_given_investment_item(investment_item_list)
# print(df_result)

# # 运行我的资产report
# for x in range(0, 6):
#     my_investment_analysis.line_by_category_total_amount(x)
#     my_investment_analysis.line_profit_by_category(x)

# for x in range(1, 6):
#     my_investment_analysis.pie_by_category(x)

# # 按照辅助分类分析
# # print(my_investment_analysis.all_category_balance.head())
# df_fuzhu = my_investment_analysis.all_category_balance[['期间', '辅助分类', '金额']]
# fuzhu_group = df_fuzhu.loc[df_fuzhu['期间'] == '2020-08-01'].groupby(['辅助分类'])
# df_fuzhu_balance = fuzhu_group.sum()
# # print(df_fuzhu_balance.loc[['A股', '其它', '可转债', '海外成熟市场股票'], :].sum())
#
# df_fuzhu_item = my_investment_analysis.all_category_balance[['期间', '辅助分类', '项目名称', '金额']]
# df_fuzhu_item = df_fuzhu_item.loc[df_fuzhu_item['期间'] == '2020-08-01']
# df_fuzhu_item = df_fuzhu_item.loc[df_fuzhu_item['辅助分类'] == '货币类']
#
# print(df_fuzhu_item.sum()-249085.25)