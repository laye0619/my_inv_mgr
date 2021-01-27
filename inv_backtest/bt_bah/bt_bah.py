from datetime import timedelta

from rqalpha.apis import *
import utility

__config__ = {
    "base": {
        "accounts": {
            "STOCK": 10000 * 10000,
        },
        "data-bundle-path": "/Users/i335644/.rqalpha/bundle",
        "start_date": "20130101",
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
    context.p_CHECK_DATE = pd.date_range(context.config.base.start_date, context.config.base.end_date, freq='d')
    context.p_bah_FIRED = False
    context.p_bah_INDEX_LIST = [
        '000300.XSHG',
        '000905.XSHG',
        '399006.XSHE',
        '000933.XSHG',
        '000935.XSHG',
        '000990.XSHG',
    ]
    context.p_bah_THRESHOLD = 0.0
    context.p_bah_EMOTIONTHRESHOLD = len(context.p_bah_INDEX_LIST) / 1.5
    context.p_bah_EMOTIONPERIOD = 20


def handle_bar(context, bar_dict):
    if pd.to_datetime(context.now.date()) not in context.p_CHECK_DATE:
        return
    if not context.p_bah_FIRED:
        logger.info('Init building position...')
        cash = context.portfolio.cash
        for index_code in context.p_bah_INDEX_LIST:
            order_target_value(index_code, cash / len(context.p_bah_INDEX_LIST))  # 按比例初始建仓
        context.p_bah_FIRED = True
        return
    logger.info('Strategy executing...')
    __trans_bah(context)


def __trans_bah(context):
    negative_number = 0
    for index_code in context.p_bah_INDEX_LIST:
        df_price = pd.DataFrame(history_bars(index_code, bar_count=50, frequency='1d', fields=['datetime', 'close']))
        df_price['datetime'] = pd.to_datetime(df_price['datetime'], format="%Y%m%d%H%M%S")
        up = (
                (df_price.iloc[-2].close - df_price.iloc[-2 - context.p_bah_EMOTIONPERIOD].close)
                / df_price.iloc[-2 - context.p_bah_EMOTIONPERIOD].close
                * 100
        )
        if up < context.p_bah_THRESHOLD:
            negative_number += 1
    if negative_number >= context.p_bah_EMOTIONTHRESHOLD:  # 大盘情绪不好，清仓
        if len(get_positions()) == 0:
            return
        for position in get_positions():
            if position.direction == POSITION_DIRECTION.LONG:
                order_target_value(position.order_book_id, 0)
    else:
        if len(get_positions()) == 0:
            for index_code in context.p_bah_INDEX_LIST:
                cash = context.portfolio.cash
                order_target_value(index_code, cash / len(context.p_bah_INDEX_LIST))


def get_target_value(context, index_code):
    return context.p_target_value_MARKET_VALUE[index_code] * (1 + context.p_target_value_INDEX_DICT[index_code])
