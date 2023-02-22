import json
import datetime
import pandas as pd

from dateutil.relativedelta import relativedelta
import quantlib.crypto_data_utils as crypto_du

import warnings
warnings.filterwarnings("ignore")

def prepare_data():
    """
    Get Data, update database

    Return: the extended historical data, all instruments
    """

    db_file = "crypto_ohlv_4h.xlsx"
    db_file_path = f"./Data/{db_file}"
    database_df = pd.read_excel(db_file_path).set_index("open_time")

    new_df, instruments = crypto_du.get_crypto_futures_df(interval="4h", limit=200)
    merge_df = pd.concat([database_df, new_df]).drop_duplicates(keep="first").sort_index()
    merge_df.to_excel(db_file_path)
    # Historical_data would include everything till now, also the current not finished kline
    historical_data = crypto_du.extend_dataframe(traded=instruments, df=merge_df, interval="4h")
    historical_data.to_excel("crypto_historical_4h.xlsx")
    
    return historical_data, instruments

def generate_signal(historical_data, instruments):
    """
    Generate signals
    """
    df = historical_data.copy()
    LOOK_BACK = 40
    LOOK_AHEAD = 20
    K = 20
    IGNORES = 1 # We do not want to count the closest momentum for possible reversion

    ret_cols = []
    SHIFT_UNITS = LOOK_BACK + IGNORES
    for inst in instruments:
        if df.iloc[-SHIFT_UNITS][f"{inst} active"] == False:
            print ("Not active symbols: ", inst)
            continue
        ret_col_name = "{} {} ret".format(inst, LOOK_BACK)
        ret_cols.append(ret_col_name)
        df[ret_col_name] = df["{} close".format(inst)].shift(IGNORES) / df["{} close".format(inst)].shift(SHIFT_UNITS) - 1

    last = df[ret_cols].tail(1).reset_index(drop=True)
    for col in last.columns:
        if last.loc[0, col] == 0: ret_cols.remove(col)
    rank = pd.qcut(last.loc[0, ret_cols], K, labels=False)
    
    # Based on rank generate symbols to be longed and symbols to be shorted
    long_list, short_list = [], []
    for col in ret_cols:
        symbol = col.split(" ")[0]
        if rank[col] == 0: short_list.append(symbol)
        elif rank[col] == K-1: long_list.append(symbol)

    print ("Long list: ", long_list)
    print ("Short list: ", short_list)
    return long_list, short_list

def execute_orders(long_list, short_list, test=True):
    """
    Execute orders, if test, no orders will be made
    """
    pass


def main(use_disk=False, test=True):
    if not use_disk:
        historical_data, instruments = prepare_data()
    else:
        historical_data = pd.read_excel("./crypto_historical_4h.xlsx", engine="openpyxl", index_col='open_time')
        instruments = crypto_du.get_symbols_from_df(historical_data)

    long_list, short_list = generate_signal(historical_data, instruments)
    execute_orders(long_list, short_list, test)

if __name__ == "__main__":
    print ("Working!")
    main(use_disk=True, test=True)
    
