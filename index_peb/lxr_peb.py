import requests
import json
import pandas as pd
import utility

url = "https://open.lixinger.com/api/a/index/fundamental"
index_list = [
    # "000905",
    # "000300",
    # "000922",
    # "000903",
    # "399006",
    # "000933",
    # "000931",
    # "000935",
    # "399995",
    # "399971",
    # "399967",
    # "000807",
    # "000992",
    # "399812",
    "000827",
    "000990",
    "399975",
    "399001",
    "000016",
    "000852",
    "1000004",
    "1000002",
    "000906"
]

for index_code in index_list:
    print("processing %s ... " % index_code)
    params = {
        "token": "1364169b-e34f-41ab-95eb-094a10638652",
        "startDate": "2005-01-01",
        "endDate": "2020-12-01",
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
            "pb.median"
        ]
    }
    headers = {"Content-Type": "application/json"}
    res = requests.post(url=url, data=json.dumps(params), headers=headers)
    dt = res.json()
    print("get data from lxr... %s... " % dt['message'])
    if dt['message'] == 'success':
        df = pd.DataFrame([], columns=['date', 'close', 'pe_mcw', 'pe_ew', 'pe_ewpvo', 'pe_avg', 'pe_median', 'pb_mcw',
                                       'pb_ew', 'pb_ewpvo', 'pb_avg', 'pb_median'])
        code = dt['data'][0]['stockCode']
        if code == '1000004':
            code = '000001'
        if code == '1000002':
            code = '000985'

        for item in dt['data']:
            try:
                close = item['cp']
            except:
                close = 0
            finally:
                df = df.append({
                    'date': item['date'],
                    'close': close,
                    'pe_mcw': item['pe_ttm']['mcw'],
                    'pe_ew': item['pe_ttm']['ew'],
                    'pe_ewpvo': item['pe_ttm']['ewpvo'],
                    'pe_median': item['pe_ttm']['median'],
                    'pe_avg': item['pe_ttm']['avg'],
                    'pb_mcw': item['pb']['mcw'],
                    'pb_ew': item['pb']['ew'],
                    'pb_ewpvo': item['pe_ttm']['ewpvo'],
                    'pb_median': item['pb']['median'],
                    'pb_avg': item['pb']['avg']
                }, ignore_index=True)
        df.to_csv('%s/index_peb/%s_peb.csv' % (utility.DATA_ROOT, utility.convert_code_2_csvfilename(code)),
                  index=False)
