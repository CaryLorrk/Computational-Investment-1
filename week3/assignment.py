#!/usr/bin/env python
# -*- coding: utf-8 -*-

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da

import copy
import datetime as dt
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

from decimal import Decimal

def generate_simulate_function(symbols):
    def simulate(startdate, enddate, symbols, allocations):
        simulate.data['fund_cumu_ret'] = 0
        for sym, alloc in zip(symbols, allocations):
            simulate.data['fund_cumu_ret'] += alloc*(simulate.data[sym] / simulate.data[sym][0])

        simulate.data['fund_daily_ret'] = simulate.data[
            'fund_cumu_ret'] / simulate.data['fund_cumu_ret'].shift(1) - 1

        simulate.data['fund_daily_ret'][0] = 0

        portfolio = dict()
        portfolio['vol'] = simulate.data['fund_daily_ret'].std(ddof=0)
        portfolio['daily_ret'] = simulate.data['fund_daily_ret'].mean()
        portfolio['sharpe'] = math.sqrt(252)*portfolio['daily_ret']/ portfolio['vol']
        portfolio['cum_ret'] = simulate.data['fund_cumu_ret'][-1]
        return portfolio

    timeofday = dt.timedelta(hours=16)
    timestamps = du.getNYSEdays(startdate, enddate, timeofday)
    dataobj = da.DataAccess('Yahoo')
    simulate.data = dataobj.get_data(timestamps, symbols, 'close')
    return simulate

if __name__ == "__main__":
    startdate = dt.datetime(2011, 1, 1)
    enddate = dt.datetime(2011, 12, 31)
    symbols = ['AAPL', 'GLD', 'GOOG', 'XOM']

    # startdate = dt.datetime(2010, 1, 1)
    # enddate = dt.datetime(2010, 12, 31)
    # symbols = ['AXP', 'HPQ', 'IBM', 'HNZ']

    simulate = generate_simulate_function(symbols)
    optimal_portfolio = {'sharpe': sys.float_info.min}
    stop = step = Decimal('-0.1')
    d_alloc = np.empty(len(symbols))

    def optimizer(remain, idx):
        if idx == 0:
            d_alloc[0] = remain
            alloc = [float(a) for a in d_alloc]
            portfolio = simulate(startdate, enddate, symbols, alloc)
            if portfolio['sharpe'] > optimal_portfolio['sharpe']:
                optimal_portfolio.update(portfolio)
                optimal_portfolio['alloc'] = alloc
            return

        for a in np.arange(remain, stop, step):
            d_alloc[idx] = a
            optimizer(remain-a, idx-1)

    optimizer(Decimal(1), len(symbols)-1)

    print 'Start Date:', startdate
    print 'End Date:', enddate
    print 'Symbols:', symbols
    print 'Optimal Allocations:', optimal_portfolio['alloc']
    print 'Sharpe Ratio:', optimal_portfolio['sharpe']
    print 'Volatility (stddev of daily returns):', optimal_portfolio['vol']
    print 'Average Daily Return:', optimal_portfolio['daily_ret']
    print 'Cumulative Return:', optimal_portfolio['cum_ret']
