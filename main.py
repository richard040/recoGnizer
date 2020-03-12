import matplotlib.pyplot as plt
from get_data import *
from harmonic_patterns import *

data, data_from = get_all_binance("ETHBTC", "4h", save=False)
# data, data_from = get_all_csv('Data/EURUSD_Candlestick_4_Hour_ASK_01.07.2019-06.02.2020.csv')

#####################
# BITMEX TO BE TESTED
# data, data_from = get_all_bitmex("ETHUSD", "5m", save=False)
#####################

if data_from == "is Binance" or data_from == "is Bitmex":
    data = data[['open', 'high', 'low', 'close', 'volume']]
    price = data.iloc[:, 3].astype(float)
elif data_from == "is CSV":
    data.columns = [['open', 'high', 'low', 'close', 'volume']]
    data = data[['open', 'high', 'low', 'close', 'volume']]
    data.drop_duplicates(keep='last', inplace=True)
    price = data.iloc[:, 3]

plt.figure(1)
plt.title("Peaks and patterns")
plt.plot(price.values, color='#3973ac')

# Find Gartley
tolerance = 0.2
order = 10

for i in range(100, len(price)):
    idx, current_idx, current_pattern, start_idx, end_idx = find_peak(price.values[:i], order)
    peaks = price.values[idx]

    XA = current_pattern[1] - current_pattern[0]
    AB = current_pattern[2] - current_pattern[1]
    BC = current_pattern[3] - current_pattern[2]
    CD = current_pattern[4] - current_pattern[3]

    price_moves = [XA, AB, BC, CD]

    result = is_gartley(price_moves, tolerance)

    if result == 1 or result == -1:
        date_start = data.iloc[start_idx].name
        date_end = data.iloc[end_idx].name
        print("Start date: ", date_start)
        print("End date: ", date_end)

        plt.figure(1)
        plt.plot(current_idx, current_pattern, color='red')
        # plt.plot(np.arange(start_idx, i), price.values[start_idx:i])

# Show peaks and patterns
plt.figure(1)
plt.scatter(idx, peaks, color='green')
plt.show()

