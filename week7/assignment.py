#!/usr/bin/env python
# -*- coding: utf-8 -*-

import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.qsdateutil as du

import datetime as dt
import matplotlib.pyplot as plt


def main():
    symbol = 'GOOG'
    startdate = dt.datetime(2010, 1, 1)
    enddate = dt.datetime(2010, 12, 31)
    lookback = 20

    ldt_timestamps = du.getNYSEdays(startdate, enddate, dt.timedelta(hours=16))
    dataobj = da.DataAccess('Yahoo')
    df_data = dataobj.get_data(ldt_timestamps, [symbol], 'close')

    r = df_data.rolling(window=lookback)
    rolling_std = r.std()
    df_data['rolling_mean'] = r.mean()[symbol]
    df_data['upper'] = df_data['rolling_mean'] + rolling_std[symbol]
    df_data['lower'] = df_data['rolling_mean'] - rolling_std[symbol]
    bollinger = (df_data[symbol] - df_data['rolling_mean'])/rolling_std[symbol]


    plt.subplot(211)
    plt.plot(df_data.index, df_data[symbol].values)
    plt.fill_between(df_data.index, df_data['upper'].values, df_data['lower'].values, facecolor='gray')
    for t in df_data.index:
        if bollinger[t] >= 1.0:
            plt.axvline(x=t, color='red')
        elif bollinger[t] <= -1.0:
            plt.axvline(x=t, color='green')

    plt.subplot(212)
    plt.plot(df_data.index, bollinger)
    plt.fill_between(df_data.index, 1, -1, facecolor='gray')
    for t in df_data.index:
        if bollinger[t] >= 1.0:
            plt.axvline(x=t, color='red')
        elif bollinger[t] <= -1.0:
            plt.axvline(x=t, color='green')
    plt.show()



if __name__ == "__main__":
    main()
