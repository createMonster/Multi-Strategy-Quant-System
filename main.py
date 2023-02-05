import json
import pandas as pd

from dateutil.relativedelta import relativedelta

import quantlib.data_utils as du
import quantlib.general_utils as gu

from subsystems.LBMOM.subsys import Lbmom

df, instruments = gu.load_file("./Data/data.obj")
print(df, instruments)

#run simulation for 5 years
VOL_TARGET = 0.20
print(df.index[-1]) #date today: 2022-02-04
sim_start = df.index[-1] - relativedelta(years=5)
print(sim_start) #start trading backtest from 017-02-04

strat = Lbmom(instruments_config="./subsystems/LBMOM/config.json", historical_df=df, simulation_start=sim_start, vol_target=VOL_TARGET)
strat.get_subsys_pos()
