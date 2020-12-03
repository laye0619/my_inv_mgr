import os
import pandas as pd

__curPath = os.path.abspath(os.path.dirname(__file__))
__rootPath = __curPath[:__curPath.find("my_backtest/") + len("my_backtest/")]
DATA_ROOT = os.path.abspath(__rootPath + '/02_data/')
PARAMS_ROOT = os.path.abspath(__rootPath + '/01_params/')
REPORT_ROOT = os.path.abspath(__rootPath + '/03_report/')


# 返回params目录下面的
def read_params():
    df_params_details = pd.read_excel('%s/01_params.xlsx' % PARAMS_ROOT, sheet_name='details', dtype='str')
    df_params_strategy = pd.read_excel('%s/01_params.xlsx' % PARAMS_ROOT, sheet_name='strategy', dtype='str')
    return df_params_details, df_params_strategy


def convert_code_2_rqcode(code):
    details, _ = read_params()
    code_mkt = details.loc[details['index_code'] == code, 'index_mkt'].iloc[0]
    mkt_rqcode = '.XSHG' if code_mkt == 'SH' else '.XSHE'
    return code + mkt_rqcode


def convert_code_2_tusharecode(code):
    details, _ = read_params()
    code_mkt = details.loc[details['index_code'] == code, 'index_mkt'].iloc[0]
    mkt_tusharecode = '.SH' if code_mkt == 'SH' else '.SZ'
    return code + mkt_tusharecode


def back_2_original_code(code):
    return code[:6]

    # cal_method = 1: 整体法，市值加权
    # cal_method = 2: 等权，亏损置零
    # cal_method = 3: 中位数，无需预处理
    # cal_method = 4: 算数平均，取分位数95%置信区间
    # Be default, cal_method = None: get all of the method


def update_pe_pb_2_csv():
    df_params_details, df_params_strategy = read_params()
    code_list = df_params_details['index_code'].apply(convert_code_2_rqcode)

