import json
import datetime
import pandas as pd


from dateutil.relativedelta import relativedelta

import quantlib.data_utils as du
import quantlib.general_utils as gu

from brokerage.oanda.oanda import Oanda
from subsystems.LBMOM.subsys import Lbmom
from subsystems.LSMOM.subsys import Lsmom

with open("config/auth_config.json", "r") as f:
    auth_config = json.load(f)

with open("config/portfolio_config.json", "r") as f:
    portfolio_config = json.load(f)

with open("config/oan_config.json", "r") as f:
    brokerage_config = json.load(f)

def main():
    #lets write a master config file
    brokerage = Oanda(auth_config=auth_config)
    db_instruments = brokerage_config["fx"] +  brokerage_config["indices"] + brokerage_config["commodities"] + brokerage_config["metals"] + brokerage_config["bonds"] + brokerage_config["crypto"]

    """
    Load and Update the Database
    """
    database_df = gu.load_file("./Data/oan_ohlcv.obj")
    #database_df = pd.read_excel("./Data/oan_ohlcv.xlsx").set_index("date")
    print(database_df) #now we can obtain, update and maintain the database from Oanda instead of the sp500 dataset!

    #save time, but we want to uncomment this laters
    # poll_df = pd.DataFrame()
    # for db_inst in db_instruments:
    #     df = brokerage.get_trade_client().get_ohlcv(instrument=db_inst, count=30, granularity="D") #get daily candles for the last 30 data points
    #     df.set_index("date", inplace=True)
    #     print(db_inst, "\n", df)
    #     cols = list(map(lambda x: "{} {}".format(db_inst, x), df.columns)) 
    #     df.columns = cols
        
    #     if len(poll_df) == 0:
    #         poll_df[cols] = df
    #     else:
    #         poll_df = poll_df.combine_first(df) #Now we do not lose any data!


    # database_df = database_df.loc[:poll_df.index[0]][:-1] #this means take original database up to the starting point of the new database, and drop the overlapping data entry point
    # database_df = database_df.append(poll_df)
    # #database_df.to_excel("./Data/oan_ohlcv.xlsx") #lets not write to excel to save time!
    # gu.save_file("./Data/oan_ohlcv.obj", database_df)
        
    """
    Extend the Database
    """
    historical_data = du.extend_dataframe(traded=db_instruments, df=database_df, fx_codes=brokerage_config["fx_codes"])

    """
    Risk Parameters
    """
    VOL_TARGET = portfolio_config["vol_target"]
    sim_start = datetime.date.today() - relativedelta(years=portfolio_config["sim_years"])

    """
    Get existing positions and capital
    """
    capital = brokerage.get_trade_client().get_account_capital()
    positions = brokerage.get_trade_client().get_account_positions()
    print(capital, positions)
    
    """
    Get Position of Subsystems
    """ 
    subsystems_config = portfolio_config["subsystems"]["oan"]
    strats = {}
    
    for subsystem in subsystems_config.keys():
        if subsystem == "lbmom":
            strat = Lbmom(
                instruments_config=portfolio_config["instruments_config"][subsystem]["oan"], 
                historical_df=historical_data, 
                simulation_start=sim_start, 
                vol_target=VOL_TARGET, 
                brokerage_used="oan"
            )
        elif subsystem == "lsmom":
            strat = Lsmom(
                instruments_config=portfolio_config["instruments_config"][subsystem]["oan"], 
                historical_df=historical_data, 
                simulation_start=sim_start, 
                vol_target=VOL_TARGET, 
                brokerage_used="oan"
            )
        else:
            pass#...
        strats[subsystem] = strat
    
    
    for k, v in strats.items():
        print("run: ", k, v)
        #key value pair of strategy name, strategy object
        strat_db, strat_inst = v.get_subsys_pos(debug=True) #see if you want to print the items
        print(strat_db, strat_inst)


#we can now run the strategy from our main driver, and add more strategies!
#let's attempt to add a new strategy, using the code already implemented
#let us implement the lsmom strategy, which is similar to the lbmom strategy but with negative weights (holdings) too     
#we are now able to run multiple strategies from the driver, with minimal code changes and only editing the config files - this is essential for our alpha research purposes, in having our
#own testing engine.
#checkpoint 6!

if __name__ == "__main__":
    main()