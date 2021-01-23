import xalpha as xa
import pandas as pd

index_code = 'SH000001'

index_info = xa.indexinfo(index_code)
df_price = index_info.price[['date', 'totvalue']].reset_index(drop=True)

target_increment = 0.5
result_df = pd.DataFrame()

for index, row in df_price.iterrows():
    print('start date is: ', row['date'])
    start_point = row['totvalue']
    current_index = index
    while True:
        current_index += 1
        if current_index >= len(df_price):
            break
        print('    compare date is: ', df_price.loc[current_index, 'date'])
        target_point = df_price.loc[current_index, 'totvalue']
        increment = (target_point - start_point) / start_point
        if increment <= 0:
            break
        elif increment >= target_increment:
            result_df = result_df.append({
                'start_date': row['date'],
                'end_date': df_price.loc[current_index, 'date'],
                'increment': increment
            }, ignore_index=True)
            break

pass
