#!/usr/bin/env python
# -*- coding: utf-8 -*-

import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.qsdateutil as du

import copy
import csv
import datetime as dt
import pandas as pd
import sys


def main(argv):
    if len(argv) < 4:
        print "usage: marketsim.py cash input output"
        return

    init_cash = argv[1]
    order_file_path = argv[2]
    value_file_path = argv[3]

    with open(order_file_path, 'rb') as order_file:
        orders = [{'date': dt.datetime(
                       int(row[0]),
                       int(row[1]),
                       int(row[2]),
                       16),
                   'symbol': row[3],
                   'op': row[4],
                   'amount': int(row[5])} for row in csv.reader(order_file)]
    orders.sort(key=lambda x: x['date'])
    symbols = set([row['symbol'] for row in orders])

    startdate = orders[0]['date']
    enddate = orders[-1]['date']
    timestamps = du.getNYSEdays(startdate, enddate, dt.timedelta(hours=16))
    dataobj = da.DataAccess('Yahoo')
    df_close = dataobj.get_data(timestamps, symbols, 'close')
    df_equity = pd.DataFrame(0, index=df_close.index, columns=list(
        symbols)+['cash'], dtype="float64")

    df_equity['cash'][0] = float(init_cash)
    for order in orders:
        sign = 1
        if order['op'].lower() == 'sell':
            sign = -1
        df_equity.loc[order['date'],
                      'cash'] -= sign * df_close.loc[order['date'],
                                                     order['symbol']] * order['amount']
        df_equity.loc[order['date'], order['symbol']] += sign * order['amount']

    for idx in range(1, len(df_equity)):
        df_equity.iloc[idx] = df_equity.iloc[idx] + df_equity.iloc[idx-1]

    df_close['cash'] = 1
    df_equity['value'] = (df_close * df_equity).sum(axis=1)

    values = [[row[0].date().year, row[0].date().month, row[0].date().day, int(row[1])] for row in zip(df_equity.index, df_equity['value'].values)]
    with open(value_file_path, 'wb') as value_file:
        csv.writer(value_file).writerows(values)


if __name__ == "__main__":
    main(sys.argv)
