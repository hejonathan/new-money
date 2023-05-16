import vectorbt as vbt
import numpy as np
import numpy.ma as ma
import pandas as pd
import inspect
import datetime
import talib
from IPython.display import display, HTML


class Backtester:
    """Initializes the backtester (timeframe, symbols, etc.)"""

    # TODO: replace start end times to a list of start and end times
    def __init__(self, symbols: list,
                 start: str = '1990-3-05',
                 end: str = '2023-3-16',
                 timeframe: str = '1d',
                 init_cash: int = 10000):
        vbt.settings.data['alpaca']['key_id'] = 'PK2XNKDSJH4PVPCYDK8E'
        vbt.settings.data['alpaca']['secret_key'] = 'f5cD1kbR3p5RRfgvNgDiQ09qRpi4LCYmPZprl3KM'
        self.symbols = symbols
        self.start = start
        self.end = end
        self.timeframe = timeframe
        self.data = None
        self.init_cash = init_cash

        print('Backtester initializing...')
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        print('Parameters:')
        for i in args:
            print("\t%s = %s" % (i, values[i]))

        self.download_alpaca()
        print('Data Download Complete.')

    '''Downloads and returns the data from alpacas'''

    def download_alpaca(self, limit: int = 100000):
        self.data = vbt.AlpacaData.download(self.symbols,
                                            start=self.start,
                                            end=self.end,
                                            limit=limit,
                                            timeframe=self.timeframe).get()

    def test(self, strategy, input_names: list, param_names: list, param_values: list):
        print(f'Running backtest on {strategy.__name__}:')
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        print('Inputs & Parameters: ')
        for i in args:
            print("\t%s = %s" % (i, values[i]))

        indicator = vbt.IndicatorFactory(
            class_name=strategy.__name__,
            short_name=strategy.__name__,
            input_names=input_names,
            output_names=['entries', 'exits'],
            param_names=param_names
        ).from_apply_func(strategy)

        inputs = [self.data[e] for e in input_names]
        parameter_dictionary = dict(zip(param_names, param_values))

        entries, exits = indicator.run(*inputs, **parameter_dictionary)

        entries = entries == 1
        exits = exits == -1

        pf = vbt.Portfolio.from_signals(self.data['Open'], entries, exits, init_cash=self.init_cash, freq=self.timeframe)

        return pf.total_return().max()
