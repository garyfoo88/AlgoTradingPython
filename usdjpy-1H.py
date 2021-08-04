from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import MetaTrader5 as mt5
import pytz
pd.set_option('display.max_columns', 500) # number of columns to be displayed
pd.set_option('display.width', 1500)      # max table width to display
import time
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


print(price_bid, price_ask)


#Functions(1H indicators)

def calculateHomeData(rate_data):
    valueSumHome = 0
    counter = 1
    for rate in (rate_data):
        valueSumHome += rate[4]
        counter += 1
        if counter > 18:
            break
    return valueSumHome / 18

def calculateEMA18(rate_18_data):
    valueSum_18 = 0
    latestPrice_18 = 0
    for idx, rate in enumerate(rates_18[:-1]):
            if idx != 18:
                valueSum_18 += rate[4]
                #print(pd.to_datetime(rate[0], unit='s'))
            else:
                latestPrice_18 += rate[4]
    prevEma_18 = valueSum_18 /18
    ema_18 = (latestPrice_18 * weight_18) + (prevEma_18 * (1 - weight_18))
    return (ema_18 * correction_18)

def calculateEMA56(rate_data_56):
    valueSum_54 = 0
    latestPrice_54 = 0  
    for idx, rate in enumerate(rates_54[:-1]):

        if idx != 54:
            valueSum_54 += rate[4]
        else:
            latestPrice_54 += rate[4]
    prevEma_54 = valueSum_54 / 54
    ema_54 = (latestPrice_54 * weight_54) + (prevEma_54 * (1 - weight_54))
    return (ema_54 * correction_54)

def calculateSMA200(rate_data_200):
    valueSum_200 = 0
    for rate in (rates_200[:-1]):
        valueSum_200 += rate[4]
    return valueSum_200 / 200

#Functions(4H indicators)



#Event Loop
while True:
    isToday = False
    isHome = False
    last_24_data = {}
    today_data = {}
    counter = 0
    rates_18 =  mt5.copy_rates_from(symbol, mt5.TIMEFRAME_H1, utc_from, 20)
    rates_24 = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_H1, utc_from, 25)[:-1]
    rates_54 = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_H1, utc_from, 56)
    rates_200 = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_H1, utc_from, 201)
    rates_18_4H = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_H4, utc_from, 20)
    rates_54_4H = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_H4, utc_from, 56)
    rates_200_4H = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_H4, utc_from, 201)
    latestTime = str(pd.to_datetime(rates_18[-1][0], unit='s'))[11:13]

    #Store last 24 candle's data and current day data
    for idx, rate in enumerate(rates_24):
        
        if isToday:
            today_data[counter] = {
            "open": rate[1],
            "close": rate[4],
            "high": rate[2],
            "low": rate[3]
            }
            counter +=1

        if str(pd.to_datetime(rate[0], unit='s'))[11:13] == "00":
            isToday = True
            today_data[counter] = {
            "open": rate[1],
            "close": rate[4],
            "high": rate[2],
            "low": rate[3]
            }
            counter += 1

        last_24_data[str(pd.to_datetime(rate[0], unit='s'))[11:13]] = {
            "open": rate[1],
            "close": rate[4],
            "high": rate[2],
            "low": rate[3]
        }

    #Calculate data for HOME from current day data
    for idx, rate in enumerate(today_data):
        data_high = today_data[idx]['high']
        data_low = today_data[idx]['low']
        today_data[idx]['home'] = calculateHomeData(mt5.copy_rates_from(symbol, mt5.TIMEFRAME_H1, utc_from, 18 + len(today_data) - idx))
        if data_high > today_data[idx]['home'] and data_low < today_data[idx]['home']:
            isHome = True

    #Evaluate data every hour and when price is home for the day
    if (currentTime == latestTime and isHome):
        #result = mt5.order_send(sell_request)
        #result = mt5.order_send(buy_request)
        final_ema_18 = calculateEMA18(rates_18)
        final_ema_54 = calculateEMA56(rates_54)
        final_sma_200 = calculateSMA200(rates_200)
        #Check the three MA's trend (TODO: check the the MA range, if too close its consider ranging)
        if (final_sma_200 < final_ema_54 and final_ema_54 < final_ema_18):
            print('uptrend')
        elif (final_sma_200 > final_ema_54 and final_ema_54 > final_ema_18):
            print('downtrend')
        else:
            print('Ranging')

        if (int(currentTime) + 1 < 10):
            currentTime = "0" + str(int(latestTime) + 1)
        else:
            currentTime = str(int(latestTime) + 1)

        print(latestTime, currentTime, final_ema_18, final_ema_54, final_sma_200)
        
        
   

    time.sleep(60)


