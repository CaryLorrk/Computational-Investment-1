#!/usr/bin/env python
# -*- coding: utf-8 -*-

import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkstudy.EventProfiler as ep

import csv
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def main():
    startdate = dt.datetime(2008, 1, 1)
    enddate = dt.datetime(2009, 12, 31)
    lookback = 20

    ldt_timestamps = du.getNYSEdays(startdate, enddate, dt.timedelta(hours=16))
    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list('sp5002012')
    ls_symbols.append('SPY')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    d_data = dict(zip(ls_keys, dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)))

    df_data = d_data['close']


    r = df_data.rolling(window=lookback)
    rolling_std = r.std()
    df_rolling_mean = r.mean()
    bollinger = (df_data - df_rolling_mean)/rolling_std

    bollinger = bollinger.fillna(method='ffill')
    bollinger = bollinger.fillna(method='bfill')
    bollinger = bollinger.fillna(1.0)
    df_events = pd.DataFrame(np.NaN, bollinger.index, bollinger.columns)
    df_events[(bollinger <= -2.0) & (bollinger.shift(1) >= -2.0) & (bollinger.where(bollinger['SPY'] >= 1.0).notnull())] = 1

    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename='report.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')

    orders = list()
    for i in range(len(df_events.index)):
        for symbol in df_events:
            if df_events.ix[i, symbol] == 1:
                startdate = df_events.index[i].date()
                enddate = df_events.index[i+5].date() if i+5 < len(
                    df_events.index) else df_events.index[-1].date()
                orders.append([startdate.year, startdate.month,
                               startdate.day, symbol, 'buy', 100])
                orders.append([enddate.year, enddate.month,
                               enddate.day, symbol, 'sell', 100])

    with open('orders.csv', 'wb') as order_file:
        csv.writer(order_file).writerows(orders)


if __name__ == "__main__":
    main()
