from rqalpha.apis import *
import utility

__config__ = {
    "base": {
        "accounts": {
            "STOCK": 1000 * 10000,
        },
        "data-bundle-path": "/Users/i335644/.rqalpha/bundle",
        "start_date": "20130101",
        "end_date": "20201208",
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
    context.fired = False
    context.p_index_details, context.p_index_strategy = utility.read_params()
    context.p_CHECK_DATE = pd.date_range(context.config.base.start_date, context.config.base.end_date, freq='W-THU')
    context.p_TOTAL_VALUE_BUFFER = 0.99  # 留1%的钱给手续费倒腾
    # set tendency28 01_params
    context.p_t28_AIM1 = utility.convert_code_2_rqcode(
        context.p_index_details.loc[context.p_index_details['strategy'] == 'Tendency28', 'index_code'].iloc[0])
    context.p_t28_AIM2 = utility.convert_code_2_rqcode(
        context.p_index_details.loc[context.p_index_details['strategy'] == 'Tendency28', 'index_code'].iloc[1])
    context.p_t28_AIM0 = '000012.XSHG'
    context.p_t28_UP_THRESHOLD = 0.5
    context.p_t28_DIFF_THRESHOLD = 1.0
    context.p_t28_PREV = 20
    context.p_t28_STATUS = 0  # having status
    context.p_t28_POSITION_RATIO = float(
        context.p_index_strategy.loc[context.p_index_strategy['strategy'] == 'Tendency28', 'position_level'].iloc[0])


def handle_bar(context, bar_dict):
    # 首次建仓
    if not context.fired:
        logger.info('首次建仓...')
        t28_amount = context.config.base.accounts['STOCK'] * context.p_TOTAL_VALUE_BUFFER
        order_target_value(context.p_t28_AIM0, t28_amount)
        context.fired = True

    if pd.to_datetime(context.now.date()) not in context.p_CHECK_DATE:
        return
    logger.info('每周执行所有策略 - 28轮动...')
    __trans_tendency28(context)


# 28轮动策略
def __trans_tendency28(context):
    df1 = pd.DataFrame(history_bars(context.p_t28_AIM1, bar_count=50, frequency='1d', fields=['datetime', 'close']))
    df1['datetime'] = pd.to_datetime(df1['datetime'], format="%Y%m%d%H%M%S")
    up1 = (
            (df1.iloc[-1].close - df1.iloc[-1 - context.p_t28_PREV].close)
            / df1.iloc[-1 - context.p_t28_PREV].close
            * 100
    )
    df2 = pd.DataFrame(history_bars(context.p_t28_AIM2, bar_count=50, frequency='1d', fields=['datetime', 'close']))
    df2['datetime'] = pd.to_datetime(df2['datetime'], format="%Y%m%d%H%M%S")
    up2 = (
            (df2.iloc[-1].close - df2.iloc[-1 - context.p_t28_PREV].close)
            / df2.iloc[-1 - context.p_t28_PREV].close
            * 100
    )
    if up1 < context.p_t28_UP_THRESHOLD and up2 < context.p_t28_UP_THRESHOLD:
        if context.p_t28_STATUS == 1:
            value = get_position(context.p_t28_AIM1, POSITION_DIRECTION.LONG).market_value
            order_target_value(context.p_t28_AIM1, 0)
            context.p_t28_STATUS = 0
            order_target_value(context.p_t28_AIM0, value)
        elif context.p_t28_STATUS == 2:
            value = get_position(context.p_t28_AIM2, POSITION_DIRECTION.LONG).market_value
            order_target_value(context.p_t28_AIM2, 0)
            context.p_t28_STATUS = 0
            order_target_value(context.p_t28_AIM0, value)
    elif up1 > context.p_t28_UP_THRESHOLD and up1 > up2:
        if context.p_t28_STATUS == 0:
            value = get_position(context.p_t28_AIM0, POSITION_DIRECTION.LONG).market_value
            order_target_value(context.p_t28_AIM0, 0)
            context.p_t28_STATUS = 1
            order_target_value(context.p_t28_AIM1, value)
        elif context.p_t28_STATUS == 2 and up1 - up2 > context.p_t28_DIFF_THRESHOLD:
            value = get_position(context.p_t28_AIM2, POSITION_DIRECTION.LONG).market_value
            order_target_value(context.p_t28_AIM2, 0)
            context.p_t28_STATUS = 1
            order_target_value(context.p_t28_AIM1, value)
    elif up2 > context.p_t28_UP_THRESHOLD and up2 > up1:
        if context.p_t28_STATUS == 0:
            value = get_position(context.p_t28_AIM0, POSITION_DIRECTION.LONG).market_value
            order_target_value(context.p_t28_AIM0, 0)
            context.p_t28_STATUS = 2
            order_target_value(context.p_t28_AIM2, value)
        elif context.p_t28_STATUS == 1 and up2 - up1 > context.p_t28_DIFF_THRESHOLD:
            value = get_position(context.p_t28_AIM1, POSITION_DIRECTION.LONG).market_value
            order_target_value(context.p_t28_AIM1, 0)
            context.p_t28_STATUS = 2
            order_target_value(context.p_t28_AIM2, value)
