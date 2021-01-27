import concurrent.futures
import multiprocessing
import glob
import pandas as pd

from rqalpha import run

start_date = "20130101"
end_date = "20201231"

p_CHECK_DATE_list = [
    pd.date_range(start_date, end_date, freq='d'),
    pd.date_range(start_date, end_date, freq='W-MON'),
    pd.date_range(start_date, end_date, freq='BM'),
]

tasks = []
for p_CHECK_DATE in p_CHECK_DATE_list:
    for p_bah_THRESHOLD in range(-2, 11, 2):
        for p_bah_EMOTIONTHRESHOLD in range(1, 6, 1):
            for p_bah_EMOTIONPERIOD in range(5, 31, 5):
                config = {
                    "extra": {
                        "context_vars": {
                            "p_CHECK_DATE": p_CHECK_DATE,
                            "p_bah_THRESHOLD": p_bah_THRESHOLD,
                            "p_bah_EMOTIONTHRESHOLD": p_bah_EMOTIONTHRESHOLD,
                            "p_bah_EMOTIONPERIOD": p_bah_EMOTIONPERIOD,
                         },
                        "log_level": "error",
                    },
                    "base": {
                        "accounts": {
                            "STOCK": 10000 * 10000,
                        },
                        "data-bundle-path": "/Users/i335644/.rqalpha/bundle",
                        "start_date": start_date,
                        "end_date": end_date,
                        "strategy_file": "bt_bah.py",
                    },
                    "mod": {
                        "sys_progress": {
                            "enabled": True,
                            "show": True,
                        },
                        "sys_analyser": {
                            "enabled": True,
                            "plot": False,
                            "output_file": "param_optimize_result/target_value_out-{p_CHECK_DATE}-{THRESHOLD}-{EMOTIONTHRESHOLD}-{EMOTIONPERIOD}.pkl".format(
                                p_CHECK_DATE=p_CHECK_DATE.freq.freqstr,
                                THRESHOLD=p_bah_THRESHOLD,
                                EMOTIONTHRESHOLD=p_bah_EMOTIONTHRESHOLD,
                                EMOTIONPERIOD=p_bah_EMOTIONPERIOD,
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

    for name in glob.glob("param_optimize_result/*.pkl"):
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
        'param_optimize_result/bt_bah_param_optimize_result.xlsx', index=0)
