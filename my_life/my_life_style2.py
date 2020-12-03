from my_life import *

# set init param
init_long_term_fixed_cost = {'min life cost': 1.5 * 12,
                             'china cost': 0.3 + 0.3 + 0.4 + 0.5,
                             'insurance': 5
                             }

my_life = MyLife(1500, 2022, init_long_term_fixed_cost)

# buy living house and car
print("beginning of year " + str(my_life.current_year) + "; we have " + str(my_life.current_money) + " wan RMB")
house_param = {'id': 'love house',
               'buying_year': my_life.current_year,
               'buying_price': 400,
               'loan_ratio': 0.65,
               'loan_interest': 0.03,
               'loan_duration': 20,
               'house_increment_ratio': 0.05,
               'house_m_tax_insurance': 0.29,
               'is_for_rental': False,
               'm_rental_income': 0}
my_life.inv_house(house_param)
my_life.buy_car('love car', 40)

# buy a investment house for rental
house_param_1 = {'id': 'rental house 1',
                 'buying_year': my_life.current_year,
                 'buying_price': 200,
                 'loan_ratio': 0.65,
                 'loan_interest': 0.03,
                 'loan_duration': 20,
                 'house_increment_ratio': 0.05,
                 'house_m_tax_insurance': 0.2,
                 'is_for_rental': True,
                 'm_rental_income': 1}
my_life.inv_house(house_param_1)

# calculate invest amount this year
fix_cost = my_life.df_cash_flow_reg['cash value'].sum()
inv_amount = my_life.current_money + fix_cost - 30
my_life.inv_fixed_return('TRUST 1st', 1, inv_amount, 0.08, True)

i = 1
while i < 10:
    my_life.next_year()
    print("beginning of year " + str(my_life.current_year) + "; we have " + str(my_life.current_money) + " wan RMB")

    # 旅旅游
    my_life.once_spend(5)

    # 败家媳妇买衣服/败家孩子
    my_life.once_spend(5)

    # calculate invest amount this year
    fix_cost = my_life.df_cash_flow_reg['cash value'].sum()
    inv_amount = my_life.current_money + fix_cost - 30
    my_life.inv_fixed_return('TRUST 1st', 1, inv_amount, 0.08, True)

    i += 1

# sell all the asset and calculate
my_life.next_year()
my_life.sell_house('love house')
my_life.sell_house('rental house 1')

profit = (my_life.current_money - my_life.init_money) / my_life.init_money + 1
duration = my_life.current_year - my_life.start_year
print(str(duration) + " years past, we have " + str(my_life.current_money) + " wan RMB")
print("final yearly profit ratio: " + str(cal_yearly_return(profit, duration)))
