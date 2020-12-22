import xalpha as xa
from xalpha.cons import yesterdayobj

import utility as utility
import pandas as pd


def get_my_inv_analysis(date=yesterdayobj()):
    ex_record_df = pd.read_excel('%s/Inv_Asset_Analysis.xlsx' % utility.PARAMS_ROOT, sheet_name='E_TransRecord')
    ex_record_df = ex_record_df[ex_record_df.date != 'tobedeleted']

    in_record_df = pd.read_excel('%s/Inv_Asset_Analysis.xlsx' % utility.PARAMS_ROOT, sheet_name='I_TransRecord')
    ex_record = xa.record(path=ex_record_df, fund_property=True)
    in_record = xa.irecord(path=in_record_df)

    return xa.mul(status=ex_record, istatus=in_record)


def generate_my_inv_month_end_closing(df_analysis, period, analysis_date):
    df_month_end_closing_template = df_analysis[df_analysis.基金名称 != '总计']
    df_month_end_closing_template = df_month_end_closing_template[['基金名称', '基金代码', '基金现值']]
    df_month_end_closing_template.rename(columns={'基金名称': '项目', '基金代码': '代码', '基金现值': '现值'}, inplace=True)
    master_data = pd.read_excel('%s/Inv_Asset_Analysis.xlsx' % utility.PARAMS_ROOT, sheet_name='MasterData',
                                dtype='str')
    non_fund_list = master_data.loc[master_data['code'].isna(), 'name']
    for name in non_fund_list:
        df_month_end_closing_template = df_month_end_closing_template.append({'项目': name}, ignore_index=True)

    type1_list = []
    type2_list = []
    for index, row in df_month_end_closing_template.iterrows():
        type1 = master_data.loc[master_data['name'] == row['项目'], 'type_1'].iloc[0]
        type1_list.append(type1)
        type2 = master_data.loc[master_data['name'] == row['项目'], 'type_2'].iloc[0]
        type2_list.append(type2)
    df_month_end_closing_template['分类1'] = type1_list
    df_month_end_closing_template['分类2'] = type2_list
    df_month_end_closing_template['期间'] = period
    df_month_end_closing_template['记录日期'] = analysis_date
    df_month_end_closing_template = df_month_end_closing_template[['期间', '记录日期', '项目', '代码', '分类1', '分类2', '现值']]
    return df_month_end_closing_template


if __name__ == '__main__':
    date = yesterdayobj()
    sys_open = get_my_inv_analysis(date=date)
    df_analysis = sys_open.combsummary().sort_values(by="基金现值", ascending=False)
    df_month_end_closing_template = generate_my_inv_month_end_closing(df_analysis, period='2020/12',
                                                                      analysis_date=date.strftime('%Y/%m/%d'))
    writer = pd.ExcelWriter(
        "%s/my_inv_analysis/my_inv_analysis_%s.xlsx" % (utility.REPORT_ROOT, date.strftime('%Y%m%d')),
        engine='openpyxl')
    df_analysis.to_excel(writer, "analysis", index=0)
    df_month_end_closing_template.to_excel(writer, "month_end_closing", index=0)
    writer.save()

    pass
