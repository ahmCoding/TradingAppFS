import sqlite3
import alpaca_trade_api as tradeapi
import appConfig
from datetime import date
import pandas as pd
import talib
from  notification import sendEmailNotification
from  datetime import datetime
#from timeZone import is_dst
from helper import *

def longBB():
    api = alpacaApi()# or use ENV Vars shown below
    clock=api.get_clock()
    today=date.today().isoformat()
    #check if the markt is open
    if clock.is_open:

        connection=sqlite3.connect(appConfig.dbAdress)
        #change tuple to object to accsess them like dics
        connection.row_factory=sqlite3.Row
        cursor=connection.cursor()
        cursor.execute("select id from strategy where name='Bollinger_Bands'")
        longStategyID = cursor.fetchone()[0]

        cursor.execute("""select symbol,name from stock join stock_strategy
         on stock_strategy.stock_id=stock.id where stock_strategy.strategy_id=?""",(longStategyID,))
        stock_on_strategy=cursor.fetchall()

        EB = 'America/New_York'
        startTime = pd.Timestamp(f'{today} 09:30', tz=EB).isoformat()
        endTime = pd.Timestamp(f'{today} 16:00', tz=EB).isoformat()

        symbols=[symbol['symbol'] for symbol in stock_on_strategy ]
        if symbols:
            #startTime = pd.Timestamp(f'{today} 09:30', tz=EB)
            #endTime = pd.Timestamp(f'{today} 09:45', tz=EB)

            #check if i have already some orders to avoid multiple order on same symbol
            orders=api.list_orders(status='all',after=today)
            openOrders=api.list_orders(status='open')
            existing_order_symbols=[order.symbol for order in orders if order.status!='canceled' and order not in openOrders]
            message = []
            #if any symbol exists in a watchlist for a trading strategy
            for symbol in symbols:
            #turn barset to data frame whith .df
                barsets = api.get_barset(symbol, '5Min', start=today).df
        #
        #             # für jedes element von index wird die bedingung in klammern geprueft und wenn
        #             # false eine 0 und wenn true ein 1 auf jeder seite
        #             # am ende werde die erzeugte 0 und 1.er Reihen mit einander bitweise und verknuepft
        #             # damit die erzeugte liste beide bedingungen enthaelt
                opening_mask=(barsets.index>=startTime) & (barsets.index<endTime)
                market_open_bars=barsets.loc[opening_mask]
                closes=market_open_bars[symbol]['close']
                opens=market_open_bars[symbol]['open']
                lenOfBB=20
                if len(closes)>lenOfBB:
                    upper, middle, lower = talib.BBANDS(closes,timeperiod=lenOfBB,nbdevup=2,nbdevdn=2,matype=0)
                    #current last canlde in the bar
                    curentC=closes[-1]
                    curentO=opens[-1]

                    pervCS=closes[-2]
                    #buyers check if last candle stick is with stronger buyers
                    buyers= curentC>curentO
                    if pervCS<lower[-2] and curentC>lower[-1] and buyers:
                        barRange = market_open_bars[symbol]['high'][-1] - market_open_bars[symbol]['low'][-1]
                        if symbol not in existing_order_symbols:
                            try:
                            #first bar in the list
                                tp=curentC+(barRange*2.5)
                                sl=pervCS
                            #hier put a bracket order made by alpaca api
                                # api.submit_order(
                                #     symbol=symbol,
                                #     qty=calcSizeOfOrder(curentC),
                                #     side='buy',
                                #     type='market',
                                #     time_in_force='day',
                                #     order_class='bracket',
                                #     stop_loss={'stop_price': sl},
                                #     take_profit={'limit_price': tp})
                                quantity=calcSizeOfOrder(curentC)
                                api.submit_order(
                                symbol=symbol,
                                qty=quantity,
                                side='buy',
                                type='market',
                                time_in_force='day')
                                tralingStop(symbol=symbol,side='buy',quantity=quantity,atiTrail=True)
                                print(f"new Order at {datetime.now()} places by {symbol}")
                                message.append(f"new Long Trade for {symbol} with price {curentC} , range of {barRange} , TP: {tp} and SL: {sl}\n\n")
                                #cursor.execute("delete from stock_strategy where stock_id=(select id from stock where symbol=?) ",(symbol,))
                                #connection.commit()
                            except Exception as e:
                                print(f"something is reeely schief gelaufen ! {e}")
                        else:
                            print(f"you already have on order in {symbol}")
            sendEmailNotification(message)


def shortBB():
    api = tradeapi.REST(appConfig.apiKey, appConfig.secretKey,base_url=appConfig.baseUrl)  # or use ENV Vars shown below
    clock = api.get_clock()
    today = date.today().isoformat()

    # check if the markt is open
    if clock.is_open:

        connection = sqlite3.connect(appConfig.dbAdress)
        # change tuple to object to accsess them like dics
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("select id from strategy where name='Bollinger_Bands'")
        bbStrategyId = cursor.fetchone()[0]

        cursor.execute("""select symbol,name from stock join stock_strategy
         on stock_strategy.stock_id=stock.id where stock_strategy.strategy_id=?""", (bbStrategyId,))
        stock_on_strategy = cursor.fetchall()

        EB = 'America/New_York'
        startTime = pd.Timestamp(f'{today} 09:30', tz=EB)
        endTime = pd.Timestamp(f'{today} 16:00', tz=EB)

        symbols = [symbol['symbol'] for symbol in stock_on_strategy]
        if symbols:
            # startTime = pd.Timestamp(f'{today} 09:30', tz=EB)
            # endTime = pd.Timestamp(f'{today} 09:45', tz=EB)

            # check if i have already some orders to avoid multiple order on same symbol
            orders = api.list_orders(status='all', after=today)
            openOrders = api.list_orders(status='open')
            existing_order_symbols = [order.symbol for order in orders if
                                      order.status != 'canceled' and order not in openOrders]
            message = []
            # if any symbol exists in a watchlist for a trading strategy
            for symbol in symbols:
                # turn barset to data frame whith .df
                barsets = api.get_barset(symbol, '5Min', start=today,end=endTime).df

                #
                #             # für jedes element von index wird die bedingung in klammern geprueft und wenn
                #             # false eine 0 und wenn true ein 1 auf jeder seite
                #             # am ende werde die erzeugte 0 und 1.er Reihen mit einander bitweise und verknuepft
                #             # damit die erzeugte liste beide bedingungen enthaelt
                opening_mask = (barsets.index >= startTime) & (barsets.index < endTime)
                market_open_bars = barsets.loc[opening_mask]
                closes = market_open_bars[symbol]['close']
                opens = market_open_bars[symbol]['open']
                lenOfBB = 20
                if len(closes) > lenOfBB:
                    upper, middle, lower = talib.BBANDS(closes, timeperiod=lenOfBB, nbdevup=2, nbdevdn=2, matype=0)
                    # current last canlde in the bar
                    curentC = closes[-1]
                    curentO = opens[-1]

                    pervCS = closes[-2]
                    # sellers check if last candle stick is with stronger buyers
                    sellers = curentC < curentO
                    if pervCS > lower[-2] and curentC < lower[-1] and sellers:
                        barRange = market_open_bars[symbol]['high'][-1] - market_open_bars[symbol]['low'][-1]
                        if symbol not in existing_order_symbols:
                            try:
                                # first bar in the list
                                tp = curentC - (barRange * 2.5)
                                sl = pervCS
                                # hier put a bracket order made by alpaca api
                                api.submit_order(
                                    symbol=symbol,
                                    qty=10,
                                    side='sell',
                                    type='market',
                                    time_in_force='day',
                                    order_class='bracket',
                                    stop_loss={'stop_price': sl},
                                    take_profit={'limit_price': tp})
                                print(f"new Order at {datetime.now()} places by {symbol}")
                                message.append(
                                    f"new Long Trade for {symbol} with price {curentC} , range of {barRange} , TP: {tp} and SL: {sl}\n\n")
                                # cursor.execute("delete from stock_strategy where stock_id=(select id from stock where symbol=?) ",(symbol,))
                                # connection.commit()
                            except Exception as e:
                                print(f"something is reeely schief gelaufen ! {e}")
                        else:
                            print(f"you already have on order in {symbol}")
            sendEmailNotification(message)


longBB()
shortBB()