from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import MetaTrader5 as mt5
import numpy as np
import pytz
pd.set_option('display.max_columns', 500) # number of columns to be displayed
pd.set_option('display.width', 1500)      # max table width to display
# pylint: disable=maybe-no-member
# connect to MetaTrader 5
if not mt5.initialize():
    print("initialize() failed")
    mt5.shutdown()

#print(mt5.account_info()._asdict())
# display data on MetaTrader 5 version
#print(mt5.version())

#print(mt5.symbol_info("EURJPY#").bid, mt5.symbol_info("EURJPY#").ask)

lasttick=mt5.symbol_info_tick("EURJPY#")
#print(lasttick)

# set time zone to UTC
timezone = pytz.timezone("Etc/UTC")
# create 'datetime' object in UTC time zone to avoid the implementation of a local time zone offset
utc_from = datetime(2022, 2, 19, tzinfo=timezone)
rates = mt5.copy_rates_from("EURJPY#", mt5.TIMEFRAME_H1, utc_from, 25)

timezone = pytz.timezone("Etc/UTC")
# create 'datetime' objects in UTC time zone to avoid the implementation of a local time zone offset
utc_from = datetime(2020, 1, 10, tzinfo=timezone)
utc_to = datetime(2020, 1, 11, hour = 10, tzinfo=timezone)
# get bars from USDJPY M5 within the interval of 2020.01.10 00:00 - 2020.01.11 13:00 in UTC time zone
rates2 = mt5.copy_rates_range("EURJPY#", mt5.TIMEFRAME_H1, utc_from, utc_to)
print(np.asarray(rates[:-1]))
for idx, rate in enumerate(rates):
    if idx != 24:
        time = pd.to_datetime(rate[0], unit='s')
        #print(rate)
# create DataFrame out of the obtained data
rates_frame = pd.DataFrame(rates)
rates_frame2 = pd.DataFrame(rates2)
# convert time in seconds into the datetime format
rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
rates_frame2['time']=pd.to_datetime(rates_frame2['time'], unit='s')
orders=mt5.orders_total()
#print(orders)
print(rates_frame)
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()