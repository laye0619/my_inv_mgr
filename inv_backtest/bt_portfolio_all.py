from rqalpha.apis import *
import utility
from datetime import timedelta

__config__ = {
    "base": {
        "accounts": {
            "STOCK": 1000 * 10000,
        },
        "data-bundle-path": "/Users/i335644/.rqalpha/bundle",
        "start_date": "20200901",
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


def __set_params(context):
    # set overall 01_params
    context.p_index_details, context.p_index_strategy = utility.read_params(file='bt_params')
    context.p_CHECK_DATE = pd.date_range(context.config.base.start_date, context.config.base.end_date, freq='W-THU')
    context.p_TOTAL_VALUE_BUFFER = 0.99  # 留XX的钱给手续费倒腾

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

    # set tendency industry 01_params
    context.p_t_ind_AIM0 = '399481.XSHE'
    context.p_t_ind_AIM_LIST = context.p_index_details.loc[
        context.p_index_details['strategy'] == 'IndustrialTendency', 'index_code'].apply(utility.convert_code_2_rqcode)
    context.p_t_ind_POSITION_RATIO = float(context.p_index_strategy.loc[
                                               context.p_index_strategy[
                                                   'strategy'] == 'IndustrialTendency', 'position_level'].iloc[0])
    context.p_t_ind_PREV = 20  # 这三个参数：判断有NUM_OF_BIG_THAN个指数，PREV天的涨幅，大于UP_THRESHOLD，则买入，否则清仓
    context.p_t_ind_UP_THRESHOLD = 3  # 这三个参数：判断有NUM_OF_BIG_THAN个指数，PREV天的涨幅，大于UP_THRESHOLD，则买入，否则清仓
    context.p_t_ind_NUM_OF_BIG_THAN = 4  # 这三个参数：判断有NUM_OF_BIG_THAN个指数，PREV天的涨幅，大于UP_THRESHOLD，则买入，否则清仓
    context.p_t_ind_INDEX_NUMBER = 2  # 每次持仓的指数数量

    # set inv by pe pb 01_params
    context.p_inv_by_pe_pb_AIM0 = '000022.XSHG'
    context.p_inv_by_pe_pb_AIM_LIST = context.p_index_details.loc[
        context.p_index_details['strategy'] == 'InvByPePb', 'index_code'].apply(utility.convert_code_2_rqcode)
    context.p_inv_by_pe_pb_LOW_THRESHOLD = 0.05  # 买入估值条件阈值
    context.p_inv_by_pe_pb_HIGH_THRESHOLD = 0.98  # 卖出估值条件阈值
    context.p_inv_by_pe_pb_DECIDE_BY = 'PE'
    context.p_inv_by_pe_pb_CALL_METHOD = 2  # which pe & pb calculation method
    context.p_inv_by_pe_pb_PERIOD = 5  # 估值百分位长度 默认5年
    context.p_inv_by_pe_pb_POSITION_RATIO = float(
        context.p_index_strategy.loc[context.p_index_strategy['strategy'] == 'InvByPePb', 'position_level'].iloc[0])


def init(context):
    logger.info('初始化参数设置...')
    __set_params(context)  # 设置参数
    context.fired = False


def handle_bar(context, bar_dict):
    # 首次建仓
    if not context.fired:
        logger.info('首次建仓...')
        t_ind_amount = context.config.base.accounts[
                           'STOCK'] * context.p_TOTAL_VALUE_BUFFER * context.p_t_ind_POSITION_RATIO
        order_target_value(context.p_t_ind_AIM0, t_ind_amount)
        inv_by_pe_pb_amount = context.config.base.accounts[
                                  'STOCK'] * context.p_TOTAL_VALUE_BUFFER * context.p_inv_by_pe_pb_POSITION_RATIO
        order_target_value(context.p_inv_by_pe_pb_AIM0, inv_by_pe_pb_amount)
        t28_amount = context.config.base.accounts['STOCK'] * context.p_TOTAL_VALUE_BUFFER * context.p_t28_POSITION_RATIO
        order_target_value(context.p_t28_AIM0, t28_amount)
        context.fired = True

    if pd.to_datetime(context.now.date()) not in context.p_CHECK_DATE:
        return
    logger.info('每周执行组合策略')
    __trans_tendeccy_ind(context)
    __trans_inv_by_pe_pb(context)
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


# 行业轮动策略
def __trans_tendeccy_ind(context):
    series_dongliang = __calc_index_dongliang(context.p_t_ind_AIM_LIST, context)
    current_holding = __get_current_holding(series_dongliang.index)
    list_to_buy_value = []  # 当卖出时，临时记录金额，买入时候取出金额

    if len(series_dongliang.loc[
               series_dongliang > context.p_t_ind_UP_THRESHOLD]) >= context.p_t_ind_NUM_OF_BIG_THAN:  # 指数有XX是正的，才买基金
        if len(current_holding['基金现值']) == 0:  # 当前没有持仓，按比例买基金
            to_buy_list = series_dongliang[0:context.p_t_ind_INDEX_NUMBER].index.tolist()
            each_value = get_position(context.p_t_ind_AIM0,
                                      POSITION_DIRECTION.LONG).market_value / context.p_t_ind_INDEX_NUMBER
            order_target_value(context.p_t_ind_AIM0, 0)
            for code in to_buy_list:
                order_target_value(code, each_value)
        else:  # 当前有持仓，检查持仓品种，确定调仓
            holding_list = current_holding['基金代码'].values.tolist()
            target_compare_list = series_dongliang[0:context.p_t_ind_INDEX_NUMBER * 2].index.tolist()
            for code in holding_list:
                if code in target_compare_list:  # 保持不操作
                    continue
                else:  # 卖掉并更新基金现值
                    list_to_buy_value.append(current_holding.loc[current_holding['基金代码'] == code, '基金现值'].iloc[0])
                    order_target_value(code, 0)
                    holding_list.remove(code)
            while len(holding_list) < context.p_t_ind_INDEX_NUMBER:  # 按照排名买入，补足基金数量
                for code in target_compare_list:
                    if code not in holding_list:
                        order_target_value(code, list_to_buy_value[0])
                        del list_to_buy_value[0]
                        holding_list.append(code)
                        break
    else:  # 形势不好，清仓基金
        each_value = current_holding['基金现值'].sum()
        if each_value != 0:  # 有持仓，清空
            for index, row in current_holding.iterrows():
                order_target_value(row['基金代码'], 0)
            order_target_value(context.p_t_ind_AIM0, each_value)


# 计算行业轮动策略动量
def __calc_index_dongliang(target_list, context):
    series_dongliang = pd.Series()
    for code in target_list:
        if context.now < pd.to_datetime(context.p_index_details.loc[
                                            context.p_index_details['index_code'] == utility.back_2_original_code(
                                                code), 'index_starts'].iloc[0]):
            continue
        df_price = history_bars(code, context.p_t_ind_PREV, '1d', 'close')
        up = ((df_price[-1] - df_price[0]) / df_price[0] * 100)
        series_dongliang[code] = up
    series_dongliang.sort_values(ascending=False, inplace=True)
    return series_dongliang


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
