# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from my_life import *

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # # 每年活动结束后，执行my_life.next_year()
    # # investment template
    # my_life.inv_fixed_return('信托1号', 5, 300, 0.08, True)
    # my_life.inv_fixed_return('信托2号', 5, 400, 0.1, False)

    # # buying house template
    # house_param = { 'id' : 'beijing 1st',
    #                 'buying_year' : my_life.current_year,
    #                 'buying_price' : 200,
    #                 'loan_ratio' : 0.5,
    #                 'loan_interest' : 0.1,
    #                 'loan_duration': 2,
    #                 'house_increment_ratio': 0.05,
    #                 'house_m_tax_insurance' : 0,
    #                 'is_for_rental' : False,
    #                 'm_rental_income' : 0}

    # my_life.inv_house(house_param)

    # # sell house template
    # my_life.sell_house('beijing 1st')

    # # once spend template
    # my_life.once_spend(2)

    # set init param
    init_long_term_fixed_cost = {'min life cost': 1.5 * 12,
                                 'china cost': 0.3 + 0.3 + 0.4 + 0.5,
                                 'insurance': 5
                                 }

    my_life = MyLife(1500, 2022, init_long_term_fixed_cost)

    # Year 2022
    print("Beginning of the year: " + str(my_life.current_year) + "; We have " + str(my_life.current_money) + "万 RMB")
    print("开始愉快的生活了...")
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

    invest_this_year = my_life.current_money - 80

    my_life.inv_fixed_return('信托1号', 1, invest_this_year, 0.08, True)

    print(str(my_life.current_year) + "结束啦！年底，我们有" + str(my_life.current_money) + "万 RMB")
    print("真是难忘的一年！")
    print()

    # Year 2023
    my_life.next_year()

    print("Beginning of the year: " + str(my_life.current_year) + "; We have " + str(my_life.current_money) + "万 RMB")
    print("开始愉快的生活了...")

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

    # 旅旅游
    my_life.once_spend(2)

    # 败家媳妇买衣服/败家孩子
    my_life.once_spend(3)

    invest_this_year = my_life.current_money - 80

    my_life.inv_fixed_return('信托1号', 1, invest_this_year, 0.08, True)

    print(str(my_life.current_year) + "结束啦！年底，我们有" + str(my_life.current_money) + "万 RMB")
    print("真是难忘的一年！")
    print()

    # Year 2024

    my_life.next_year()

    print("Beginning of the year: " + str(my_life.current_year) + "; We have " + str(my_life.current_money) + "万 RMB")
    print("开始愉快的生活了...")
    # 旅旅游
    my_life.once_spend(2)

    # 败家媳妇买衣服/败家孩子
    my_life.once_spend(3)

    invest_this_year = my_life.current_money - 80

    my_life.inv_fixed_return('信托1号', 1, invest_this_year, 0.08, True)

    print(str(my_life.current_year) + "结束啦！年底，我们有" + str(my_life.current_money) + "万 RMB")
    print("真是难忘的一年！")
    print()

    # Year 2025

    my_life.next_year()

    print("Beginning of the year: " + str(my_life.current_year) + "; We have " + str(my_life.current_money) + "万 RMB")
    print("开始愉快的生活了...")

    # 旅旅游
    my_life.once_spend(4)

    # 败家媳妇买衣服/败家孩子
    my_life.once_spend(3)

    invest_this_year = my_life.current_money - 80

    my_life.inv_fixed_return('信托1号', 1, invest_this_year, 0.08, True)

    print(str(my_life.current_year) + "结束啦！年底，我们有" + str(my_life.current_money) + "万 RMB")
    print("真是难忘的一年！")
    print()

    # Year 2026

    my_life.next_year()

    print("Beginning of the year: " + str(my_life.current_year) + "; We have " + str(my_life.current_money) + "万 RMB")
    print("开始愉快的生活了...")

    # 旅旅游
    my_life.once_spend(4)

    # 败家媳妇买衣服/败家孩子
    my_life.once_spend(3)

    invest_this_year = my_life.current_money - 80

    my_life.inv_fixed_return('信托1号', 1, invest_this_year, 0.08, True)

    print(str(my_life.current_year) + "结束啦！年底，我们有" + str(my_life.current_money) + "万 RMB")
    print("真是难忘的一年！")
    print()

    # Year 2027

    my_life.next_year()

    print("Beginning of the year: " + str(my_life.current_year) + "; We have " + str(my_life.current_money) + "万 RMB")
    print("开始愉快的生活了...")

    # 旅旅游
    my_life.once_spend(5)

    # 败家媳妇买衣服/败家孩子
    my_life.once_spend(5)

    invest_this_year = my_life.current_money - 80

    my_life.inv_fixed_return('信托1号', 1, invest_this_year, 0.08, True)

    print(str(my_life.current_year) + "结束啦！年底，我们有" + str(my_life.current_money) + "万 RMB")
    print("真是难忘的一年！")
    print()

    # Year 2028

    my_life.next_year()

    print("Beginning of the year: " + str(my_life.current_year) + "; We have " + str(my_life.current_money) + "万 RMB")
    print("开始愉快的生活了...")

    # 旅旅游
    my_life.once_spend(5)

    # 败家媳妇买衣服/败家孩子
    my_life.once_spend(5)

    invest_this_year = my_life.current_money - 80

    my_life.inv_fixed_return('信托1号', 1, invest_this_year, 0.08, True)

    print(str(my_life.current_year) + "结束啦！年底，我们有" + str(my_life.current_money) + "万 RMB")
    print("真是难忘的一年！")
    print()

    # Year 2029

    my_life.next_year()

    print("Beginning of the year: " + str(my_life.current_year) + "; We have " + str(my_life.current_money) + "万 RMB")
    print("开始愉快的生活了...")

    # 旅旅游
    my_life.once_spend(5)

    # 败家媳妇买衣服/败家孩子
    my_life.once_spend(5)

    invest_this_year = my_life.current_money - 80

    my_life.inv_fixed_return('信托1号', 1, invest_this_year, 0.08, True)

    print(str(my_life.current_year) + "结束啦！年底，我们有" + str(my_life.current_money) + "万 RMB")
    print("真是难忘的一年！")
    print()

    # Year 2030

    my_life.next_year()

    print("Beginning of the year: " + str(my_life.current_year) + "; We have " + str(my_life.current_money) + "万 RMB")
    print("开始愉快的生活了...")

    # 旅旅游
    my_life.once_spend(5)

    # 败家媳妇买衣服/败家孩子
    my_life.once_spend(5)

    invest_this_year = my_life.current_money - 80

    my_life.inv_fixed_return('信托1号', 1, invest_this_year, 0.08, True)

    print(str(my_life.current_year) + "结束啦！年底，我们有" + str(my_life.current_money) + "万 RMB")
    print("真是难忘的一年！")
    print()

    # Year 2031

    my_life.next_year()

    print("Beginning of the year: " + str(my_life.current_year) + "; We have " + str(my_life.current_money) + "万 RMB")
    print("开始愉快的生活了...")

    # 旅旅游
    my_life.once_spend(5)

    # 败家媳妇买衣服/败家孩子
    my_life.once_spend(5)

    invest_this_year = my_life.current_money - 80

    my_life.inv_fixed_return('信托1号', 1, invest_this_year, 0.08, True)

    print(str(my_life.current_year) + "结束啦！年底，我们有" + str(my_life.current_money) + "万 RMB")
    print("真是难忘的一年！")
    print()

    # Year 2032

    my_life.next_year()

    print("Beginning of the year: " + str(my_life.current_year) + "; We have " + str(my_life.current_money) + "万 RMB")
    print("开始愉快的生活了...")

    # 旅旅游
    my_life.once_spend(5)

    # 败家媳妇买衣服/败家孩子
    my_life.once_spend(5)

    my_life.sell_house('love house')
    my_life.sell_house('rental house 1')

    print(str(my_life.current_year) + "结束啦！年底，我们有" + str(my_life.current_money) + "万 RMB")
    print("真是难忘的一年！")
    print()

    # Year 2033

    my_life.next_year()

    print("Beginning of the year: " + str(my_life.current_year) + "; We have " + str(my_life.current_money) + "万 RMB")

    # # Year XXXX

    # my_life.next_year()

    # print("Beginning of the year: " + str(my_life.current_year) + "; We have " + str(my_life.current_money) + "万 RMB")
    # print("开始愉快的生活了...")

    # print(str(my_life.current_year) + "结束啦！年底，我们有" + str(my_life.current_money) + "万 RMB")
    # print("真是难忘的一年！")
    # print()

    profit = (my_life.current_money - my_life.init_money) / my_life.init_money + 1
    print(cal_yearly_return(profit, 10))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
