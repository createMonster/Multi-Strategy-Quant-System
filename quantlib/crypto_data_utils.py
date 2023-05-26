import requests
import time
import pandas as pd

BINANCE_BASE_URL = "https://fapi.binance.com"


def get_symbols():
    url = "/fapi/v1/exchangeInfo"
    url = BINANCE_BASE_URL + url
    try:
        symbols = requests.get(url).json()["symbols"]
        symbols = [x["symbol"] for x in symbols]
    except:
        raise Exception("Could be the problem of region! Try another location")
    
    # Remove some BUSD pairs
    remove_list = []
    for symbol in symbols:
        if "BUSD" in symbol and symbol[:-4] + "USDT" in symbols:
            remove_list.append(symbol)
        if "_" in symbol or "USDC" in symbol:
            remove_list.append(symbol)
    symbols = [x for x in symbols if x not in remove_list]

    return symbols

def get_symbols_from_df(df):
    instruments = []
    for col in df.columns:
        inst = col.split(" ")[0]
        if "USD" in inst and inst not in instruments:
            instruments.append(inst)
    return instruments


def sleep_if_big_limit(limit):
    if limit >= 1000:
        time.sleep(0.35)

def get_crypto_futures_df(interval='4h', limit=1000, end_time=None):
    """Get all tradable crypto data from binance"""
    url = "/fapi/v1/klines"
    url = BINANCE_BASE_URL + url

    columns = ["open_time", "open","high","low","close","volume","close_time","quote_volume","count","taker_buy_volume","taker_buy_quote_volume","ignore"]
    symbols = get_symbols()
    ohlcvs = {}
    for symbol in symbols:
        sleep_if_big_limit(limit) # Prevent exceeding the API limit
        data = {
            "symbol": symbol,
            "interval": interval,
            "limit": str(limit)
        }
        if end_time:
            data["endTime"] = end_time
        response = requests.get(url, params=data).json()
        ohlcvs[symbol] = (pd.DataFrame(response, columns=columns, dtype=float)
                            .drop(["close_time", "ignore", "volume", "taker_buy_volume"], axis=1)
                            .set_index("open_time")
                         )
        print (ohlcvs[symbol])

    df = pd.DataFrame(index=ohlcvs["BTCUSDT"].index)
    instruments = list(ohlcvs.keys())

    for inst in instruments:
        inst_df = ohlcvs[inst]
        cols = list(map(lambda x: f"{inst} {x}", inst_df.columns))
        df[cols] = inst_df

    if not end_time:
        df.to_excel(f"crypto_ohlv_{interval}.xlsx")
    else:
        df.to_excel(f"crypto_ohlv_{interval}_{end_time}.xlsx")
    return df, instruments


def extend_dataframe(traded, df, interval='4h'):
    df.index = pd.to_datetime(df.index, unit='ms')
    target_cols = [col for col in df.columns if col.split(' ')[0] in traded]
    historical_data = df.copy()
    historical_data = historical_data[target_cols]
    historical_data.fillna(method="ffill", inplace=True)
    historical_data.fillna(method="bfill", inplace=True)

    for inst in traded:
        historical_data[f"{inst} avg trade size"] = historical_data[f"{inst} quote_volume"] / historical_data[f"{inst} count"]
        historical_data[f"{inst} taker %"] = historical_data[f"{inst} taker_buy_quote_volume"] / historical_data[f"{inst} quote_volume"]
        historical_data[f"{inst} % ret"] = historical_data[f"{inst} close"] / historical_data[f"{inst} close"].shift(1) - 1
        historical_data[f"{inst} % ret vol"] = historical_data[f"{inst} % ret"].rolling(25).std()
        # active if the close price are not the same between two days
        historical_data[f"{inst} active"] = historical_data[f"{inst} close"] != historical_data[f"{inst} close"].shift(1)

    #historical_data.to_excel(f"crypto_historical_{interval}.xlsx")
    return historical_data
        

if __name__ == "__main__":
    df, instruments = get_crypto_futures_df(interval='4h', limit=1400, end_time=1656691200000) # max limit is 1500
    #historical_data = extend_dataframe(instruments, df, interval='1h')