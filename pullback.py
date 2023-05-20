import vectorbt as vbt
import numpy as np
import numpy.ma as ma
import pandas as pd
import inspect
import datetime
import talib
from IPython.display import display, HTML

from backtest import Backtester


def pullback_place_entry(start, close, rsi_window=10, sma_window=200, entry=30, out=40, leave=10):
    RSI = vbt.IndicatorFactory.from_talib('RSI')
    SMA = vbt.IndicatorFactory.from_talib('SMA')

    rsi = RSI.run(close, rsi_window).real.to_numpy()
    sma = SMA.run(close, sma_window).real.to_numpy()

    entry = np.where((rsi < entry) & (sma < start), 1, 0)

    entry = np.roll(entry, 2)

    leave_array = np.roll(entry.astype(float), leave)
    leave_array[:leave] = np.inf

    stop_loss = np.where((leave_array == 1), -1, 0)
    take_profit = np.where(rsi > out, -1, 0)
    sell = np.where((leave_array == 1) | (rsi > out), -1, 0)
    sell = np.roll(sell, 2)

    return entry == 1, stop_loss == -1


bt = Backtester()  # uses default settings, you can customize symbols, timeframe, and more through parameters

param_dict = {
    'rsi_window': np.arange(10, 30, step=1, dtype=int),
    'sma_window': np.arange(50, 300, step=5, dtype=int),
    'entry': np.arange(10, 50, step=2, dtype=int),
    'out': 40,
    'leave': 10
}

bt.test(strategy=pullback_place_entry,
        input_names=['Open', 'Close'],
        param_dict=param_dict
        )
