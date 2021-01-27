from rqalpha.apis import *
import utility

__config__ = {
    "base": {
        "accounts": {
            "STOCK": 10000 * 10000,
        },
        "data-bundle-path": "/Users/i335644/.rqalpha/bundle",
        "start_date": "20120101",
        "end_date": "20201231",
    },
    "extra": {
        "log_level": "info",
    },
    "mod": {
        "sys_analyser": {
            "plot": True,
            "benchmark": "000300.XSHG",
            "report_save_path": '%s/backtest/' % utility.REPORT_ROOT,
        },
        'sys_simulation': {
            'volume_limit': False,  # 成交量限制，因为买指数，按指数成交，所有金额较大，关闭成交量限制
        },
        'sys_transaction_cost': {
            'commission_multiplier': 0.2  # 默认是万8，实际上是万1.5
        }
    }
}


def init(context):
    context.p_CHECK_DATE = pd.date_range(context.config.base.start_date, context.config.base.end_date, freq='BM')
    context.p_target_value_FIRED = False
    context.p_target_value_INDEX_DICT = {
        '000300.XSHG': 0.1 / 12,
        '000905.XSHG': 0.12 / 12,
        '399006.XSHE': 0.15 / 12,
        '000933.XSHG': 0.15 / 12,
        '000935.XSHG': 0.15 / 12,
        '000990.XSHG': 0.20 / 12,
    }
    context.p_target_value_INIT_POSITION_LEVEL = 0.8
    context.p_target_value_MARKET_VALUE = {}


def handle_bar(context, bar_dict):
    if pd.to_datetime(context.now.date()) not in context.p_CHECK_DATE:
        return
    if not context.p_target_value_FIRED:
        logger.info('Init building position...')
        cash = context.portfolio.cash * context.p_target_value_INIT_POSITION_LEVEL
        for index_code in context.p_target_value_INDEX_DICT.keys():
            order_target_value(index_code, cash / len(context.p_target_value_INDEX_DICT))  # 按比例初始建仓
            context.p_target_value_MARKET_VALUE[index_code] = get_position(index_code).market_value  # 记录当期仓位
        context.p_target_value_FIRED = True
        return
    logger.info('Strategy executing...')
    __trans_target_value(context)


def __trans_target_value(context):
    for index_code in context.p_target_value_INDEX_DICT.keys():
        target_value = get_target_value(context, index_code)
        order_target_value(index_code, target_value)
        context.p_target_value_MARKET_VALUE[index_code] = get_position(index_code).market_value  # 记录当期仓位
    pass


def get_target_value(context, index_code):
    return context.p_target_value_MARKET_VALUE[index_code] * (1 + context.p_target_value_INDEX_DICT[index_code])
