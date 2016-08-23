#!/usr/bin/env python
# -*- coding: utf-8 -*-

import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.qsdateutil as du

import csv
import datetime as dt
import math
import matplotlib.pyplot as plt
import pandas as pd
import sys

from operator import itemgetter

def calculate(s):
    daily_ret = s / s.shift(1) - 1
    daily_ret.iloc[0] = 0

    result = dict()

    result['vol'] = daily_ret.std(ddof=0)
    result['daily_ret'] = daily_ret.mean()
    result['sharpe'] = math.sqrt(252) * result['daily_ret'] / result['vol']
    result['cum_ret'] = s[-1] / s[0]
    return result


def main(argv):
    if len(argv) < 3:
        print "usage: analyze.py input benchmark"
        return

    value_file_path = argv[1]
    benchmark_symbol = argv[2]
    with open(value_file_path, 'rb') as value_file:
        index = list()
        data = list()
        for row in csv.reader(value_file):
            index.append(dt.datetime(int(row[0]), int(row[1]), int(row[2]), 16))
            data.append(float(row[3]))
    s_value = pd.Series(data,index)
    portfolio = calculate(s_value)

    startdate = s_value.index[0]
    enddate = s_value.index[-1]
    timestamps = du.getNYSEdays(startdate, enddate, dt.timedelta(hours=16))
    s_close = da.DataAccess('Yahoo').get_data(timestamps, [benchmark_symbol], 'close')[benchmark_symbol]
    s_close = s_close / s_close[0] * s_value[0]
    benchmark = calculate(s_close)


    print "The final value of the portfolio using the sample file is --", index[-1].date(), data[-1]
    print ""
    print "Details of the Performance of the portfolio :"
    print ""
    print "Data Range :", s_value.index[0], "to", s_value.index[-1]
    print ""
    print "Sharpe Ratio of Fund :", portfolio['sharpe']
    print "Sharpe Ratio of", benchmark_symbol ,":", benchmark['sharpe']
    print ""
    print "Total Return of Fund :", portfolio['cum_ret']
    print "Total Return of", benchmark_symbol ,":", benchmark['cum_ret']
    print ""
    print "Standard Deviation of Fund :", portfolio['vol']
    print "Standard Deviation of", benchmark_symbol,":", benchmark['vol']
    print ""
    print "Average Daily Return of Fund :", portfolio['daily_ret']
    print "Average Daily Return of", benchmark_symbol, ":", benchmark['daily_ret']

    plt.clf()
    plt.plot(s_value.index,zip(s_value.values, s_close.values))
    plt.legend(['fund', benchmark_symbol])
    plt.show()



if __name__ == '__main__':
    main(sys.argv)
