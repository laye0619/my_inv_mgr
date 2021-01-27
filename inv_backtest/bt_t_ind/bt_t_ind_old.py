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
    context.fired = False
    context.p_index_details, context.p_index_strategy = utility.read_params(file='bt_params')
    context.p_CHECK_DATE = pd.date_range(context.config.base.start_date, context.config.base.end_date, freq='W-THU')
    context.p_TOTAL_VALUE_BUFFER = 0.99  # 留1%的钱给手续费倒腾
    # set tendency industry 01_params
    context.p_t_ind_AIM0 = '399481.XSHE'
    context.p_t_ind_AIM_LIST = context.p_index_details.loc[
        context.p_index_details['strategy'] == 'IndustrialTendency', 'index_code'].apply(utility.convert_code_2_rqcode)
    context.p_t_ind_POSITION_RATIO = float(context.p_index_strategy.loc[
                                               context.p_index_strategy[
                                                   'strategy'] == 'IndustrialTendency', 'position_level'].iloc[0])
    context.p_t_ind_PREV = 20  # 这三个参数：判断有NUM_OF_BIG_THAN个指数，PREV天的涨幅，大于UP_THRESHOLD，则买入，否则清仓
    context.p_t_ind_UP_THRESHOLD = 1  # 这三个参数：判断有NUM_OF_BIG_THAN个指数，PREV天的涨幅，大于UP_THRESHOLD，则买入，否则清仓
    context.p_t_ind_NUM_OF_BIG_THAN = 6  # 这三个参数：判断有NUM_OF_BIG_THAN个指数，PREV天的涨幅，大于UP_THRESHOLD，则买入，否则清仓
    context.p_t_ind_INDEX_NUMBER = 2  # 每次持仓的指数数量


def handle_bar(context, bar_dict):
    # 首次建仓
    if not context.fired:
        logger.info('首次建仓...')
        t_ind_amount = context.config.base.accounts['STOCK'] * context.p_TOTAL_VALUE_BUFFER
        order_target_value(context.p_t_ind_AIM0, t_ind_amount)
        context.fired = True

    if pd.to_datetime(context.now.date()) not in context.p_CHECK_DATE:
        return
    logger.info('每周执行所有策略 - 行业轮动...')
    __trans_tendeccy_ind(context)


# 行业轮动策略
def __trans_tendeccy_ind(context):
    series_dongliang = __calc_index_dongliang(context.p_t_ind_AIM_LIST, context)
    current_holding = __get_current_holding(series_dongliang.index)
    list_to_buy_value = []  # 当卖出时，临时记录金额，买入时候取出金额

    if len(series_dongliang.loc[series_dongliang > context.p_t_ind_UP_THRESHOLD]) >= context.p_t_ind_NUM_OF_BIG_THAN:  # 指数有XX是正的，才买基金
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
