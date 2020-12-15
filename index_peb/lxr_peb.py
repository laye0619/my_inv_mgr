import os
from datetime import date, timedelta

import requests
import json
import pandas as pd
import utility

'''
共有三种形式的指标格式：
[metricsName].[granularity].[metricsType]: 支持指标有 pe_ttm, pb, ps_ttm
[metricsName].[metricsType]: 支持指标有 dyr(股息率), pe_ttm, pb, ps_ttm
[metricsName]: 被剩余的指标支持，如 cp(收盘点位), cpc(涨跌幅), mc(市值)

metricsName
    PE-TTM :pe_ttm
    PB :pb
    PS-TTM :ps_ttm
    股息率 :dyr
    收盘点位 :cp
    全收益收盘点位 :r_cp
    涨跌幅 :cpc
    市值 :mc
    流通市值 :cmc
    融资余额 :fb
    融券余额 :sb
    陆股通持仓金额 :ha_shm
granularity
    所有 :fs
    20年 :y20
    10年 :y10
    5年 :y5
    3年 :y3
metricsType
    市值加权 :mcw
    等权 :ew
    正数等权 :ewpvo
    平均值 :avg
    中位数 :median
'''


def update_data(index_list, end_date=None):
    if end_date is None:
        end_date = date.today() - timedelta(1)
    url = "https://open.lixinger.com/api/a/index/fundamental"
    for index_code in index_codes:
        result_df = pd.DataFrame()  # 最终的结果-全集
        if index_code == '1000004':
            temp_code = '000001'
        elif index_code == '1000002':
            temp_code = '000985'
        else:
            temp_code = index_code
        data_path = '%s/index_peb/%s_peb.csv' % (
            utility.DATA_ROOT, utility.convert_code_2_csvfilename(temp_code))
        if os.path.exists(data_path):  # existed csv file, go update incrementally
            print('incrementally update: %s...' % index_code)
            result_df = pd.read_csv(data_path, parse_dates=True)
            if len(result_df) == 0:
                start_date = pd.to_datetime('2005-01-01')
            else:
                start_date = pd.to_datetime(result_df['date'].iloc[-1]) + timedelta(1)
            if end_date <= start_date:
                continue
        else:
            print('init update: %s...' % index_code)
            start_date = pd.to_datetime('2005-01-01')
        params = {
            "token": "1364169b-e34f-41ab-95eb-094a10638652",
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
            "stockCodes": [index_code],
            "metricsList": [
                "cp",
                "pe_ttm.mcw",
                "pe_ttm.ew",
                "pe_ttm.ewpvo",
                "pe_ttm.avg",
                "pe_ttm.median",
                "pb.mcw",
                "pb.ew",
                "pb.ewpvo",
                "pb.avg",
                "pb.median",
                "pe_ttm.fs.mcw",
                "pe_ttm.fs.ew",
                "pe_ttm.fs.ewpvo",
                "pe_ttm.fs.avg",
                "pe_ttm.fs.median",
                "pb.fs.mcw",
                "pb.fs.ew",
                "pb.fs.ewpvo",
                "pb.fs.avg",
                "pb.fs.median",
                "pe_ttm.y10.mcw",
                "pe_ttm.y10.ew",
                "pe_ttm.y10.ewpvo",
                "pe_ttm.y10.avg",
                "pe_ttm.y10.median",
                "pb.y10.mcw",
                "pb.y10.ew",
                "pb.y10.ewpvo",
                "pb.y10.avg",
                "pb.y10.median",
                "pe_ttm.y5.mcw",
                "pe_ttm.y5.ew",
                "pe_ttm.y5.ewpvo",
                "pe_ttm.y5.avg",
                "pe_ttm.y5.median",
                "pb.y5.mcw",
                "pb.y5.ew",
                "pb.y5.ewpvo",
                "pb.y5.avg",
                "pb.y5.median",
            ]
        }
        headers = {"Content-Type": "application/json"}
        res = requests.post(url=url, data=json.dumps(params), headers=headers)
        dt = res.json()
        if dt['message'] == 'success':
            code = dt['data'][0]['stockCode']
            if code == '1000004':
                code = '000001'
            if code == '1000002':
                code = '000985'

            new_dict = {}
            for date_item in dt['data']:
                for l1_k in date_item:
                    if isinstance(date_item[l1_k], dict):
                        for l2_k in date_item[l1_k]:
                            if isinstance(date_item[l1_k][l2_k], dict):
                                for l3_k in date_item[l1_k][l2_k]:
                                    if isinstance(date_item[l1_k][l2_k][l3_k], dict):
                                        for l4_k in date_item[l1_k][l2_k][l3_k]:
                                            new_dict['%s_%s_%s_%s' % (l1_k, l2_k, l3_k, l4_k)] = \
                                                date_item[l1_k][l2_k][l3_k][l4_k]
                                    else:
                                        new_dict['%s_%s_%s' % (l1_k, l2_k, l3_k)] = date_item[l1_k][l2_k][l3_k]
                            else:
                                new_dict['%s_%s' % (l1_k, l2_k)] = date_item[l1_k][l2_k]
                    else:
                        new_dict[l1_k] = date_item[l1_k]
                result_df = result_df.append(new_dict, ignore_index=True)
            result_df['date'] = result_df['date'].apply(lambda x: x[:10])
            result_df = result_df.sort_values(by=['date'], ignore_index=True)
            result_df.to_csv('%s/index_peb/%s_peb.csv' % (utility.DATA_ROOT, utility.convert_code_2_csvfilename(code)),
                             index=False)


if __name__ == '__main__':
    index_codes, _ = utility.read_params()
    index_codes = index_codes['index_code'].drop_duplicates()
    index_codes = index_codes.replace('000001', '1000004')
    index_codes = index_codes.replace('000985', '1000002')

    update_data(index_codes)
