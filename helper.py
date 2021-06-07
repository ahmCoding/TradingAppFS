
import alpaca_trade_api as tradeapi
import appConfig
import datetime
import talib
import pandas as pd

# get handel of alpaca-api
def alpacaApi():
    api = tradeapi.REST(appConfig.apiKey, appConfig.secretKey, base_url=appConfig.baseUrl)
    return api


# Dynamic calculation of order-size
def calcSizeOfOrder(price):
    api = alpacaApi()
    accontInfo=api.get_account()
    cash=float(accontInfo.__getattr__('cash'))
    buyPower=float(accontInfo.__getattr__('buying_power'))
    if cash>=price:
        if price>(cash*0.15):
            return 1
        else:
            #10 przent of current buypower for new order
            return(buyPower*0.10)//price


#this function has to be execute 20 minits bevor market_closing
def closeAllPositions():
    api=alpacaApi()
    close=api.close_all_positions()
    print(close)

# return the date of today and the date of (today - @daysAgo)
# todays date will caculate for daily data after market close (in Germany 10 PM)
# for intraday data is todays date the current date of time
def calcDate(daysAgo=1,intraday=False):
    if intraday:
        today=datetime.date.today()
    else:
        now=str(datetime.datetime.now()).split('.')[0]
        t1=datetime.datetime.strptime(now,"%Y-%m-%d %H:%M:%S")
        t2=now.split(' ')[0]+" 22:00:00"
        t2=datetime.datetime.strptime(t2,"%Y-%m-%d %H:%M:%S")
        t3=now.split(' ')[0]+" 00:00:00"
        t3=datetime.datetime.strptime(now,"%Y-%m-%d %H:%M:%S")
        if (t1 >t2 and t1<t3):
            today=datetime.date.today()
        else:
            today=datetime.date.today()-datetime.timedelta(days=1)
    pastDays=(today-datetime.timedelta(days=daysAgo))

    EB = 'Europe/Berlin'
    startD = pd.Timestamp(pastDays, tz=EB).isoformat()
    endD = pd.Timestamp(today, tz=EB).isoformat()
    return startD,endD


# set a traling-order by market orders
def tralingStop(symbol,side,quantity,atiTrail=False):
    api=alpacaApi()
    timeF='1D'
    # 6 procent of price
    procentageToTrail='0.6'
    if side=='sell':
        tralingSide='buy'
    else:
        tralingSide='sell'
    if atiTrail:
        atrPeriod=14
        startD,endD=calcDate(daysAgo=25)
        data=api.get_barset(symbol=symbol,timeframe=timeF,start=startD,end=endD).df
        atr=talib.ATR(data.A.high.values,data.A.low.values,data.A.close.values,timeperiod=atrPeriod)[-1]
        api.submit_order(symbol=symbol,side=tralingSide,type='trailing_stop',qty=quantity,time_in_force='day',trail_price=str(atr))
    else:
        api.submit_order(symbol=symbol,side=tralingSide,type='trailing_stop',qty=quantity,time_in_force='day',trail_percent='0.6')
