import requests
import datetime
import time
import pandas as pd
import yfinance as yf #python3 -m pip install yFinance
from bs4 import BeautifulSoup #python3 -m pip insall bs4

BINANCE_BASE_URL = "https://fapi.binance.com"


def get_symbols():
    url = "/fapi/v1/exchangeInfo"
    url = BINANCE_BASE_URL + url
    symbols = requests.get(url).json()["symbols"]
    symbols = [x["symbol"] for x in symbols]
    
    # Remove some BUSD pairs
    remove_list = []
    for symbol in symbols:
        if "BUSD" in symbol and symbol[:-4] + "USDT" in symbols:
            remove_list.append(symbol)
        if "_" in symbol:
            remove_list.append(symbol)
    symbols = [x for x in symbols if x not in remove_list]

    return symbols

def get_crypto_futures_df(interval='8h', limit="1000"):
    """Get all tradable crypto data from binance"""
    url = "/fapi/v1/klines"
    url = BINANCE_BASE_URL + url

    columns = ["open_time", "open","high","low","close","volume","close_time","quote_volume","count","taker_buy_volume","taker_buy_quote_volume","ignore"]
    symbols = get_symbols()
    ohlcvs = {}
    for symbol in symbols:
        data = {
            "symbol": symbol,
            "interval": interval,
            "limit": str(limit)
        }
        response = requests.get(url, params=data).json()
        df = pd.DataFrame(response, columns=columns)
        df = df.drop(["close_time", "ignore", "volume"], axis=1)
        print (df)
        break

get_crypto_futures_df()