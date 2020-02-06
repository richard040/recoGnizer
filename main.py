import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from harmonic_patterns import *

# Dataset import
my_date_parser = lambda x: pd.datetime.strptime(x, '%d.%m.%Y %H:%M:%S.%f')
data = pd.read_csv('Data/EURUSD_Candlestick_4_Hour_ASK_01.07.2019-06.02.2020.csv',
                   index_col='Gmt time',
                   parse_dates=['Gmt time'],
                   date_parser=my_date_parser)
data.columns = [['open', 'high', 'low', 'close', 'volume']]
data = data[['open', 'high', 'low', 'close', 'volume']]
data.drop_duplicates(keep='last', inplace=True)
price = data.iloc[:, 3]

# Find Gartley
tolerance = 0.2
order = 10

for i in range(100, len(price)):
    idx, current_idx, current_pattern, start_idx, end_idx = find_peak(price.values[:i], order)
    peaks = price.values[idx]

    if i == 100:  # to make sure the price values only get plotted once, but before the found pattern
        plt.title("Peaks and patterns")
        plt.plot(price.values, color='#3973ac')

    XA = current_pattern[1] - current_pattern[0]
    AB = current_pattern[2] - current_pattern[1]
    BC = current_pattern[3] - current_pattern[2]
    CD = current_pattern[4] - current_pattern[3]

    price_moves = [XA, AB, BC, CD]

    gartley_result = is_gartley(price_moves, tolerance)

    if gartley_result == 1 or gartley_result == -1:
        date_start = data.iloc[start_idx].name
        date_end = data.iloc[end_idx].name
        print("Start date: ", date_start)
        print("End date: ", date_end)

        plt.plot(np.arange(start_idx, i), price.values[start_idx:i])
        plt.plot(current_idx, current_pattern, color='red')

# Show peaks and patterns
plt.scatter(idx, peaks, color='red')
plt.show()

