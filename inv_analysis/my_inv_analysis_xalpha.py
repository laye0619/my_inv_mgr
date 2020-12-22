import xalpha as xa
from xalpha.cons import yesterdayobj

import utility as utility
import pandas as pd


def get_my_inv_analysis(date=yesterdayobj()):
    ex_record_df = pd.read_excel('%s/my_inv_month_end_closing/Inv_Asset_new.xlsx' % utility.DATA_ROOT,
                                 sheet_name='E_TransRecord')
    ex_record_df = ex_record_df[ex_record_df.date != 'tobedeleted']

    in_record_df = pd.read_excel('%s/my_inv_month_end_closing/Inv_Asset_new.xlsx' % utility.DATA_ROOT,
                                 sheet_name='I_TransRecord')
    ex_record = xa.record(path=ex_record_df, fund_property=True)
    in_record = xa.irecord(path=in_record_df)

    return xa.mul(status=ex_record, istatus=in_record)


date = yesterdayobj()
sys_open = get_my_inv_analysis(date=date)
sys_open.combsummary().sort_values(by="基金现值", ascending=False).to_excel(
    '%s/my_inv_analysis/my_inv_analysis_%s.xlsx' % (utility.REPORT_ROOT, date.strftime('%Y%m%d')),
    index=0)
