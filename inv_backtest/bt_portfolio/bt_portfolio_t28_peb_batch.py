from datetime import timedelta, datetime

from rqalpha import run_file
import pandas as pd
import utility

__config__ = {
    "base": {
        "accounts": {
            "STOCK": 1000 * 10000,
        },
        "data-bundle-path": "/Users/i335644/.rqalpha/bundle",
        "start_date": "20130105",
        "end_date": "20201109",
    },
    "extra": {
        "log_level": "info",
    },
    "mod": {
        "sys_analyser": {
            "plot": False,
            "benchmark": "000300.XSHG",
        },
        'sys_simulation': {
            'volume_limit': False,  # 成交量限制，因为买指数，按指数成交，所有金额较大，关闭成交量限制
        },
        'sys_transaction_cost': {
            'commission_multiplier': 0.2  # 默认是万8，实际上是万1.5
        }
    }
}

start_date = pd.to_datetime('2011-01-01')
each_period_years = 5
df_result = pd.DataFrame()
check_date = pd.date_range(start_date, datetime.now().date(), freq='W-THU')

while True:
    if start_date in check_date:
        end_date = start_date + timedelta(each_period_years * 365)
        if end_date > datetime.now():
            break
        print('Processing date: %s...' % start_date.date())
        __config__['base']['start_date'] = start_date.strftime('%Y%m%d')
        __config__['base']['end_date'] = end_date.strftime('%Y%m%d')
        portfolio_result = run_file('bt_portfolio_t28_peb.py', __config__)
        df_result = df_result.append(portfolio_result['sys_analyser']['summary'], ignore_index=True)
    start_date = start_date + timedelta(1)

df_result.to_excel('%s/backtest/bt_portfolio_t28_peb_batch_test_result.xlsx' % utility.REPORT_ROOT)
