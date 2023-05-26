
import os
import pandas as pd
import datetime
from dotenv import load_dotenv

from binance.um_futures import UMFutures
from quantlib.crypto_format_utils import format_price, format_quantity

from collections import defaultdict

class TradeClient():

    def __init__(self, brokerage_config=None, auth_config=None, service_client=None):
        load_dotenv()
        self.key=os.getenv("KEY")
        self.secret =os.getenv("SECRET")
        self.client = UMFutures(key=self.key, secret=self.secret)
        self.mark_price = None

    """
    We are interested in getting
    1. Capital
    2. Positions
    3. Submit Orders
    4. Get OHLCV data etc
    """
    def get_mark_price(self):
        """Get the current market mark price when needed"""
        self.mark_price = self.client.mark_price()

    def get_account_details(self):
        try:
            return self.client.account()
        except Exception as err:
            print(err)

    def get_account_summary(self):
        pass

    def get_account_instruments(self):
        #Get the list of tradable instruments for the given Account. The list of tradeable instruments is dependent on the regulatory division that the Account is located in
        #we can get financing rates for instruments here , etc
        try:
            positions = self.get_account_details()['positions']
            instruments = [x['symbol'] for x in positions]
            return instruments
        except Exception as e:
            print (e)

    def get_account_capital(self):
        try:
            return float(self.get_account_summary()["totalWalletBalance"])
        except Exception as err:
            pass

    def get_account_available_balance(self):
        try:
            return float(self.get_account_summary()["availableBalance"])
        except Exception as e:
            print (e)

    #we can try to enter some positions or trades to see what the return result looks like
    #we see that the Oanda brokerage automatically performs netting of positions
    #we bought 30 EUR_USD units, sold 6, and we have 24 units of open positions
    #do note that this is not the same for every brokerage. In some cases, brokerages allow two open trades of opposing direction without netting
    #this would cause the txn fees to increase!
    def get_account_positions(self):
        positions_data = self.get_account_details()["positions"]
        positions = {}
        for entry in positions_data:
            instrument = entry["symbol"]
            positionAmt = float(entry["positionAmt"])
            entryPrice = float(entry["entryPrice"])
            unrealizedProfit = float(entry["unrealizedProfit"])
            if positionAmt != 0:
                positions[instrument] = {
                    "positionAmt": positionAmt,
                    "entryPrice": entryPrice,
                    "unrealizedProfit": unrealizedProfit,
                }
        return positions

    def get_account_trades(self):
        pass

    def format_date(self, series):
        #series in the form :: 2021-09-21T21:00:00.000000000Z
        ddmmyy = series.split("T")[0].split("-")
        return datetime.date(int(ddmmyy[0]), int(ddmmyy[1]), int(ddmmyy[2]))

    def get_ohlcv(self, instrument, count, granularity):
        pass
    
    def set_isolated_leverage(self, symbol, leverage):
        try:
            res = self.client.change_leverage(symbol=symbol, leverage=leverage)
            res = self.client.change_margin_type(
                symbol=symbol, marginType="ISOLATED")
        except Exception as e:
            print (e)
            print ("Seems already isolated!")

    def repeat_orders(self, kwargs, times=5):
        response = None
        for i in range(times):
            try:
                response = self.client.new_order(**kwargs)
            except Exception as e:
                continue
            break
        return response

    def make_market_order(self, symbol, order_config={}, open=False):
        # quantity should indicate the side
        if open:
            self.set_isolated_leverage(symbol=symbol, leverage=order_config["leverage"])
        MARKET_SLIPPERAGE = 0.03
        quantity = float(order_config["quantity"])
        reduce_only = order_config.get("reduceOnly", False)
        if quantity < 0:
            position_side = "SELL"
            price = float(order_config["price"]) * (1-MARKET_SLIPPERAGE)
        else:
            position_side = "BUY"
            price = float(order_config["price"]) * (1+MARKET_SLIPPERAGE)
        
        params = {
            'symbol': symbol,
            'side': position_side,
            'type': 'LIMIT',
            'quantity': format_quantity(abs(quantity), price),
            'price': format_price(price),
            'timeInForce': 'GTC',
            'reduceOnly': reduce_only
        }
        print (params)
        res = self.repeat_orders(params)
        return res
    
    def close(self, symbol):
        positions = self.get_account_positions()
        try:
            details = positions[symbol]
            self.close_positon(symbol, details)
        except:
            print (f"There is no such position for {symbol}!")
            return
        
    def close_positon(self, symbol, details):
        try:
            quantity = 0-details['positionAmt'] # Take the opposite to close a position
            price = self.get_current_price(symbol)
            price = format_price(price)

            order_config = {
                "reduceOnly": True,
                "quantity": format_quantity(quantity, price),
                "price": price
            }
            response = self.make_market_order(symbol, order_config=order_config)
            return response
        except Exception as e:
            print (f"Error when closing position for {symbol}!")
            print (e)
    
    def open_position(self, symbol, param):
        try:
            price = self.get_current_price(symbol)
            price = format_price(price)
            nominal_usd = param['leverage'] * param['collateral']

            quantity = nominal_usd / price
            quantity = format_quantity(quantity, price)
            if param['side'] == "SELL":
                quantity = -quantity
            order_config = {
                "quantity": quantity,
                "price": price,
                "leverage": param['leverage']
            }
            response = self.make_market_order(symbol, order_config=order_config, open=True)
            return response
        except Exception as e:
            print (f"Error when opening position for {symbol}!")
            print (e)

    def get_current_price(self, symbol):
        if not self.mark_price:
            self.get_mark_price()
        for element in self.mark_price:
            if element['symbol'] == symbol:
                return float(element['markPrice'])
        return
        

if __name__ == "__main__":
    trade_client = TradeClient()
    symbol = "WAVESUSDT"
    order_config = {
        "quantity": 20,
        "price": 3.05,
        "leverage": 3
    }
    #trade_client.market_order(symbol, order_config)
    #print (trade_client.get_account_details()['positions'])
    #print (trade_client.client.mark_price())

    BUY_PARAMS = {
        "side": "BUY",
        "leverage": 3,
        "collateral": 10,
    }
    trade_client.close(symbol)