import concurrent.futures
import multiprocessing
import glob
from datetime import datetime, timedelta

import pandas as pd

from rqalpha import run

start_date = pd.to_datetime('2011-01-01')
each_period_years = 3
df_result = pd.DataFrame()
check_date = pd.date_range(start_date, datetime.now().date(), freq='W-THU')

tasks = []
for date in check_date:
    end_date = date + timedelta(each_period_years * 365)
    if end_date > datetime.now():
        break
    config = {
        "base": {
            "accounts": {
                "STOCK": 1000 * 10000,
            },
            "data-bundle-path": "/Users/i335644/.rqalpha/bundle",
            "start_date": date.strftime('%Y%m%d'),
            "end_date": end_date.strftime('%Y%m%d'),
            "strategy_file": "bt_t28_wo_bond.py",
        },
        "mod": {
            "sys_progress": {
                "enabled": True,
                "show": True,
            },
            "sys_analyser": {
                "enabled": True,
                "plot": False,
                "output_file": "3_year_test_result/t_28_wo_bond_out-{start_date}.pkl".format(
                    start_date=date.strftime('%Y%m%d'),
                )
            },
            'sys_simulation': {
                'volume_limit': False,  # 成交量限制，因为买指数，按指数成交，所有金额较大，关闭成交量限制
            },
            'sys_transaction_cost': {
                'commission_multiplier': 0.2  # 默认是万8，实际上是万1.5
            }
        },
    }
    tasks.append(config)


def run_bt(config):
    run(config)


def get_analysis_result():
    years = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days / 365
    results = []

    for name in glob.glob("3_year_test_result/*.pkl"):
        result_dict = pd.read_pickle(name)
        summary = result_dict["summary"]
        trades = result_dict['trades']
        results.append({
            "name": name,
            "annualized_returns": summary["annualized_returns"],
            "sharpe": summary["sharpe"],
            "max_drawdown": summary["max_drawdown"],
            "trade_times_per_year": round(len(trades) / years, 1),
            "alpha": summary["alpha"],
            "total_returns": summary["total_returns"],
        })

    return pd.DataFrame(results)


if __name__ == '__main__':
    with concurrent.futures.ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        for task in tasks:
            executor.submit(run_bt, task)
    get_analysis_result().sort_values(by='sharpe', ascending=False).to_excel(
        '3_year_test_result/bt_t28_wo_bond_3years.xlsx', index=0)
