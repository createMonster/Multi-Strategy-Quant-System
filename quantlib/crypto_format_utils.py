"""Crypto format utils functions"""

def format_quantity(quantity, price):
    if price < 100:
        quantity = int("{:.0f}".format(quantity))
    elif price < 250:
        quantity = float("{:.1f}".format(quantity))
    elif price < 10000:
        quantity = float("{:.2f}".format(quantity))
    else:
        quantity = float("{:.3f}".format(quantity))

    return quantity

def format_price(stop_price):

    if stop_price < 0.01:
        stop_price = float("{:.5f}".format(stop_price))
    elif stop_price < 0.5:
        stop_price = float("{:.4f}".format(stop_price))
    elif stop_price < 10:
        stop_price = float("{:.3f}".format(stop_price))
    elif stop_price < 200:
        stop_price = float("{:.2f}".format(stop_price))
    else:
        stop_price = float("{:.1f}".format(stop_price))

    return stop_price