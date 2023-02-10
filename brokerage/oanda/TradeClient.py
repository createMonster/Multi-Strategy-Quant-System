#interacts with the oandapyV20 api to make, update, delete and read orders
#the documentation and code samples give us all the info we need! https://readthedocs.org/projects/oanda-api-v20/downloads/pdf/latest/

import json
import pandas as pd
import datetime
import oandapyV20
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.positions as positions
import oandapyV20.endpoints.instruments as instruments

from collections import defaultdict

class TradeClient():

    def __init__(self, brokerage_config=None, auth_config=None, service_client=None):
        self.id = auth_config["oan_acc_id"]
        self.token = auth_config["oan_token"]
        self.env = auth_config["oan_env"]
        self.client = oandapyV20.API(access_token=self.token, environment=self.env)        

    """
    We are interested in getting
    1. Capital
    2. Positions
    3. Submit Orders
    4. Get OHLCV data etc
    """

    def get_account_details(self):
        try:
            return self.client.request(accounts.AccountDetails(self.id))["account"]
        except Exception as err:
            print(err)

    def get_account_summary(self):
        try:
            return self.client.request(accounts.AccountSummary(self.id))["account"]
        except Exception as err:
            print(err)
            #do your error handling

    def get_account_instruments(self):
        #Get the list of tradable instruments for the given Account. The list of tradeable instruments is dependent on the regulatory division that the Account is located in
        #we can get financing rates for instruments here , etc
        try:
            r = self.client.request(accounts.AccountInstruments(accountID=self.id))["instruments"]
            instruments = {}
            currencies, cfds, metals = [], [], []
            tags = defaultdict(list)
            for inst in r:
                #suppose we want to also store their tags
                inst_name = inst["name"]
                type = inst["type"]
                tag_name = inst["tags"][0]["name"]
                tags[tag_name].append(inst_name) 
                instruments[inst_name] = {
                    "type": type, #and other things you want to store, such as precision, marginRate etc
                    "tag": inst["tags"][0]["name"]
                }
                if type == "CFD":
                    cfds.append(inst_name)
                elif type == "CURRENCY":
                    currencies.append(inst_name)
                elif type == "METAL":
                    metals.append(inst_name)
                else:
                    print("unknown type", inst_name)
                    exit()

            return instruments, currencies, cfds, metals, tags
        except Exception as err:
            print(err)

    def get_account_capital(self):
        try:
            return float(self.get_account_summary()["NAV"])
        except Exception as err:
            pass

    #we can try to enter some positions or trades to see what the return result looks like
    #we see that the Oanda brokerage automatically performs netting of positions
    #we bought 30 EUR_USD units, sold 6, and we have 24 units of open positions
    #do note that this is not the same for every brokerage. In some cases, brokerages allow two open trades of opposing direction without netting
    #this would cause the txn fees to increase!
    def get_account_positions(self):
        positions_data = self.get_account_details()["positions"]
        positions = {}
        for entry in positions_data:
            instrument = entry["instrument"]
            long_pos = float(entry["long"]["units"])
            short_pos = float(entry["short"]["units"])
            net_pos = long_pos + short_pos
            if net_pos != 0:
                positions[instrument] = net_pos
        return positions

    def get_account_trades(self):
        try:
            trade_data = self.client.request(trades.OpenTrades(accountID=self.id))
            return trade_data
        except Exception as err:
            pass

    def format_date(self, series):
        #series in the form :: 2021-09-21T21:00:00.000000000Z
        ddmmyy = series.split("T")[0].split("-")
        return datetime.date(int(ddmmyy[0]), int(ddmmyy[1]), int(ddmmyy[2]))

    def get_ohlcv(self, instrument, count, granularity):
        try:
            params = {"count": count, "granularity": granularity}
            candles = instruments.InstrumentsCandles(instrument=instrument, params=params)
            self.client.request(candles)
            ohlcv_dict = candles.response["candles"]
            ohlcv = pd.DataFrame(ohlcv_dict)
            ohlcv = ohlcv[ohlcv["complete"]]
            ohlcv_df = ohlcv["mid"].dropna().apply(pd.Series)
            ohlcv_df["volume"] = ohlcv["volume"]
            ohlcv_df.index = ohlcv["time"]
            ohlcv_df = ohlcv_df.apply(pd.to_numeric)
            ohlcv_df.reset_index(inplace=True) #once again we want to format the date and columns in the same way as we did for the extend_dataframe function for sp500 dataset
            ohlcv_df.columns = ["date", "open", "high", "low", "close", "volume"]
            ohlcv_df["date"] = ohlcv_df["date"].apply(lambda x: self.format_date(x)) #this is the format that yahoo finance API gave us, and we just need to add identifiers!
            return ohlcv_df
        except Exception as err:
            print(err) #do some error handling

    def market_order(self, inst, order_config={}):
        #lets try to make a fill or kill market order - read the documentation for the order types and what they mean
        contract_change = order_config["rounded_contracts"] - order_config["current_contracts"]
        order_data = {
            "order": {
            "price": "", #market order is liqudity taking
            "timeInForce": "FOK",
            "instrument": inst,
            "units": str(contract_change),
            "type": "MARKET",
            "positionFill": "DEFAULT"
            }
        }
        print(json.dumps(order_config, indent=4))
        print(json.dumps(order_data, indent=4))
        r = orders.OrderCreate(accountID=self.id, data=order_data)
        self.client.request(r)
        return r.response
        
    #we need to implement these functionalities to have a `successful` TradeClient. This is what is `promised` to be implemented to other components of the trading system, 
    #no matter what brokerage is used!
    #lets now implement these wrapper functions

