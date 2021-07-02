from datetime import timedelta

import xalpha as xa
from xalpha.cons import yesterdayobj
import utility as utility
import pandas as pd


# 生成上一交易日分析df
def get_my_inv_analysis(type='open', totmoney=None):
    _, ex_record_df, in_record_df = utility.read_params(file='Inv_Asset_Record')
    ex_record_df = ex_record_df[ex_record_df.date != 'tobedeleted']

    ex_record = xa.record(path=ex_record_df, fund_property=True)
    in_record = xa.irecord(path=in_record_df)

    if type == 'open':
        result = xa.mul(status=ex_record, istatus=in_record)
    elif type == 'fix':
        result = xa.mulfix(status=ex_record, istatus=in_record, totmoney=totmoney)
    return result


# 生成上一交易日分析以及月结模版df
def generate_my_inv_month_end_closing(df_analysis, period, analysis_date):
    df_month_end_closing_template = df_analysis[df_analysis.基金名称 != '总计']
    df_month_end_closing_template = df_month_end_closing_template[['基金名称', '基金代码', '基金现值']]
    df_month_end_closing_template.rename(columns={'基金名称': '项目', '基金代码': '代码', '基金现值': '现值'}, inplace=True)
    master_data, _, _ = utility.read_params(file='Inv_Asset_Record')
    master_data = master_data[master_data['Validation'] == 'Y']  # 删除所有不在用的投资项目
    non_fund_list = master_data.loc[master_data['code'].isna(), 'name']
    for name in non_fund_list:
        df_month_end_closing_template = df_month_end_closing_template.append({'项目': name}, ignore_index=True)

    type1_list = []
    type2_list = []
    type3_list = []
    for index, row in df_month_end_closing_template.iterrows():
        type1 = master_data.loc[master_data['name'] == row['项目'], 'type_1'].iloc[0]
        type1_list.append(type1)
        type2 = master_data.loc[master_data['name'] == row['项目'], 'type_2'].iloc[0]
        type2_list.append(type2)
        type3 = master_data.loc[master_data['name'] == row['项目'], 'type_3'].iloc[0]
        type3_list.append(type3)
    df_month_end_closing_template['分类1'] = type1_list
    df_month_end_closing_template['分类2'] = type2_list
    df_month_end_closing_template['分类3'] = type3_list
    df_month_end_closing_template['期间'] = period
    df_month_end_closing_template['记录日期'] = analysis_date
    df_month_end_closing_template = df_month_end_closing_template[['期间', '记录日期', '项目', '代码', '分类1', '分类2', '分类3', '现值']]
    return df_month_end_closing_template


# 交易日分析以及月结模版，存储在report文件夹下
def save_analysis_and_month_end_closing_template(period, date=None):
    '''
    :param period: YYYY/MM
    :param date: pd.to_datetime('YYYY-MM-DD')
    :return:
    '''
    if date is None:
        date = yesterdayobj()
    sys_open = get_my_inv_analysis(type='open')
    df_analysis = sys_open.combsummary(date=date).sort_values(by="基金现值", ascending=False)
    df_analysis = df_analysis[df_analysis['基金现值'] != 0]
    df_month_end_closing_template = generate_my_inv_month_end_closing(df_analysis, period=period,
                                                                      analysis_date=date.strftime('%Y/%m/%d'))
    df_month_end_closing_template = utility.convert_float_for_dataframe_columns(df_month_end_closing_template, ['现值'])
    writer = pd.ExcelWriter(
        "%s/my_inv_analysis/month_end_closing_%s.xlsx" % (utility.REPORT_ROOT, date.strftime('%Y%m%d')),
        engine='openpyxl')
    df_month_end_closing_template.to_excel(writer, "month_end_closing", index=0)
    df_analysis.to_excel(writer, "analysis", index=0, float_format="%.2f")
    writer.save()


# 增量更新每周五资产记录：03_report/my_inv_analysis/weekly_inv_report.xlsx
def update_weekly_inv_report():
    # 取出现有文件
    current_df = pd.read_excel('%s/my_inv_analysis/weekly_inv_report.xlsx' % utility.REPORT_ROOT, sheet_name='data')
    last_date = pd.to_datetime(current_df['日期'].iloc[-1], format='%Y/%m/%d') + timedelta(1)

    date_list = pd.date_range(start=last_date, end=yesterdayobj(), freq='W-FRI')
    for date in date_list:
        print('processing date: %s...' % date.strftime('%Y%m%d'))
        sys_open = get_my_inv_analysis(type='open')
        df_analysis = sys_open.combsummary(date=date).sort_values(by="基金现值", ascending=False)
        df_analysis = df_analysis[df_analysis.基金名称 != '总计']
        df_analysis['日期'] = date.strftime('%Y/%m/%d')
        current_df = pd.concat([current_df, df_analysis])
    current_df.to_excel('%s/my_inv_analysis/weekly_inv_report.xlsx' % utility.REPORT_ROOT, sheet_name='data', index=0,
                        float_format="%.2f")


if __name__ == '__main__':
    save_analysis_and_month_end_closing_template(period='2021/06')
    # update_weekly_inv_report()

    # inv_report = get_my_inv_analysis()
    # inv_report.combsummary().to_excel('report.xlsx', index=0)
    pass
