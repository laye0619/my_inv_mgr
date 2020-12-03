from rqalpha.apis import *
from strategy_backtest import utility as utility
from datetime import timedelta

__config__ = {
    "base": {
        "accounts": {
            "STOCK": 1000 * 10000,
        },
        "02_data-bundle-path": "/Users/i335644/.rqalpha/bundle",
        "start_date": "20130101",
        "end_date": "20201111",
    },
    "extra": {
        "log_level": "info",
    },
    "mod": {
        "sys_analyser": {
            "plot": True,
            "benchmark": "000300.XSHG",
            "report_save_path": utility.REPORT_ROOT,
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
    context.p_inv_by_pe_pb_LOW_THRESHOLD = 0.05  # 买入估值条件阈值
    context.p_inv_by_pe_pb_HIGH_THRESHOLD = 0.98  # 卖出估值条件阈值
    context.p_inv_by_pe_pb_DECIDE_BY = 'PE'
    context.p_inv_by_pe_pb_CALL_METHOD = 2  # which pe & pb calculation method
    context.p_inv_by_pe_pb_PERIOD = 5  # 估值百分位长度 默认5年


def handle_bar(context, bar_dict):
    # 首次建仓
    if not context.fired:
        logger.info('首次建仓...')
        inv_by_pe_pb_amount = context.config.base.accounts['STOCK'] * context.p_TOTAL_VALUE_BUFFER
        '''
        context.p_inv_by_pe_pb_TARGET_DICT = __gen_target_dict(context, inv_by_pe_pb_amount)  # 首次分配底仓比例
        '''
        order_target_value(context.p_inv_by_pe_pb_AIM0, inv_by_pe_pb_amount)
        context.fired = True

    if pd.to_datetime(context.now.date()) not in context.p_CHECK_DATE:
        return
    logger.info('每周执行所有策略 - 底仓估值策略...')
    __trans_inv_by_pe_pb(context)


# 根据估值底仓策略
def __trans_inv_by_pe_pb(context):
    df_index_pe_pb_level = __get_index_pe_pb_level(context)
    if context.p_inv_by_pe_pb_DECIDE_BY == 'PE':
        df_index_level = df_index_pe_pb_level.drop(['pb', 'pb_high', 'pb_low'], axis=1)
    elif context.p_inv_by_pe_pb_DECIDE_BY == 'PB':
        df_index_level = df_index_pe_pb_level.drop(['pe', 'pe_high', 'pe_low'], axis=1)
    current_holding = __get_current_holding(context.p_inv_by_pe_pb_AIM_LIST)
    is_small_than_low = df_index_level.iloc[:, 0] < df_index_level.iloc[:, 1]
    is_big_than_high = df_index_level.iloc[:, 0] > df_index_level.iloc[:, 2]

    num_holding = len(current_holding)
    num_all = len(context.p_inv_by_pe_pb_AIM_LIST)

    for i, v in is_small_than_low.iteritems():
        if v and i not in current_holding['基金代码'].values:  # 没有持仓，买入
            to_buy_value = get_position(context.p_inv_by_pe_pb_AIM0).market_value / (num_all - num_holding)
            order_value(context.p_inv_by_pe_pb_AIM0, -to_buy_value)
            order_value(i, to_buy_value)

    for i, v in is_big_than_high.iteritems():
        if v and i in current_holding['基金代码'].values:  # 持仓，卖出
            to_sell_value = get_position(i).market_value
            order_value(i, -to_sell_value)
            order_value(context.p_inv_by_pe_pb_AIM0, to_sell_value)


# 计算估值底仓策略指数估值
def __get_index_pe_pb_level(context):
    today_date = context.now.date()
    start_date = today_date - timedelta(context.p_inv_by_pe_pb_PERIOD * 365)
    df_result = pd.DataFrame([], columns=['index_code', 'pe', 'pe_low', 'pe_high', 'pb', 'pb_low', 'pb_high'])
    for code in context.p_inv_by_pe_pb_AIM_LIST:
        file_name = ('sh' if context.p_index_details.loc[
                                 context.p_index_details['index_code'] == utility.back_2_original_code(
                                     code), 'index_mkt'].iloc[0] == 'SH' else 'sz') + utility.back_2_original_code(code)
        df_pe_pb = pd.read_csv('%s/index_pe_pb/%s_pe_pb.csv' % (utility.DATA_ROOT, file_name))
        df_pe_pb = df_pe_pb.loc[df_pe_pb['Unnamed: 0'].apply(pd.to_datetime) > pd.Timestamp(start_date)]
        df_pe_pb = df_pe_pb.loc[df_pe_pb['Unnamed: 0'].apply(pd.to_datetime) < pd.Timestamp(today_date)]
        pe_call_method = 'pe%s' % context.p_inv_by_pe_pb_CALL_METHOD
        pb_call_method = 'pb%s' % context.p_inv_by_pe_pb_CALL_METHOD
        pe = df_pe_pb[pe_call_method].iloc[-1]
        pe_low_threshold = df_pe_pb[pe_call_method].quantile(context.p_inv_by_pe_pb_LOW_THRESHOLD)
        pe_high_threshold = df_pe_pb[pe_call_method].quantile(context.p_inv_by_pe_pb_HIGH_THRESHOLD)
        pb = df_pe_pb[pb_call_method].iloc[-1]
        pb_low_threshold = df_pe_pb[pb_call_method].quantile(context.p_inv_by_pe_pb_LOW_THRESHOLD)
        pb_high_threshold = df_pe_pb[pb_call_method].quantile(context.p_inv_by_pe_pb_HIGH_THRESHOLD)
        df_result = df_result.append({'index_code': code,
                                      'pe': pe,
                                      'pe_low': pe_low_threshold,
                                      'pe_high': pe_high_threshold,
                                      'pb': pb,
                                      'pb_low': pb_low_threshold,
                                      'pb_high': pb_high_threshold}, ignore_index=True)
    df_result.set_index(["index_code"], inplace=True)
    return df_result


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
