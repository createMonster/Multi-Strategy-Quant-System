import json
import pandas as pd
import quantlib.indicators_cal as indicators_cal
class Lbmom:

    def __init__(self, instruments_config, historical_df, simulation_start, vol_target):
        self.pairs = [(44, 100), (156, 245), (23, 184), (176, 290), (215, 288), (245, 298), (59, 127), (134, 275), (220, 286), (60, 168), (208, 249), (19, 152), (38, 122), (234, 254), (227, 293), (64, 186), (28, 49), (22, 106), (25, 212), (144, 148), (260, 284)]
        self.historical_df = historical_df
        self.simulation_start = simulation_start
        self.vol_target = vol_target #we adopt the volatility targetting risk framework. 
        #https://hangukquant.substack.com/p/volatility-targeting-the-strategy
        #https://hangukquant.substack.com/p/volatility-targeting-the-asset-level
        with open(instruments_config) as f:
            self.instruments_config = json.load(f)
        self.sysname = "LBMOM"

    """
    Let's Implement the Strategy `API`: this is what the class Lbmom `promises` to implement other components of the trading system
    We want to implement
    1. Function to get data and indicators specific to strategy
    2. Function to run backtest and get positions
    """

    def extend_historicals(self, instruments, historical_data):
        #we need to obtain data with regards to the LBMOM strategy
        #in particular, we want the moving averages, which is a proxy for momentum factor
        #we also want a univariate statistical factor as an indicator of regime. We use the average directional index ADX as a proxy for momentum regime indicator
        for inst in instruments:
            historical_data["{} adx".format(inst)] = indicators_cal.adx_series(
                high=historical_data["{} high".format(inst)],
                low=historical_data["{} low".format(inst)],
                close=historical_data["{} close".format(inst)],
                n=14
            )
            for pair in self.pairs:
                #calculate the fastMA - slowMA
                historical_data["{} ema{}".format(inst, str(pair))] = indicators_cal.ema_series(historical_data["{} close".format(inst)], n=pair[0]) - \
                    indicators_cal.ema_series(historical_data["{} close".format(inst)], n=pair[1])
        #the historical_data has all the information required for backtesting                
        return historical_data

    def run_simulation(self, historical_data):
        """
        Init Params
        """
        instruments = self.instruments_config["instruments"]

        """
        Pre-processing
        """
        historical_data = self.extend_historicals(instruments=instruments, historical_data=historical_data)
        print(historical_data)
        portfolio_df = pd.DataFrame(index=historical_data[self.simulation_start:].index).reset_index()
        portfolio_df.loc[0, "capital"] = 10000
        print(portfolio_df)

        """
        Run Simulation
        """
        
        pass

    def get_subsys_pos(self):
        self.run_simulation(historical_data=self.historical_df)
