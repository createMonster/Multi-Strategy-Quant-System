"""
A calculator for indicators and other functionalities
"""

#we are going to use another dependency, called the technical analysis library (talib)
#Google: how to install talib (on Mac using brew) and (on Windows downloading the relevant file - do note that your python version needs to match with the downloaded whl file -  then run pip install)

import talib
import numpy as np
import pandas as pd

def adx_series(high, low, close, n):
    return talib.ADX(high, low, close, timeperiod=n)

def ema_series(series, n):
    return talib.EMA(series, timeperiod=n)

def sma_series(series, n):
    return talib.SMA(series, timeperiod=n)
