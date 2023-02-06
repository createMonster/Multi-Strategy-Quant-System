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

"""
The reason why we do this in a separate library is due to design principle, such as separation of concerns.
Other modules are not concerned with how the logic for EMA/SMA is implemented, it is just interested in getting the SMA.
for instance, we can change the implementation of the sma_series function to

return series.rolling(n).mean()

this means that if we were to change the implementation inside the sma_series function, no other component of the trading system needs to be `concerned` with this change,
as long as the specification is met.

suppose we did talib.SMA everywhere instead of using the sma_series function, then when we change the implementation, we would need to edit the code everywhere the function
is used, and this means your code is not scalable!
"""