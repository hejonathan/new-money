from backtest import *

bt = Backtester()  # uses default settings, you can customize symbols, timeframe, and more through parameters

RSI = vbt.IndicatorFactory.from_talib('RSI')
SMA = vbt.IndicatorFactory.from_talib('SMA')


# input must have names: 'Open', 'Close', 'High', 'Low'
def pullback_place_entry(Open, Close, rsi_window, sma_window, entries, out, leave):
    close = Close
    start = Open

    rsi = RSI.run(close, rsi_window).real.to_numpy()
    sma = SMA.run(close, sma_window).real.to_numpy()

    entries = np.where((rsi < entries) & (sma < start), 1, 0)
    entries = np.roll(entries, 2)

    leave_array = np.roll(entries.astype(float), leave)
    leave_array[:leave] = np.inf

    sell = np.where((leave_array == 1) | (rsi > out), -1, 0)
    sell = np.roll(sell, 2)

    exits = sell == -1
    entries = entries == 1

    return entries, exits  # mandatory


param_dict = {
    'rsi_window': np.arange(10, 30, step=1, dtype=int),
    'sma_window': np.arange(50, 300, step=5, dtype=int),
    'entry': np.arange(10, 50, step=2, dtype=int),
    'out': 40,
    'leave': 10
}

print(bt.test(strategy=pullback_place_entry,
              input_names=['Open', 'Close'],
              param_dict=param_dict
              ))
