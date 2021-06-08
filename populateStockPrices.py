import sqlite3
#import alpaca_trade_api as tradeapi
import appConfig
import pandas as pd
from helper import *

# stratDate= -1 means that DB is empty and needs to be initialized
def setupForDB(startDate,endDate,dbInit:bool=False):
    # EB = 'America/New_York'
    # if startDate!=-1:
    #     start=pd.Timestamp(startDate, tz=EB).isoformat()
    #end=pd.Timestamp('2021-05-20', tz=EB).isoformat()
    #1Min, 5Min, 15Min, day or 1D. minute is an alias of 1Min
    timeF='1D'
    api = alpacaApi() # or use ENV Vars shown below
    #assets = api.list_assets()
    connection=sqlite3.connect(appConfig.dbAdress)
    connection.row_factory=sqlite3.Row
    cursor=connection.cursor()
    cursor.execute("""select * from stock""")
    rows=cursor.fetchall()
    #rows=cursor.fetchall()
    #rows=rows[1:3]

    stockId={}
    for row in rows:
        s=row['symbol']
        stockId[s]=row['id']
    keys=list(stockId.keys())

    for i in range(0,len(stockId),200):
        currentSymbols=keys[i:i+200]
        #barsets=api.get_barset(currentSymbols, timeF, start=start, end=end)
        # if startDate!=-1:
        #     barsets=api.get_barset(currentSymbols, timeF,start=start)
        # else:
        #     barsets=api.get_barset(currentSymbols, timeF)
        barsets = api.get_barset(currentSymbols, timeF,start=startDate,end=endDate)

        for symbol in barsets:
            for bar in barsets[symbol]:
                if not dbInit:
                    cursor.execute("select date from stock_price where stock_id=?",(stockId[symbol],))
                    dates=cursor.fetchall()
                    # check if the date is already in table
                    date = pd.DataFrame(dates, columns=['date'])
                    if bar.t.date() not in date.date.values:
                        cursor.execute(" insert into stock_price (stock_id,date,open,high,low,close,volume) values(?,?,?,?,?,?,?)",
                                    (stockId[symbol],bar.t.date(),bar.o,bar.h,bar.l,bar.c,bar.v))
                else:
                    cursor.execute(" insert into stock_price (stock_id,date,open,high,low,close,volume) values(?,?,?,?,?,?,?)",
                        (stockId[symbol], bar.t.date(), bar.o, bar.h, bar.l, bar.c, bar.v))

            print(f"symbol {symbol} procced!")
        connection.commit()


def keep_db_clean():
    connection = sqlite3.connect(appConfig.dbAdress)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("""select id from stock """)
    rows = cursor.fetchall()
    for r in rows:
        cursor.execute("select count(*) from stock_price where stock_id=?", (r['id'],))
        anzahlTage = cursor.fetchone()[0]
    # keep db just for 60 days
        if anzahlTage > 60:
            rowToDelete=anzahlTage-60
            cursor.execute("delete from stock_price where date in "
                           "(select date from stock_price where stock_id=? order by date limit (?)) and stock_id =?",(r['id'],rowToDelete,r['id']))
            print(f"cleaning stock {r['id']} {rowToDelete} rows!")
    connection.commit()



# for i in range(0,len(stockId),200):
    #     currentSymbols=keys[i:i+200]
    #     #barsets=api.get_barset(currentSymbols, timeF, start=start, end=end)
    #     for symbol in barsets:
    #         for bar in barsets[symbol]:
    #         cursor.execute("select count(*) from stock_price where stock_id=?", (stockId[symbol]))
    # anzahlTage = cursor.fetchone()[0]
    # # keep db just for 60 days
    # while anzahlTage > 60:
    #     cursor.execute("delete from stock_price where date=( select min(date) from stock_price) and stock_id=?",
    #                    (stockId[symbol]))
    # connection.commit()

# EB = 'America/New_York'
# t=endT=pd.Timestamp('2021-03-01', tz=EB).isoformat()

#start,end=calcDate(daysAgo=65)
#setupForDB(startDate=start,endDate=end,dbInit=True)
keep_db_clean()

#jon the tables to check the correcnes of function
# sqlite> select symbol,name,date,open,close from stock_price join stocks on stocks.id=stock_price.stock_id where symbol='AAPL' order by date;

