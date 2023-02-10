

from brokerage.darwinex.TradeClient import TradeClient
from brokerage.darwinex.ServiceClient import ServiceClient

#note that the contract specifications are different from oanda - each contract has different sizing
#for FX; 100000
#etc...
class Darwinex():

    def __init__(self, brokerage_config=None, auth_config=None):
        self.brokerage_config = brokerage_config
        self.auth_config=auth_config
        self.trade_client = None
        self.service_client = None

    def get_service_client(self):
        if self.service_client is None:
            self.service_client = ServiceClient(brokerage_config=self.brokerage_config)
        return self.service_client


    def get_trade_client(self):
        if self.trade_client is None:
            self.trade_client = TradeClient(
                brokerage_config=self.brokerage_config,
                auth_config=self.auth_config,
                service_client=self.get_service_client()
            )
        return self.trade_client