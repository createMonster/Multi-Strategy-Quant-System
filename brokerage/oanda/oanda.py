#I already created a demo oanda account. pip install oandapyV20, and generate your own API key
#READ the documentation and code samples! We are choosing the REST API option instead of the streaming option.
# oanda_id: 101-003-13732651-006
# oanda_key:  6320bb8b1dd427ff7b5c6dd31f00675e-05e3c53f0a74851c18d25b929510b2cd

from brokerage.oanda.TradeClient import TradeClient
from brokerage.oanda.ServiceClient import ServiceClient

class Oanda():

    def __init__(self, brokerage_config=None, auth_config=None):
        self.service_client = ServiceClient(brokerage_config=brokerage_config)
        self.trade_client = TradeClient(auth_config=auth_config)
    #lets create a service class and trade class for Oanda

    def get_service_client(self):
        return self.service_client

    def get_trade_client(self):
        return self.trade_client