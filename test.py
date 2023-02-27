import json
import datetime
import pandas as pd

from dateutil.relativedelta import relativedelta

import quantlib.data_utils as du
import quantlib.crypto_data_utils as crypto_du
import quantlib.general_utils as gu
import quantlib.backtest_utils as backtest_utils
import quantlib.diagnostics_utils as diagnostic_utils
from quantlib.printer_utils import Printer as Printer
from quantlib.printer_utils import _Colors as Colors
from quantlib.printer_utils import _Highlights as Highlights

from brokerage.oanda.oanda import Oanda
from subsystems.LBMOM.crypto import Lbmom
from subsystems.LSMOM.subsys import Lsmom
from subsystems.SKPRM.subsys import Skprm

import warnings
warnings.filterwarnings("ignore")

with open("config/auth_config.json", "r") as f:
    auth_config = json.load(f)

with open("config/portfolio_config.json", "r") as f:
    portfolio_config = json.load(f)


brokerage_used = portfolio_config["brokerage"]
brokerage_config_path = portfolio_config["brokerage_config"][brokerage_used]
db_file = portfolio_config["database"][brokerage_used]

with open("config/{}".format(brokerage_config_path), "r") as f:
    brokerage_config = json.load(f)

if brokerage_used == "oan":
    brokerage = Oanda(brokerage_config=brokerage_config, auth_config=auth_config)
    db_instruments = brokerage_config["fx"] +  brokerage_config["indices"] + brokerage_config["commodities"] + brokerage_config["metals"] + brokerage_config["bonds"] + brokerage_config["crypto"]
else:
    print("unknown brokerage, try again.")
    exit()



subsystem = "lbmom"
db_instruments = crypto_du.get_symbols()
db_file = "crypto_ohlv_4h.xlsx"
db_file_path = f"./Data/{db_file}"
database_df = pd.read_excel(db_file_path).set_index("open_time")

new_df, instruments = crypto_du.get_crypto_futures_df(interval="4h", limit=200)
merge_df = pd.concat([database_df, new_df]).drop_duplicates(keep="first")


#new_file = "crypto_ohlv_4h.xlsx"
#new_df = pd.read_excel(new_file).set_index("open_time")
#merge_df = pd.concat([new_df, database_df]).drop_duplicates()

merge_df = merge_df.sort_index()
merge_df.to_excel(db_file_path)
historical_data = crypto_du.extend_dataframe(traded=db_instruments, df=merge_df, interval="4h")
historical_data.to_excel("crypto_historical_4h.xlsx")
exit()
VOL_TARGET = 0.2
sim_start = datetime.date.today() - relativedelta(days=30)
print (sim_start)

strat = Lbmom(
                instruments_config=portfolio_cnfig["instruments_config"][subsystem][brokerage_used], 
                historical_df=historical_data, 
                simulation_start=sim_start, 
                vol_target=VOL_TARGET, 
                brokerage_used="binance"
)
portfolio_df, instruments = strat.get_subsys_pos(debug=True, use_disk=False)
print (instruments)