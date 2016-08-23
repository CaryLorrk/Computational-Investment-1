#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep


def find_events(ls_symbols, d_data):
    df_actual_close = d_data['actual_close']
    df_events = df_actual_close * np.NAN
    df_events[(df_actual_close < 5.0) & (df_actual_close.shift(1) >= 5.0)] = 1

    return df_events


def main(list_name):
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list(list_name)
    ls_symbols.append('SPY')

    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    df_events = find_events(ls_symbols, d_data)
    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename=list_name+'.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')


if __name__ == '__main__':
    main('sp5002008')
    main('sp5002012')
