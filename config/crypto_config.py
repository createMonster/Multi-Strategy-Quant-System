
########SETTINGS################
long_amount = 3500
short_amount = long_amount * 0.6
long_nums, short_nums = 1, 12
################################

long_leverage, short_leverage = 3, 2
long_collateral = int(long_amount / long_leverage / long_nums)
short_collateral = int(short_amount / short_leverage / short_nums)

BUY_PARAMS = {
    "side": "BUY",
    "leverage": long_leverage,
    "collateral": long_collateral,
}

SELL_PARAMS = {
    "side": "SELL",
    "leverage": short_leverage,
    "collateral": short_collateral,
}

if __name__ == "__main__":
    print (BUY_PARAMS)
    print (SELL_PARAMS)