#interacts with the oandapyV20 api to make, update, delete and read orders
#the documentation and code samples give us all the info we need! https://readthedocs.org/projects/oanda-api-v20/downloads/pdf/latest/

import json
import time
import datetime
import pandas as pd
import heapq


from collections import defaultdict
from dateutil.relativedelta import relativedelta
from decimal import Decimal #this helps with floating point errors and arithmetic between strings

from brokerage.darwinex.DWX_ZeroMQ_Connector_v2_0_1_RC8 import DWX_ZeroMQ_Connector

class TradeClient():

    def __init__(self, brokerage_config=None, auth_config=None, service_client=None):
        self.dwx_config = brokerage_config
        self._zmqclient = DWX_ZeroMQ_Connector(_verbose=False)
        self.auth_config = auth_config
        self.service_client = service_client

    #recall that the result is not immediate, we should sleep for a moment for TCP socket to retrieve the data
    def _request_result(self, s_delay=0.5):
        time.sleep(s_delay)
        return self._zmqclient._get_response_()

    def get_account_details(self):
        try:
            self._zmqclient._DWX_GET_ACCOUNT_DETAILS()
            res = self._request_result()
            return dict(res)
        except Exception as err:
            print(err)

    def get_account_summary(self):
        try:
            return self.get_account_details() #there is only one function in DWX_ZeroMQ connector to get account details that we implemented
        except Exception as err:
            print(err)
            #do your error handling

    def get_account_instruments(self):
        pass #we already scraped the assets tradable

    def get_account_capital(self):
        try:
            return float(self.get_account_summary()["_equity"]) #this is the result we passed back from the MT4 terminal
        except Exception as err:
            pass

    def get_account_positions(self):
        trades = self.get_account_trades()
        positions = defaultdict(Decimal)
        for id in trades.keys():
            details = trades[id]
            if len(details) != 0:
                instrument = self.service_client.code_to_label_nomenclature(code=details["_symbol"])
                lots = Decimal(str(details["_lots"]))
                multiplier = 1 if details["_type"] == 0 else -1
                positions[instrument] += Decimal(str(lots * multiplier))
        return positions

    def get_account_trades(self):
        client = self._zmqclient
        client._DWX_MTX_GET_ALL_OPEN_TRADES_()
        res = self._request_result()
        trades = dict(res)["_trades"]
        return trades

    def format_date(self, series):
        #series in the form :: 2022.01.11 00:00 
        ddmmyy = series.split(" ")[0].split(".")
        return datetime.date(int(ddmmyy[0]), int(ddmmyy[1]), int(ddmmyy[2]))

    """
    _DWX_MTX_SEND_HIST_REQUEST_(self,
                                 _symbol='EURUSD',
                                 _timeframe=1440,
                                 _start='2020.01.01 00:00:00',
                                 _end=Timestamp.now().strftime('%Y.%m.%d %H:%M:00')):
                                 #_end='2019.01.04 17:05:00'):
        
    note that the parameters start and end is no longer a count, but a timestamp in strftime
    """
    def get_ohlcv(self, instrument, count, granularity):
        try:
            client = self._zmqclient
            start = datetime.date.today()
            end = start - relativedelta(days=count) #we convert the count units into the format that DWX takes
            start = start.strftime('%Y.%m.%d %H:%M:00')
            end = end.strftime('%Y.%m.%d %H:%M:00')
            client._DWX_MTX_SEND_HIST_REQUEST_(
                _symbol=self.service_client.label_to_code_nomenclature(label=instrument),
                _start=start,
                _end=end
            )
            res = self._request_result()
            #we see that we manage to get the HIST request data back, and now need to convert this into a ohlcv df format that our internal logic will accept
            return_instrument = res["_symbol"].split("_")[0] if res["_symbol"].split("_")[1] == "D1" else None
            if return_instrument == self.service_client.label_to_code_nomenclature(label=instrument):
                ohlcv = pd.DataFrame(res["_data"])
                ohlcv["time"] = ohlcv["time"].apply(lambda x: self.format_date(x))
                ohlcv.drop(columns=["spread", "real_volume"], inplace=True)
                ohlcv.rename(columns={"time": "date", "tick_volume": "volume"}, inplace=True)
                ohlcv.set_index("date", inplace=True)
                ohlcv.loc[~ohlcv.index.duplicated(keep="first")]
                ohlcv = ohlcv.apply(pd.to_numeric)
                ohlcv.reset_index(inplace=True)
            return ohlcv
        except Exception as err:
            raise ConnectionError("Fail to retrieve instrument {} : ".format(str(err)) + instrument)

    def _get_trades_stack(self, open_trades, inst):
        pass #get the stack of open trades in long and short position separately
        long_stack = []
        short_stack = []
        for id in open_trades.keys():
            details = open_trades[id]
            if len(details) != 0:
                instrument = self.service_client.code_to_label_nomenclature(code=details["_symbol"])
                if inst == instrument:
                    contracts = details["_lots"]
                    if details["_type"] == 0:
                        heapq.heappush(long_stack, (contracts, id)) #k, v pair where contracts it the `priority` value
                    elif details["_type"] == 1:
                        heapq.heappush(short_stack, (contracts, id))
                    else:
                        print("market order type can only be 0 or 1")
                        exit()
        return long_stack, short_stack


    def _new_market_order(self, inst, contract_change): #a new market order
        trade = self._get_market_order_dict(inst, contract_change)
        self._zmqclient._DWX_MTX_NEW_TRADE_(_order=trade)
        res = self._request_result(1) #lets wait longer on more sensitive operations
        return res
    
    def _get_market_order_dict(self, inst, contract_change):
        return ({'_action': 'OPEN',
                  '_type': 0 if contract_change > 0 else 1,
                  '_symbol': self.service_client.label_to_code_nomenclature(inst),
                  '_price': 0.0,
                  '_SL': 0, # SL/TP in POINTS, not pips.
                  '_TP': 0,
                  '_comment': "HANGUKQUANT ORDER",
                  '_lots': abs(contract_change),
                  '_magic': 123456,
                  '_ticket': 0})

    def _adjust_order_market(self, inst, contract_change, long_stack, short_stack, is_long):
        #we first want to reduce the open position or close position starting from the smallest position in inst
        client = self._zmqclient
        if (is_long and short_stack and not long_stack):
            #reduce a short position and get relatively longer
            while short_stack and contract_change > 0: #start shaving from the short stack, using min heapq to get the smallest contract position
                smallest_short, ticket_id = heapq.heappop(short_stack)
                if smallest_short > contract_change:
                    #then close partially the smallest position
                    client._DWX_MTX_CLOSE_PARTIAL_BY_TICKET_(
                        _ticket=ticket_id, _lots=abs(round(contract_change, 2))
                    )
                    res = self._request_result(1)
                    contract_change = 0
                elif smallest_short <= contract_change:
                    #then close the entire position and reanalyze the stack
                    client._DWX_MTX_CLOSE_TRADE_BY_TICKET_(_ticket=ticket_id)
                    res = self._request_result(1)
                    contract_change -= smallest_short #we still might have remaining short positions to reduce or kill
            if contract_change < 0:
                raise Exception("Order Logic is Wrong") #means we undershot
            elif contract_change > 0 and not short_stack: #means after clearing our shorts, we still have longs to add so we reverse position into net long
                trade = self._new_market_order(inst, contract_change)
                res = self._request_result(1)
                contract_change = 0

        elif (not is_long and long_stack and not short_stack): #do the opposite
            #reduce a long position and get relatively shorter
            while long_stack and contract_change < 0: 
                smallest_long, ticket_id = heapq.heappop(long_stack)
                if smallest_long > abs(contract_change):
                    #then close partially the smallest position
                    client._DWX_MTX_CLOSE_PARTIAL_BY_TICKET_(
                        _ticket=ticket_id, _lots=abs(round(contract_change, 2))
                    )
                    res = self._request_result(1)
                    contract_change = 0
                elif smallest_long <= abs(contract_change):
                    #then close the entire position and reanalyze the stack
                    client._DWX_MTX_CLOSE_TRADE_BY_TICKET_(_ticket=ticket_id)
                    res = self._request_result(1)
                    contract_change += smallest_long
            if contract_change > 0:
                raise Exception("Order Logic is Wrong") #means we undershot
            elif contract_change < 0 and not long_stack: #means after clearing our longs, we still have shorts to add so we reverse position into net short
                trade = self._new_market_order(inst, contract_change)
                res = self._request_result(1)
                contract_change = 0
        return res

    def market_order(self, inst, order_config={}): #generic market order
        client = self._zmqclient
        is_new = order_config["current_contracts"] == 0
        contract_change = round(order_config["rounded_contracts"] - order_config["current_contracts"], 2)
        is_long = contract_change > 0
        if is_new:
            print("Opening New Trades")
            res = self._new_market_order(inst, contract_change)
            return res
        else:
            open_trades = self.get_account_trades()
            long_stack, short_stack = self._get_trades_stack(open_trades, inst)
            if (not long_stack and not short_stack) or (long_stack and short_stack):
                raise Exception("Positions data invalid, please first close opposing trades")
            if (is_long and long_stack and not short_stack) or (not is_long and short_stack and not long_stack):
                print("Accumulating existing trade")
                res = self._new_market_order(inst, contract_change)
                return res
            elif (is_long and short_stack and not long_stack) or (not is_long and long_stack and not short_stack):
                print("Edit existing trade in opposite direction")
                res = self._adjust_order_market(inst, contract_change, long_stack, short_stack, is_long)
                return res
            else:
                raise Exception("Unknown Configuration, Check Logic")
