import os
import pandas as pd

__curPath = os.path.abspath(os.path.dirname(__file__))
__rootPath = __curPath[:__curPath.find("my_inv_mgr") + len("my_inv_mgr/")]
DATA_ROOT = os.path.abspath(__rootPath + '/02_data/')
PARAMS_ROOT = os.path.abspath(__rootPath + '/01_params/')
REPORT_ROOT = os.path.abspath(__rootPath + '/03_report/')


# 返回params目录下面的
def read_params(file):
    if file == 'bt_params':
        df_params_details = pd.read_excel('%s/%s.xlsx' % (PARAMS_ROOT, file), sheet_name='details', dtype='str')
        df_params_strategy = pd.read_excel('%s/%s.xlsx' % (PARAMS_ROOT, file), sheet_name='strategy', dtype='str')
        return df_params_details, df_params_strategy
    if file == 'Inv_Asset_Analysis':
        master_data = pd.read_excel('%s/Inv_Asset_Analysis.xlsx' % PARAMS_ROOT, sheet_name='MasterData',
                                    dtype='str')
        ex_record_df = pd.read_excel('%s/Inv_Asset_Analysis.xlsx' % PARAMS_ROOT, sheet_name='E_TransRecord')
        in_record_df = pd.read_excel('%s/Inv_Asset_Analysis.xlsx' % PARAMS_ROOT, sheet_name='I_TransRecord')
        return master_data, ex_record_df, in_record_df


def convert_code_2_rqcode(code):
    details, _ = read_params(file='bt_params')
    code_mkt = details.loc[details['index_code'] == code, 'index_mkt'].iloc[0]
    mkt_rqcode = '.XSHG' if code_mkt == 'SH' else '.XSHE'
    return code + mkt_rqcode


def convert_code_2_tusharecode(code):
    details, _ = read_params(file='bt_params')
    code_mkt = details.loc[details['index_code'] == code, 'index_mkt'].iloc[0]
    mkt_tusharecode = '.SH' if code_mkt == 'SH' else '.SZ'
    return code + mkt_tusharecode


def convert_code_2_xalphacode(code):
    details, _ = read_params(file='bt_params')
    code_mkt = details.loc[details['index_code'] == code, 'index_mkt'].iloc[0]
    mkt_xalphacode = '0' if code_mkt == 'SH' else '1'
    return mkt_xalphacode + code


def convert_code_2_csvfilename(code):
    details, _ = read_params(file='bt_params')
    code_mkt = details.loc[details['index_code'] == code, 'index_mkt'].iloc[0]
    mkt_csvfilenamecode = 'sh' if code_mkt == 'SH' else 'sz'
    return mkt_csvfilenamecode + code


def back_2_original_code(code):
    return code[:6]


def get_name_from_ori_code(code):
    details, _ = read_params(file='bt_params')
    return details.loc[details['index_code'] == code, 'index_name'].iloc[0]


def get_cn_desc_from_index_peb_field(field_name):
    result = pd.read_csv('%s/index_peb/data_dict.csv' % DATA_ROOT)
    return result.loc[result['Field'] == field_name, 'Desc'].iloc[0]


if __name__ == '__main__':
    desc = get_cn_desc_from_index_peb_field('pb_fs_avg_cvpos')
    pass
