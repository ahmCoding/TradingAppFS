#execute this script after execute populate prices
import sqlite3
import alpaca_trade_api as tradeapi
import appConfig
import numpy as np
import pandas as pd
import talib
from rangeBreakingOut import detectStockpriceRange

def indicatorsPrices():
    connection=sqlite3.connect(appConfig.dbAdress)
    connection.row_factory=sqlite3.Row
    cursor=connection.cursor()
    cursor.execute("""select * from stock""")
    rows=cursor.fetchall()
    symbols=[symbol['symbol'] for symbol in rows]

    for symbol in symbols:
        cursor.execute("""select close from stock_price join stock on 
        stock.id == stock_price.stock_id where symbol=?""",(symbol,))
        closes=cursor.fetchall()
        if (len(closes)>20):
            toCalc=np.array(closes[-20:])
            toCalc=np.reshape(toCalc,(1,20))[0]
            sma_20=talib.SMA(toCalc,timeperiod=20)[-1]
            cursor.execute("select id from stock where symbol=?",(symbol,))
            stock_id=cursor.fetchone()[0]
            #cursor.execute("insert into indicator_stock (stock_id,sma_20) values (?,?)",(stock_id,sma_20))
            #detect ranging of Price
            priceRanging=detectStockpriceRange(closes=toCalc,procentage=2.3)
            #cursor.execute("insert into indicator_stock (range) values (?) where stock_id=?", (priceRanging,stock_id))
            #insert sma and rang
            cursor.execute("insert into indicator_stock (stock_id,sma_20,range) values (?,?,?)",(stock_id,sma_20,priceRanging))

            if len(closes)>50:
                toCalc= np.array(closes[-51:-1])
                toCalc= np.reshape(toCalc, (1, 50))[0]
                sma_50 = talib.SMA(toCalc, timeperiod=50)[-1]
                rsi_14=np.reshape((np.array(closes)),(1,len(closes)))[0]
                rsi_14=talib.RSI(rsi_14,timeperiod=14)[-1]
                cursor.execute("update indicator_stock set sma_50=?,rsi_14=? where stock_id=?", (sma_50,rsi_14,stock_id))
        connection.commit()
        print(f"processing {symbol}")

        #sma_20=talib.SMA(closes,timeperiod=20)
        #print(sma_20)
# connection.commit()
#
# setupForDB()

#jon the tables to check the correcnes of function
# sqlite> select symbol,name,date,open,close from stock_price join stocks on stocks.id=stock_price.stock_id where symbol='AAPL' order by date;

indicatorsPrices()
