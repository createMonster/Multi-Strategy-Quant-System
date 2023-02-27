from brokerage.binance.TradeClient import TradeClient
from brokerage.binance.ServiceClient import ServiceClient
from brokerage.binance.DataClient import DataClient

class Binance():

    def __init__(self, brokerage_config=None, auth_config=None):
        self.service_client = ServiceClient(brokerage_config=brokerage_config)
        self.trade_client = TradeClient(auth_config=auth_config)
        self.data_client = DataClient()
    #lets create a service class and trade class for Oanda

    def get_service_client(self):
        return self.service_client

    def get_trade_client(self):
        return self.trade_client
    
    def get_data_client(self):
        return self.data_client