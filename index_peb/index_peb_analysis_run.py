import index_peb_analysis
import pandas as pd
import datetime

# TODO to change code here after updating peb
report_root = './report/'
params_root = './params/'

index_analyze = index_analyze.IndexAnalyze(data_source='jqdata')

# # get pe and pb from data source and update/add to csv files
index_analyze.index_data_update_2_csv()

# run daily report and target selling point report
cal_method = 2
daily_report, target_selling_report = index_analyze.daily_pe_pb_report(cal_method)
with pd.ExcelWriter('%sdaily_pe_pb_report_%s_c%s.xlsx' %
                    (report_root, daily_report.index.name, cal_method)) as writer:
    daily_report.to_excel(writer, sheet_name='daily_report')
    target_selling_report.to_excel(writer, sheet_name='target_selling')

# # get df of single index's price/PE/PB
# index_analyze.build_single_index_price_pe_pb('000990')


# # plot PE and PB historical report
# index_analyze.plot_pe_report(['000991', '000990', '399812', '000905'], cal_method=1)
# index_analyze.plot_pe_report()

# index_analyze.plot_pb_report(['000905'])
# index_analyze.plot_pb_report()

# # plot PE and PB histogram
# index_analyze.plot_pe_hist('000300')
# index_analyze.plot_pb_hist('000300')

# index_analyze.plot_pe_bin('000991', interval=80)
# index_analyze.plot_pb_bin('000991', interval=80)

# # plot single index PE with all kinds of methods
# index_analyze.plot_single_index_different_pe_method('000990')
# index_analyze.plot_single_index_different_pb_method('000990')

# # index corr report
# df_index_corr = index_analyze.cal_index_corr()
# df_index_corr.to_excel('%sindex_corr.xlsx' % report_root)

# # plot single index's two data(pe vs pb / pe vs price / pb vs price)
# index_analyze.plot_single_index_price_pe_pb('000985', ['PB', 'PE'])
pass
