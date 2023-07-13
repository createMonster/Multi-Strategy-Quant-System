import time
import pandas as pd
from collections import defaultdict

from dateutil.relativedelta import relativedelta
import quantlib.crypto_data_utils as crypto_du
from brokerage.binance.TradeClient import TradeClient

import config.crypto_config as conf

import warnings
warnings.filterwarnings("ignore")

LONG_RANK = [(0, 3), (1, 3), (4, 0)]
lw = [0.25, 0.25, 0.5]
SHORT_RANK = [(0, 0), (0, 2), (1, 0)]
sw = [0.4, 0.2, 0.4]
rank_weight_dict = {}
for i, rank in enumerate(LONG_RANK):
    rank_weight_dict[rank] = lw[i]
for i, rank in enumerate(SHORT_RANK):
    rank_weight_dict[rank] = sw[i]
print (rank_weight_dict)

def prepare_data(limit=100):
    """
    Get Data, update database

    Return: the extended historical data, all instruments
    """

    db_file = "crypto_ohlv_4h.xlsx"
    db_file_path = f"./Data/{db_file}"
    database_df = pd.read_excel(db_file_path).set_index("open_time")

    new_df, instruments = crypto_du.get_crypto_futures_df(interval="4h", limit=limit)
    merge_df = pd.concat([database_df, new_df])
    merge_df = merge_df[~merge_df.index.duplicated(keep='last')].sort_index()
    merge_df.to_excel(db_file_path)
    # Historical_data would include everything till now, also the current not finished kline
    historical_data = crypto_du.extend_dataframe(traded=instruments, df=merge_df, interval="4h")
    historical_data.to_excel("crypto_historical_4h.xlsx")
    
    return historical_data, instruments

def get_symbol_rank(rank_df, symbol):
    rank_df = rank_df.to_frame().transpose()
    for col in rank_df.columns:
        if col[:6] == symbol[:6]:
            return int(rank_df[col])
        
def get_volitility(inst):
    return float(df.iloc[-1][f"{inst} % ret vol"])

def generate_rank_dict(rank1, rank2, instruments):
    rank_dict = defaultdict(list)
    for inst in instruments:
        inst_details = {
            "symbol": inst,
            "vol_weight": 1 / (get_volitility(inst) + 0.001)
        }
        r1, r2 = get_symbol_rank(rank1, inst), get_symbol_rank(rank2, inst)
        rank_dict[(r1, r2)].append(inst_details)

    # Set weights
    rank_dict_with_weights = defaultdict(list)
    for k, v in rank_dict.items():
        if k not in rank_weight_dict: continue
        if not v: continue
        try:
            total_vol_weight = sum([x["vol_weight"] for x in v])
            for details in v:
                details["weight"] = rank_weight_dict[k] * details["vol_weight"] / total_vol_weight
                rank_dict_with_weights[k].append(details)
        except Exception as e:
            print (e)
            for details in v:
                details["weight"] = rank_weight_dict[k] / len(v)
                rank_dict_with_weights[k].append(details)

    return rank_dict_with_weights
    
    
def generate_signal(historical_data, instruments):
    """
    Generate signals
    """
    global df
    df = historical_data.copy()
    LOOK_BACK = 62
    LOOK_AHEAD = 15
    K1, K2 = 5, 4
    IGNORES = 5 # We do not want to count the closest momentum for possible reversion

    active_insts = []
    ret_cols = []
    SHIFT_UNITS = LOOK_BACK + IGNORES
    for inst in instruments:
        if df.iloc[-SHIFT_UNITS][f"{inst} active"] == False:
            print ("Not active symbols: ", inst)
            continue
        active_insts.append(inst)
        ret_col_name = "{} {} ret".format(inst, LOOK_BACK)
        ret_cols.append(ret_col_name)
        df[ret_col_name] = df["{} close".format(inst)].shift(IGNORES) / df["{} close".format(inst)].shift(SHIFT_UNITS) - 1

    # Modify last row to get the second feature
    second_feature_cols = []
    last = df[ret_cols].tail(1).reset_index(drop=True)
    for inst in active_insts:
        col_name = f"{inst} {LOOK_BACK} max bar ret"
        second_feature_cols.append(col_name)
        last.loc[0, col_name] = max(df.iloc[-SHIFT_UNITS:-IGNORES][f"{inst} % ret"])

    rank1 = pd.qcut(last.loc[0, ret_cols], K1, labels=False)
    rank2 = pd.qcut(last.loc[0, second_feature_cols], K2, labels=False)
    
    # Based on rank generate symbols to be longed and symbols to be shorted
    rank_dict = generate_rank_dict(rank1, rank2, active_insts)

    long_list, short_list = [], []
    for long_rank in LONG_RANK:
        long_list += rank_dict[long_rank]
    for short_rank in SHORT_RANK:
        short_list += rank_dict[short_rank]

    #print ("Long list: ", long_list)
    #print ("Short list: ", short_list)
    return long_list, short_list

def execute_orders(long_list, short_list, test=True):
    """
    Execute orders, if test, no orders will be made
    """
    client = TradeClient()
    curr_positions = client.get_account_positions()
    if test:
        print (curr_positions)
        return

    long_symbols = [x["symbol"] for x in long_list]
    short_symbols = [x["symbol"] for x in short_list]

    # Close positions
    for symbol, details in curr_positions.items():
        position_amount = details['positionAmt']
        if symbol in long_symbols and position_amount > 0:
            continue
        if symbol in short_symbols and position_amount < 0:
            continue
        client.close_positon(symbol, details)

    # Open positons
    curr_positions = client.get_account_positions()
    
    for i, symbol in enumerate(long_symbols):
        if symbol not in curr_positions:
            params = conf.BUY_PARAMS.copy()
            params["collateral"] = params["collateral"] * long_list[i]["weight"]
            print (symbol, params)
            client.open_position(symbol, params)
            time.sleep(0.3)
    
    for i, symbol in enumerate(short_symbols):
        if symbol not in curr_positions:
            params = conf.SELL_PARAMS.copy()
            params["collateral"] = params["collateral"] * short_list[i]["weight"]
            print (symbol, params)
            client.open_position(symbol, params)
            time.sleep(0.3)

    print ("Orders have been placed!")


def main(use_disk=False, test=True):
    if not use_disk:
        historical_data, instruments = prepare_data(limit=100)
    else:
        historical_data = pd.read_excel("./crypto_historical_4h.xlsx", engine="openpyxl", index_col='open_time')
        instruments = crypto_du.get_symbols_from_df(historical_data)

    long_list, short_list = generate_signal(historical_data, instruments)
    print (long_list)
    execute_orders(long_list, short_list, test)

if __name__ == "__main__":
    print ("Working!")
    main(use_disk=False, test=True)
    #main(use_disk=False, test=False)
