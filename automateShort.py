import sqlite3
import alpaca_trade_api as tradeapi
import appConfig
from datetime import date,datetime
import pandas as pd
from  notification import sendEmailNotification
#from timeZone import is_dst


def autoTradeShort():
    api = tradeapi.REST(appConfig.apiKey, appConfig.secretKey, base_url=appConfig.baseUrl) # or use ENV Vars shown below
    clock=api.get_clock()
    #check if the markt is open
    if clock.is_open:
        connection=sqlite3.connect(appConfig.dbAdress)
        #change tuple to object to accsess them like dics
        connection.row_factory=sqlite3.Row
        cursor=connection.cursor()
        cursor.execute("select id from strategy where name= 'opening_range_breakdown'")
        shortStategyID =cursor.fetchone()[0]
        #check if the symbol is shortable
        cursor.execute("""select * from(select symbol,name,shortable from stock
         join stock_strategy on stock_strategy.stock_id=stock.id where stock_strategy.strategy_id=?) where shortable='1' """,(shortStategyID,))
        stock_on_strategy=cursor.fetchall()
        symbols=[symbol['symbol'] for symbol in stock_on_strategy ]
        if symbols:

            today=date.today().isoformat()
            EB = 'America/New_York'
            startTime = pd.Timestamp(f'{today} 09:30', tz=EB)
            endTime = pd.Timestamp(f'{today} 09:45', tz=EB)

            #check if i have already some orders to avoid multiple order on same symbol
            orders=api.list_orders(status='all',after=today)
            openOrders=api.list_orders(status='open')
            existing_order_symbols=[order.symbol for order in orders if order.status!='canceled' and order not in openOrders]
            message = []
            #if any symbol exists in a watchlist for a trading strategy
            for symbol in symbols:
                #if symbol
                #turn barset to data frame whith .df
                barsets = api.get_barset(symbol, '5Min', start=today).df

                # für jedes element von index wird die bedingung in klammern geprueft und wenn
                # false eine 0 und wenn true ein 1 auf jeder seite
                # am ende werde die erzeugte 0 und 1.er Reihen mit einander bitweise und verknuepft
                # damit die erzeugte liste beide bedingungen enthaelt
                opening_mask=(barsets.index>=startTime) & (barsets.index<endTime)
                #erzeugte maske als label bzw. index der panad-frame dataset mit loc
                opening=barsets.loc[opening_mask]
                opening_bar_high=opening[symbol]['high'].max()
                opening_bar_low=opening[symbol]['low'].min()

                if opening_bar_high!=opening_bar_low:
                    bar_range=opening_bar_high-opening_bar_low
                else:
                    bar_range=opening_bar_low*0.05

                #check if the current barset time is lower than first barset time for opening-break-down strategy
                after_opening_mask= barsets.index>=endTime
                after_opening_bars=barsets.loc[after_opening_mask]

                #check if a new bar is above the opening close
                after_opening_breakdown=after_opening_bars.loc[(after_opening_bars[symbol]['close']<opening_bar_low)]
                if not after_opening_breakdown.empty:
                    if symbol not in existing_order_symbols:
                        try:
                            #first bar in the list
                            limit=after_opening_breakdown.iloc[0][symbol]['close']
                            tp=limit-(bar_range*1.5)
                            sl=limit+bar_range
                            #hier put a bracket order made by alpaca api
                            api.submit_order(
                                symbol=symbol,
                                qty=10,
                                side='sell',
                                type='limit',
                                time_in_force='day',
                                order_class='bracket',
                                limit_price=limit,
                                stop_loss={'stop_price': sl},
                                take_profit={'limit_price': tp})
                            print(f"new Order places at {datetime.now()} by {symbol}")
                            message.append(f"new Short Trade  for {symbol} with price{limit} , range of {bar_range} , TP: {tp} and SL: {sl}\n\n")
                            cursor.execute("delete from stock_strategy where stock_id=(select id from stock where symbol=?) ",(symbol,))
                            connection.commit()
                        except Exception as e:
                            print(f"something is reeely schief gelaufen ! {e}")
                    else:
                        print(f"you already have on order in {symbol}")
            sendEmailNotification(message)

autoTradeShort()