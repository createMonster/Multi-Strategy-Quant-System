import json
import datetime
import pandas as pd


from dateutil.relativedelta import relativedelta

import quantlib.data_utils as du
import quantlib.general_utils as gu

from subsystems.LBMOM.subsys import Lbmom
from brokerage.oanda.oanda import Oanda

with open("config/auth_config.json", "r") as f:
    auth_config = json.load(f)

with open("config/portfolio_config.json", "r") as f:
    portfolio_config = json.load(f)

with open("config/oan_config.json", "r") as f:
    brokerage_config = json.load(f)


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
print(list(historical_data)) #we have our inverse quotes for fx too, and we can then use this later on in the fx caclulations

"""
Risk Parameters
"""
VOL_TARGET = portfolio_config["vol_target"]
sim_start = datetime.date.today() - relativedelta(years=portfolio_config["sim_years"])

"""
Get Position of Subsystems
""" 

strat = Lbmom(
    instruments_config="./subsystems/LBMOM/config.json", 
    historical_df=historical_data, 
    simulation_start=sim_start, 
    vol_target=VOL_TARGET, 
    brokerage_used="oan"
)
strat.get_subsys_pos()
#we see that we can now run the same strategy we used on the sp500 dataset by using a new config file, instead of editing the code!


#since we perform caclulations in more than one currency denomination, we need to perform fx conversions!