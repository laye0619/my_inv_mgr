from rqalpha.apis import *

__config__ = {
    "base": {
        "accounts": {
            "STOCK": 10 * 10000,
        },
        "02_data-bundle-path": "/Users/i335644/.rqalpha/bundle",
        "start_date": "20080101",
        "end_date": "20201111",
    },
    "extra": {
        "log_level": "info",
    },
    "mod": {
        "sys_analyser": {
            "plot": True,
            "benchmark": "000300.XSHG",
            "report_save_path": "03_report",
        }
    }
}


def init(context):
    context.fired = False


def handle_bar(context, bar_dict):
    if not context.fired:
        order_target_percent("000300.XSHG", 0.5)
        context.fired = True
