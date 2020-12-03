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


t28_result = run_file('./bt_t28.py', __config__)
t_ind_result = run_file('bt_t_ind.py', __config__)
inv_by_pe_pb_result = run_file('./bt_inv_by_pe_pb.py', __config__)
portfolio_result = run_file('./bt_portfolio.py', __config__)
portfolio_position_ctl_result = run_file('./bt_portfolio_position_ctl.py', __config__)

df_result = pd.DataFrame()
df_result = df_result.append(t28_result['sys_analyser']['summary'], ignore_index=True)
df_result = df_result.append(t_ind_result['sys_analyser']['summary'], ignore_index=True)
df_result = df_result.append(inv_by_pe_pb_result['sys_analyser']['summary'], ignore_index=True)
df_result = df_result.append(portfolio_result['sys_analyser']['summary'], ignore_index=True)
df_result = df_result.append(portfolio_position_ctl_result['sys_analyser']['summary'], ignore_index=True)

df_result.to_excel('%s/backtest/mul_strategies_result.xlsx' % utility.REPORT_ROOT)
