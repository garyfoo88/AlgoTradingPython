from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import MetaTrader5 as mt5
import pytz
pd.set_option('display.max_columns', 500) # number of columns to be displayed
pd.set_option('display.width', 1500)      # max table width to display
import time
import talib
# pylint: disable=maybe-no-member
# connect to MetaTrader 5
currentTime = 0
weight_54 = 1/(54+1)
weight_18 = 1/(18+1)
correction_54 = 0.999554430872578
correction_18 = 0.999904430872578
lot = 0.1
symbol = "USDJPY#"
deviation = 20
timezone = pytz.timezone("etc/UTC")
utc_from = datetime(2023, 2, 19, tzinfo=timezone)
#Calculate current time
if int(str(datetime.now())[11:13])-6 < 10:
    currentTime = "0" + str(int(str(datetime.now())[11:13])-6)
else:
    currentTime = str(int(str(datetime.now())[11:13])-6)

if not mt5.initialize():
    print("initialize() failed")
    mt5.shutdown()

single_pip = mt5.symbol_info(symbol).point
#Use this for BUY orders
price_ask = mt5.symbol_info_tick(symbol).ask
price_bid = mt5.symbol_info_tick(symbol).bid
buy_request = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": symbol,
    "volume": lot,
    "type": mt5.ORDER_TYPE_BUY,
    "price": price_ask,
    "sl": price_ask - 300 * single_pip,
    "tp": price_ask + 300 * single_pip,
    "deviation": deviation,
    "magic": 234000,
    "comment": "python script open",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_IOC,
}

sell_request = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": symbol,
    "volume": lot,
    "type": mt5.ORDER_TYPE_SELL,
    "price": price_ask,
    "sl": price_ask + 300 * single_pip,
    "tp": price_ask - 300 * single_pip,
    "deviation": deviation,
    "magic": 234000,
    "comment": "python script open",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_IOC,
}

priceArray = []

rates =  mt5.copy_rates_from(symbol, mt5.TIMEFRAME_M15, utc_from, 400)
for rate in rates:
    priceArray.append(rate[4])

close = np.array(priceArray)
print(talib.SMA(close, timeperiod=20)[-2])
print(talib.SMA(close, timeperiod=64)[-2])
sma_84 = (talib.SMA(close, timeperiod=84)[-20:-1])

print(sma_84)