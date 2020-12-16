from rqalpha.apis import *
import utility
from index_peb.lxr_peb_analysis import get_indexes_mul_date_by_field
from datetime import timedelta

__config__ = {
    "base": {
        "accounts": {
            "STOCK": 1000 * 10000,
        },
        "data-bundle-path": "/Users/i335644/.rqalpha/bundle",
        "start_date": "20130101",
        "end_date": "20200630",
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
    # set inv by pe pb 01_params
    context.p_inv_by_pe_pb_AIM0 = '000022.XSHG'
    context.p_inv_by_pe_pb_AIM_LIST = context.p_index_details.loc[
        context.p_index_details['strategy'] == 'InvByPePb', 'index_code'].apply(utility.convert_code_2_rqcode)
    context.p_inv_by_pe_pb_LOW_THRESHOLD = 0.2  # 买入估值条件阈值
    context.p_inv_by_pe_pb_HIGH_THRESHOLD = 0.85  # 卖出估值条件阈值
    context.p_inv_by_pe_pb_CALL_METHOD = 'pe_ttm_y10_median'
    context.p_inv_by_pe_pb_PEB_LEVEL = __get_peb_level(context)


def handle_bar(context, bar_dict):
    # 首次建仓
    if not context.fired:
        logger.info('首次建仓...')
        inv_by_pe_pb_amount = context.config.base.accounts['STOCK'] * context.p_TOTAL_VALUE_BUFFER
        order_target_value(context.p_inv_by_pe_pb_AIM0, inv_by_pe_pb_amount)
        context.fired = True

    if pd.to_datetime(context.now.date()) not in context.p_CHECK_DATE:
        return
    logger.info('每周执行所有策略 - 底仓估值策略...')
    __trans_inv_by_pe_pb(context)


# 根据估值底仓策略
def __trans_inv_by_pe_pb(context):
    index_pe_pb_level = context.p_inv_by_pe_pb_PEB_LEVEL.loc[
        context.p_inv_by_pe_pb_PEB_LEVEL.index < context.now.date().strftime('%Y-%m-%d')].iloc[-1]
    current_holding = __get_current_holding(context.p_inv_by_pe_pb_AIM_LIST)
    num_holding = len(current_holding)
    num_all = len(context.p_inv_by_pe_pb_AIM_LIST)

    to_buy = index_pe_pb_level.loc[index_pe_pb_level <= context.p_inv_by_pe_pb_LOW_THRESHOLD].index.values
    to_sell = index_pe_pb_level.loc[index_pe_pb_level >= context.p_inv_by_pe_pb_HIGH_THRESHOLD].index.values

    for sell_code in to_sell:  # 卖出
        sell_rqcode = utility.convert_code_2_rqcode(sell_code)
        if sell_rqcode in current_holding['基金代码'].tolist():  # 有持仓，卖出
            to_sell_value = get_position(sell_rqcode).market_value
            order_value(sell_rqcode, -to_sell_value)
            order_value(context.p_inv_by_pe_pb_AIM0, to_sell_value)

    for buy_code in to_buy:  # 买入
        buy_rqcode = utility.convert_code_2_rqcode(buy_code)
        if buy_rqcode not in current_holding['基金代码'].tolist():  # 没有持仓，买入
            to_buy_value = get_position(context.p_inv_by_pe_pb_AIM0).market_value / (num_all - num_holding)
            order_value(context.p_inv_by_pe_pb_AIM0, -to_buy_value)
            order_value(buy_rqcode, to_buy_value)


# 取回指数列表中指数在回测日期范围内的给定参数的百分位
def __get_peb_level(context):
    field_param = context.p_inv_by_pe_pb_CALL_METHOD + '_cvpos'
    start_date = context.config.base.start_date - timedelta(10)
    df = get_indexes_mul_date_by_field(context.p_inv_by_pe_pb_AIM_LIST.apply(utility.back_2_original_code).tolist(),
                                       start_date=start_date.strftime('%Y%m%d'),
                                       end_date=context.config.base.end_date.strftime('%Y%m%d'),
                                       field=field_param)
    return df


# 公共函数
# 取得当前持仓
def __get_current_holding(index_list):
    current_holding = pd.DataFrame([], columns=['基金代码', '基金现值'])
    current_all_holding = get_positions()
    for holding in current_all_holding:
        if holding.order_book_id in index_list.values and holding.direction == POSITION_DIRECTION.LONG:
            current_holding = current_holding.append([{'基金代码': holding.order_book_id, '基金现值': holding.market_value}],
                                                     ignore_index=True)
    return current_holding
