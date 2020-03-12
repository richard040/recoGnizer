import pandas as pd
import math
import os.path
import time
from bitmex import bitmex
from binance.client import Client
from datetime import timedelta, datetime
from dateutil import parser
from tqdm import tqdm

# API
bitmex_api_key = 'Kex0Rj458lqwRsVo3uOpu9XF'
bitmex_api_secret = '1bBiR3A0Msyw-TcmN6Wqy5R-XJnMaMYIPAY_FR9msn7XacEb'
binance_api_key = '9GtSsxCPRWR2sBGJpxLdeUMeaTZkgP99WH5XRHkkgCFVFcU4UFWzDqfViA8VUW4G'
binance_api_secret = 'PfkWEhwWuKh7YCBCL2PtAJKVnAK6NqKgrOYtnsE9yqiAMTRtkiVHPjA2kPdKx19U'

# CONSTANTS
bin_sizes = {"1m": 1, "5m": 5, "1h": 60, "4h": 240, "1d": 1440}
batch_size = 750
bitmex_client = bitmex(test=False, api_key=bitmex_api_key, api_secret=bitmex_api_secret)
binance_client = Client(api_key=binance_api_key, api_secret=binance_api_secret)


def minutes_of_new_data(symbol, kline_size, data, source):
    if not data.empty:
        old = parser.parse(data["timestamp"].iloc[-1])
    if source == "binance":
        old = datetime.strptime('1 Jan 2020', '%d %b %Y')
    elif source == "bitmex":
        old = bitmex_client.Trade.Trade_getBucketed(symbol=symbol, binSize=kline_size, count=1,
                                                    reverse=False).result()[0][0]['timestamp']
    if source == "binance":
        new = pd.to_datetime(binance_client.get_klines(symbol=symbol, interval=kline_size)[-1][0],
                             unit='ms')
    elif source == "bitmex":
        new = bitmex_client.Trade.Trade_getBucketed(symbol=symbol, binSize=kline_size, count=1,
                                                    reverse=True).result()[0][0]['timestamp']
    return old, new


def get_all_binance(symbol, kline_size, save=False):
    is_binance = "is Binance"
    filename = '%s-%s-data.csv' % (symbol, kline_size)
    if os.path.isfile(filename):
        data_df = pd.read_csv(filename)
    else:
        data_df = pd.DataFrame
    oldest_point, newest_point = minutes_of_new_data(symbol, kline_size, data_df, source="binance")
    delta_min = (newest_point - oldest_point).total_seconds() / 60
    available_data = math.ceil(delta_min / bin_sizes[kline_size])
    if oldest_point == datetime.strptime('1 Jan 2017', '%d %b %Y'):
        print("Source: Binance")
        print('Downloading all available %s data for %s...' % (kline_size, symbol))
    else:
        print("Source: Binance")
        print('Downloading %d minutes of new data available for %s, i.e. %d instances of %s data...'
              % (delta_min, symbol, available_data, kline_size))
    klines = binance_client.get_historical_klines(symbol, kline_size, oldest_point.strftime("%d %b %Y %H:%M:%S"),
                                                  newest_point.strftime("%d %b %Y %H:%M:%S"))
    data = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                         'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    if not data_df.empty:
        temp_df = pd.DataFrame(data)
        data_df = pd.DataFrame()
        data_df = data_df.append(temp_df)
    else:
        data_df = data
    data_df.set_index('timestamp', inplace=True)
    if save:
        data_df.to_csv(filename)
    print('All caught up..!')
    return data_df, is_binance


def get_all_bitmex(symbol, kline_size, save=False):
    is_bitmex = "is Bitmex"
    filename = '%s-%s-data.csv' % (symbol, kline_size)
    if os.path.isfile(filename):
        data_df = pd.read_csv(filename)
    else:
        data_df = pd.DataFrame
        oldest_point, newest_point = minutes_of_new_data(symbol, kline_size, data_df, source="bitmex")
        delta_min = (newest_point - oldest_point).total_seconds() / 60
        available_data = math.ceil(delta_min / bin_sizes[kline_size])
        rounds = math.ceil(available_data / batch_size)
        if rounds > 0:
            print("Source: Bitmex")
            print('Downloading %d minutes of new data available for %s, i.e %d instances of %s data in %d rounds...'
                  % (delta_min, symbol, available_data, kline_size, rounds))
            for round_num in tqdm(range(rounds)):
                time.sleep(1)
                new_time = (oldest_point + timedelta(minutes=round_num * batch_size * bin_sizes[kline_size]))
                data = bitmex_client.Trade.Trade_getBucketed(symbol=symbol, binSize=kline_size, count=batch_size,
                                                             startTime=new_time).result()[0]
                temp_df = pd.DataFrame(data)
                data_df = pd.DataFrame()
                data_df = data_df.append(temp_df)
        data_df.set_index('timestamp', inplace=True)
        if save and rounds > 0:
            data_df.to_csv(filename)
        print('All caught up..!')
        return data_df, is_bitmex


def get_all_csv(file_route):
    is_csv = "is CSV"
    my_date_parser = lambda x: pd.datetime.strptime(x, '%d.%m.%Y %H:%M:%S.%f')
    print("Source:", file_route)
    data_df = pd.read_csv(file_route,
                          index_col='Gmt time',
                          parse_dates=['Gmt time'],
                          date_parser=my_date_parser)
    return data_df, is_csv

