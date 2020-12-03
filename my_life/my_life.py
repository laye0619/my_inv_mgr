# daily life and investment

import logging

import pandas as pd


# calculate yearly return (compound interest)
def cal_yearly_return(profit, duration):
    return profit ** (1 / duration) - 1


# calculate monthly payment
def monthly_payment(total_debt, year_rate, year_duration):
    # 贷款额为a，月利率为i，年利率为I，还款月数为n
    if total_debt == 0:
        return 0
    i = year_rate / 12
    n = 12 * year_duration
    return total_debt * i * pow((1 + i), n) / (pow((1 + i), n) - 1)


class MyLife:
    def __init__(self, init_money, start_year, init_long_term_fixed_cost):
        self.init_money = init_money
        self.current_money = init_money
        self.start_year = start_year
        self.current_year = start_year

        # investment registration
        self.df_investment_reg = pd.DataFrame(columns=["inv_amount",
                                                       "inv_duration",
                                                       "annual_cash_income",
                                                       "due_year",
                                                       "due_value"])
        # cash flow registration
        self.df_cash_flow_reg = pd.DataFrame(columns=["cash value",
                                                      "validate until"])
        # houses registration
        self.df_house_reg = pd.DataFrame(columns=["buying_year",
                                                  "buying_price",
                                                  "loan_ratio",
                                                  "loan_interest",
                                                  "loan_duration",
                                                  "house_increment_ratio",
                                                  "house_m_tax_insurance",
                                                  "is_for_rental",
                                                  "m_rental_income",
                                                  "m_house_loan"])

        # add fixed cost
        for cost_item in init_long_term_fixed_cost:
            self.df_cash_flow_reg.loc[cost_item] = [init_long_term_fixed_cost[cost_item] * -1, 9999]

            # handle first year cash flow
        df_this_year_cash_flow = self.df_cash_flow_reg[self.df_cash_flow_reg['validate until'] >= self.current_year]
        self.current_money += df_this_year_cash_flow['cash value'].sum()

    # next year
    def next_year(self):
        self.current_year += 1

        # handle this year cash flow
        df_this_year_cash_flow = self.df_cash_flow_reg[self.df_cash_flow_reg['validate until'] >= self.current_year]
        this_year_cash_flow = df_this_year_cash_flow['cash value'].sum()
        #         print("total cost: " + str(this_year_cash_flow))
        if self.current_money + this_year_cash_flow < 0:
            logging.error("you don't have enough money to live... you gonna die...")
        self.current_money += this_year_cash_flow

        # get due this year investments
        yearly_inv_due_income = self.__handle_due_this_year()
        self.current_money += yearly_inv_due_income

    # fixed return investment
    def inv_fixed_return(self, inv_id, duration, amount, interest, yearly_payment):
        if self.current_money < amount:
            logging.warning("you don't have such much money! Fail to invest!!")
            return

        self.current_money -= amount
        self.df_investment_reg.loc[inv_id] = [amount, duration, 0, self.current_year + duration, 0]
        if yearly_payment is True:
            self.df_investment_reg.loc[inv_id, "annual_cash_income"] = amount * interest
            # reg cash flow
            self.df_cash_flow_reg.loc[inv_id] = [self.df_investment_reg.loc[inv_id, "annual_cash_income"],
                                                 self.current_year + duration]
            self.df_investment_reg.loc[inv_id, "due_value"] = amount
        else:
            self.df_investment_reg.loc[inv_id, "due_value"] = amount * (1 + interest) ** duration

    # once spend, such as travel, buying a car...
    def once_spend(self, once_spend_amount):
        if self.current_money < once_spend_amount:
            logging.warning("you don't have such much money! Fail to spend!!")
            return
        self.current_money -= once_spend_amount

    # invest a house; dict_inv_param: ref as house reg table
    def inv_house(self, dict_inv_param):
        house_price = dict_inv_param.get('buying_price')
        down_payment = house_price * (1 - dict_inv_param.get('loan_ratio'))
        if self.current_money < down_payment:
            logging.warning("you don't have such much money! Fail to invest!!")
            return
            # pay down payment
        self.current_money -= down_payment

        # register house
        self.df_house_reg.loc[dict_inv_param.get('id')] = {"buying_year": dict_inv_param.get('buying_year'),
                                                           "buying_price": dict_inv_param.get('buying_price'),
                                                           "loan_ratio": dict_inv_param.get('loan_ratio'),
                                                           "loan_interest": dict_inv_param.get('loan_interest'),
                                                           "loan_duration": dict_inv_param.get('loan_duration'),
                                                           "house_increment_ratio": dict_inv_param.get(
                                                               'house_increment_ratio'),
                                                           "house_m_tax_insurance": dict_inv_param.get(
                                                               'house_m_tax_insurance'),
                                                           "is_for_rental": dict_inv_param.get('is_for_rental'),
                                                           "m_rental_income": dict_inv_param.get('m_rental_income'),
                                                           "m_house_loan": 0
                                                           }

        # calc and fill monthly balance...
        self.df_house_reg.loc[dict_inv_param.get('id'), "m_house_loan"] = self.__calc_m_loan_payment(
            dict_inv_param.get('id'))

        # reg cash flow for new house
        rental_balance = dict_inv_param.get('m_rental_income') * 12
        loan_balance = self.df_house_reg.loc[dict_inv_param.get('id'), "m_house_loan"] * -12
        tax_insurance = dict_inv_param.get('house_m_tax_insurance') * -12
        self.df_cash_flow_reg.loc[dict_inv_param.get('id') + "-rental"] = [rental_balance, 9999]
        self.df_cash_flow_reg.loc[dict_inv_param.get('id') + "-loan"] = [loan_balance,
                                                                         self.current_year + dict_inv_param.get(
                                                                             'loan_duration')]
        self.df_cash_flow_reg.loc[dict_inv_param.get('id') + "-tax&insurance"] = [tax_insurance, 9999]
        return

    # sell a house; param: house_id
    def sell_house(self, house_id):
        # calculate current house value
        buying_price = self.df_house_reg.loc[house_id, "buying_price"]
        increment_ratio = self.df_house_reg.loc[house_id, "house_increment_ratio"]
        holding_duration = self.current_year - self.df_house_reg.loc[house_id, "buying_year"]

        current_value = buying_price * (1 + increment_ratio) ** holding_duration

        # calculate due loan and interest
        due_loan_duration = self.df_house_reg.loc[house_id, "loan_duration"] - holding_duration
        selling_price = current_value - self.df_house_reg.loc[house_id, "m_house_loan"] * 12 * due_loan_duration

        # handle current money
        self.current_money += selling_price

        # handle house reg and cash flow reg
        result_df = self.df_cash_flow_reg[self.df_cash_flow_reg.index.str.startswith(house_id)]
        self.df_cash_flow_reg = self.df_cash_flow_reg.drop(result_df.index)
        self.df_house_reg = self.df_house_reg.drop(index=house_id)
        return

    # buy a car
    def buy_car(self, car_id, car_price):
        if self.current_money < car_price:
            logging.warning("you don't have such much money! Fail to buy a car!!")
        self.current_money -= car_price

        # reg yearly cash flow table
        self.df_cash_flow_reg.loc[car_id] = [500 * 5 * 12 * -1 / 10000, 9999]

    # add new yearly fixed cost, such as after buying a car, yearly car cost...
    def add_yearly_fixed_cost(self, cost_item, cost_value, validate_until):
        self.df_cash_flow_reg.loc[cost_item] = [cost_value, validate_until]

    # Private: calculate due this year investment; del the correspond inv items and return the total value
    def __handle_due_this_year(self):
        due_this_year_inv = self.df_investment_reg[self.df_investment_reg['due_year'] == self.current_year]
        due_this_year_value = due_this_year_inv['due_value'].sum()
        self.df_investment_reg = self.df_investment_reg.drop(due_this_year_inv.index)
        due_this_year_inv = due_this_year_inv.drop(
            due_this_year_inv[due_this_year_inv['annual_cash_income'] == 0].index)
        self.df_cash_flow_reg = self.df_cash_flow_reg.drop(due_this_year_inv.index)
        return due_this_year_value

    # Private: calculate given house monthly loan
    def __calc_m_loan_payment(self, house_reg_id):
        total_debt = self.df_house_reg.loc[house_reg_id, 'buying_price'] * self.df_house_reg.loc[
            house_reg_id, 'loan_ratio']
        year_rate = self.df_house_reg.loc[house_reg_id, 'loan_interest']
        year_duration = self.df_house_reg.loc[house_reg_id, 'loan_duration']
        m_payment = monthly_payment(total_debt, year_rate, year_duration)

        return m_payment
