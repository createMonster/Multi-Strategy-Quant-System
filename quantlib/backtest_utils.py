import numpy as np
import pandas as pd

def get_backtest_day_stats(portfolio_df, instruments, date, date_prev, date_idx, historical_data, is_crypto=False):
    pnl = 0 #pnl for the day
    nominal_ret = 0 #nominal returns

    #we can either use vector operations to calculate returns or calculate one by one
    #the former is faster, but the latter is clearer and easier to interpret

    for inst in instruments:
        previous_holdings = portfolio_df.loc[date_idx - 1, "{} units".format(inst)]
        if previous_holdings != 0:
            price_change = historical_data.loc[date, "{} close".format(inst)] - historical_data.loc[date_prev, "{} close".format(inst)]
            if is_crypto:
                dollar_change = price_change
            else:
                dollar_change = unit_val_change(inst, price_change, historical_data, date_prev)
            dollar_change = price_change
            inst_pnl = dollar_change * previous_holdings
            pnl += inst_pnl
            nominal_ret += portfolio_df.loc[date_idx - 1, "{} w".format(inst)] * historical_data.loc[date, "{} % ret".format(inst)]
    
    capital_ret = nominal_ret * portfolio_df.loc[date_idx - 1, "leverage"]
    portfolio_df.loc[date_idx, "capital"] = portfolio_df.loc[date_idx - 1, "capital"] + pnl
    portfolio_df.loc[date_idx, "daily pnl"] = pnl
    portfolio_df.loc[date_idx, "nominal ret"] = nominal_ret
    portfolio_df.loc[date_idx, "capital ret"] = capital_ret
    return portfolio_df, pnl, capital_ret

#https://hangukquant.substack.com/p/volatility-targeting-the-strategy
def get_strat_scaler(portfolio_df, lookback, vol_target, idx, default):
    capital_ret_history = portfolio_df.loc[:idx].dropna().tail(lookback)["capital ret"]
    strat_scaler_history = portfolio_df.loc[:idx].dropna().tail(lookback)["strat scalar"]
    if len(capital_ret_history) == lookback:
        #enough data, then increase or decrease the scalar based on empirical vol of the strategy equity curve relative to target vol
        annualized_vol = capital_ret_history.std() * np.sqrt(253) #annualise the vol from daily vol
        scalar_hist_avg = np.mean(strat_scaler_history)
        strat_scalar = scalar_hist_avg * vol_target / annualized_vol
        return strat_scalar
    else:
        #not enough data, just return a default value
        return default

#How much is the price change in contract x worth in base currency USD?
"""
from_prod: instrument traded, e.g. HK33_HKD
val_change: change in price quote
"""
def unit_val_change(from_prod, val_change, historical_data, date):
    is_denominated = len(from_prod.split("_")) == 2
    if not is_denominated:
        return val_change #assume USD denominated, e.g. AAPL
    elif is_denominated and from_prod.split("_")[1] == "USD":
        return val_change #USD denominated, e.g. AAPL_USD, EUR_USD
    else:
        #e.g. HK33_HKD, USD_JPY (X_Y)
        #take delta price * (Y_USD) = price change in USD terms
        return val_change * historical_data.loc[date, "{}_USD close".format(from_prod.split("_")[1])]

#how much is 1 contract `worth`?
def unit_dollar_value(from_prod, historical_data, date):
    is_denominated = len(from_prod.split("_")) == 2
    if not is_denominated:
        return historical_data.loc[date, "{} close".format(from_prod)] #e.g. AAPL units is worth the price of 1 AAPL unit
    if is_denominated and from_prod.split("_")[0] == "USD":
        return 1 #e.g. USD_JPY unit is worth 1 USD!
    if is_denominated and not from_prod.split("_")[0] == "USD":
        #e.g.HK33_HKD, EUR_USD, (X_Y)
        #then you want to take the price change in the denominated currency, which is unit_price * Y_USD
        unit_price = historical_data.loc[date, "{} close".format(from_prod)]
        fx_inst = "{}_{}".format(from_prod.split("_")[1], "USD")
        fx_quote = 1 if fx_inst == "USD_USD" else historical_data.loc[date, "{} close".format(fx_inst)]
        return unit_price * fx_quote


def set_leverage_cap(portfolio_df, instruments, date, idx, nominal_tot, leverage_cap, historical_data):
    leverage = nominal_tot / portfolio_df.loc[idx, "capital"]
    if leverage > leverage_cap:
        new_nominals = 0
        leverage_scalar = leverage_cap / leverage
        for inst in instruments:
            newpos = portfolio_df.loc[idx, "{} units".format(inst)] * leverage_scalar
            portfolio_df.loc[idx, "{} units".format(inst)] = newpos
            if newpos != 0:
                new_nominals += abs(newpos * unit_dollar_value(inst, historical_data, date))
        return new_nominals
    else:
        return nominal_tot

#get some statistics from the portfolio df
def kpis(df):
    portfolio_df = df.copy()
    portfolio_df["cum ret"] = (1 + portfolio_df["capital ret"]).cumprod()
    portfolio_df["drawdown"] = portfolio_df["cum ret"] / portfolio_df["cum ret"].cummax() - 1
    sharpe = portfolio_df["capital ret"].mean() / portfolio_df["capital ret"].std() * np.sqrt(253)
    drawdown_max = portfolio_df["drawdown"].min() * 100
    volatility = portfolio_df["capital ret"].std() * np.sqrt(253) * 100 #annualised percent vol
    return portfolio_df, sharpe, drawdown_max, volatility