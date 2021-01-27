import concurrent.futures
import multiprocessing
import glob
import pandas as pd

from rqalpha import run

start_date = "20130101"
end_date = "20201231"

peb_method_list = [
    'pe_ttm_y10_median', 'pe_ttm_y5_median', 'pe_ttm_y10_mcw', 'pe_ttm_y5_mcw', 'pe_ttm_y10_ewpvo', 'pe_ttm_y5_ewpvo',
    'pb_y10_median', 'pb_y5_median', 'pb_y10_mcw', 'pb_y5_mcw', 'pb_y10_ewpvo', 'pb_y5_ewpvo',
]

tasks = []
for peb_method in peb_method_list:
    for p_inv_by_pe_pb_LOW_THRESHOLD in range(0, 21, 3):
        for p_inv_by_pe_pb_HIGH_THRESHOLD in range(80, 101, 3):
            config = {
                "extra": {
                    "context_vars": {
                        "p_inv_by_pe_pb_CALL_METHOD": peb_method,
                        "p_inv_by_pe_pb_LOW_THRESHOLD": p_inv_by_pe_pb_LOW_THRESHOLD / 100,
                        "p_inv_by_pe_pb_HIGH_THRESHOLD": p_inv_by_pe_pb_HIGH_THRESHOLD / 100,
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
                    "strategy_file": "bt_inv_by_pe_pb.py",
                },
                "mod": {
                    "sys_progress": {
                        "enabled": True,
                        "show": True,
                    },
                    "sys_analyser": {
                        "enabled": True,
                        "plot": False,
                        "output_file": "param_optimize_result/out-{peb_method}-{LOW_THRESHOLD}-{HIGH_THRESHOLD}.pkl".format(
                            peb_method=peb_method,
                            LOW_THRESHOLD=p_inv_by_pe_pb_LOW_THRESHOLD,
                            HIGH_THRESHOLD=p_inv_by_pe_pb_HIGH_THRESHOLD,
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
        'param_optimize_result/bt_inv_by_pe_pb_param_optimize_result.xlsx', index=0)
