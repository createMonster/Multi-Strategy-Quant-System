#Install Python > 3,6
#Install VS Code

#Install Pandas python3 -m pip install pandas
#Install Pandas python3 -m pip install yfinance


#First, let us obtain stickers in the SP500. (data part)

import requests
import datetime
import pandas as pd
import yfinance as yf #python3 -m pip install yFinance
from bs4 import BeautifulSoup #python3 -m pip insall bs4

def get_sp500_instruments():
    res = requests.get("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    soup = BeautifulSoup(res.content,'lxml')
    table = soup.find_all('table')[0] 
    df = pd.read_html(str(table))
    return list(df[0]["Symbol"])


def get_sp500_df():
    symbols = get_sp500_instruments()
    #to save time, let us perform ohlcv retrieval for 30 stocks
    symbols = symbols[:30]
    ohlcvs = {}
    for symbol in symbols:
        symbol_df = yf.Ticker(symbol).history(period="10y") #this gives us the OHLCV Dividends + Stock Splits
        #we are interested in the OHLCV mainly, let's rename them 
        ohlcvs[symbol] = symbol_df[["Open", "High", "Low", "Close", "Volume"]].rename(
            columns={
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume"
            }
        )
        print(symbol)
        print(ohlcvs[symbol]) #we can now get the data that we want inside a nicely formatted df
    
    #now, we want to put that all into a single dataframe.
    #since the columns need to be unique to identify the instrument, we want to add an identifier.
    #let's steal the GOOGL index as our dataframe index
    df = pd.DataFrame(index=ohlcvs["GOOGL"].index)
    df.index.name = "date"
    instruments = list(ohlcvs.keys())

    for inst in instruments:
        inst_df = ohlcvs[inst]
        columns = list(map(lambda x: "{} {}".format(inst, x), inst_df.columns)) #this tranforms open, high... to AAPL open , AAPL high and so on
        df[columns] = inst_df

    return df, instruments

#take an ohlcv df and add some other statistics
def extend_dataframe(traded, df, fx_codes):
    df.index = pd.Series(df.index).apply(lambda x: format_date(x)) 
    open_cols = list(map(lambda x: str(x) + " open", traded))
    high_cols = list(map(lambda x: str(x) + " high", traded))
    low_cols = list(map(lambda x: str(x) + " low", traded))
    close_cols = list(map(lambda x: str(x) + " close", traded))
    volume_cols = list(map(lambda x: str(x) + " volume", traded))
    historical_data = df.copy()
    historical_data = historical_data[open_cols + high_cols + low_cols + close_cols + volume_cols] #get a df with ohlcv for all traded instruments
    historical_data.fillna(method="ffill", inplace=True) #fill missing data by first forward filling data, such that [] [] [] a b c [] [] [] becomes [] [] [] a b c c c c
    historical_data.fillna(method="bfill", inplace=True) #fill missing data by backward filling data, such that [] [] [] a b c c c c becomes a a a a b c c c c
    for inst in traded:
        historical_data["{} % ret".format(inst)] = historical_data["{} close".format(inst)] / historical_data["{} close".format(inst)].shift(1) - 1 #close to close return statistic
        historical_data["{} % ret vol".format(inst)] = historical_data["{} % ret".format(inst)].rolling(25).std() #historical rolling standard deviation of returns as realised volatility proxy
        #test if stock is actively trading by using rough measure of non-zero price change from previous time step
        historical_data["{} active".format(inst)] = historical_data["{} close".format(inst)] != historical_data["{} close".format(inst)].shift(1)

        if is_fx(inst, fx_codes):
            inst_rev = "{}_{}".format(inst.split("_")[1], inst.split("_")[0])
            #fill in inverse fx quotes and statistics
            historical_data["{} close".format(inst_rev)] = 1 / historical_data["{} close".format(inst)]
            historical_data["{} % ret".format(inst_rev)] = historical_data["{} close".format(inst_rev)] / historical_data["{} close".format(inst_rev)].shift(1) - 1
            historical_data["{} % ret vol".format(inst_rev)] = historical_data["{} % ret".format(inst_rev)].rolling(25).std()
            historical_data["{} active".format(inst_rev)] = historical_data["{} close".format(inst_rev)] != historical_data["{} close".format(inst_rev)].shift(1)
    return historical_data

def is_fx(inst, fx_codes):
    return len(inst.split("_")) == 2 and inst.split("_")[0] in fx_codes and inst.split("_")[1] in fx_codes

def format_date(date):
    #convert 2012-02-06 00:00:00 >> datetime.date(2012, 2, 6)
    yymmdd = list(map(lambda x: int(x), str(date).split(" ")[0].split("-")))
    return datetime.date(yymmdd[0], yymmdd[1], yymmdd[2])


"""
Note there are multiple ways to fill missing data, depending on your requirements and purpose
Some options
1. Ffill -> bfill
2. Brownian motion/bridge
3. GARCH/GARCH Copula et cetera
4. Synthetic Data, such as GAN and Stochastic Volatility Neural Networks

The choices differ for your requirements . For instance, in backtesting you might favor (1), while in training neural models you might favor (4).

Note that the data cycle can be very complicated, with entire research teams dedicated to obtaining, processing and extracting signals from structured/unstructured data.
What we show today barely scratches the surface of the entire process, since we are dealing with well behaved data that is structured and already cleaned for us by Yahoo Finance API.
"""