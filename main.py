from fastapi import FastAPI,Request,Form
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")
import alpaca_trade_api as tradeapi
import appConfig
import sqlite3
from datetime import date
from fastapi.responses import RedirectResponse
import talib
from patterns import patterns
import numpy as np
import  pandas as pd



app=FastAPI()
@app.get("/")
def index(request:Request):
    #ToDo: check the date of today and if it is a weekeend turn it to a friday to get good result
    # get new date
    #today='2021-05-13'
    #weekday=date.today().weekday()
    #if weekday==6:
    filterValues={"":"All stock ","intraday_highest_close":" new highest Close ",
                  "intraday_lowest_close":" new lowest Close","intraday_lowest_open":" new lowest Open",
                  "cross_sma_20":"Cross Over SMA 20","cross_sma_50":"cross Over SMA 50",
                  "cross_under_sma_20":"Cross Under SMA 20","cross_under_sma_50":"Cross Under SMA 50",
                  "rsi_overbought":"RSI Over Bought","rsi_oversold":"RSI Over Sold","breaking_range":"breaking_Range"}
    #filterValues['new_intraday_close']=""
    currentFilter=request.query_params.get("filter",False)
    candlestickPattern=request.query_params.get("candlestickPattern",False)
    #api = tradeapi.REST(appConfig.apiKey, appConfig.secretKey, base_url=appConfig.baseUrl)
    #assets = api.list_assets()
    connection=sqlite3.connect(appConfig.dbAdress)
    connection.row_factory=sqlite3.Row
    #change tuple to object to accsess them like dics
    cursor=connection.cursor()

    # get the latest date of in DB saved bars for "AAA"-symbol
    # cursor.execute("""select date from (select symbol,date from stock_price
    #    join stocks on stocks.id =stock_price.stock_id order by date desc) where symbol="AAA" """)
    # latestDateInDBdbDate = cursor.fetchone()[0]
    #filter date on new high and low ranges
    if currentFilter:
        if currentFilter=='intraday_highest_close':
            cursor.execute("""select * from(select stock.id,symbol,name,signal,stock_id,date,max(close) from stock_price
             join stock on stock.id=stock_price.stock_id group by stock_id order by symbol)
             where date= (select max(date) from stock_price )""")
        elif currentFilter=='intraday_lowest_close':
            cursor.execute("""select * from(select stock.id,symbol,name,signal,stock_id,date,min(low) from stock_price join stock on stock.id=stock_price.stock_id group by stock_id order by symbol)
             where date=(select max(date) from stock_price )""")
        elif currentFilter=='intraday_lowest_open':
            cursor.execute("""select * from(select stock.id,symbol,name,signal,stock_id,date,min(open) from stock_price
             join stock on stock.id=stock_price.stock_id group by stock_id order by symbol)
             where date=(select max(date) from stock_price )""")
        elif currentFilter=='cross_sma_20':
            cursor.execute("""select id,symbol,name,signal from stock inner join (select stock_price.stock_id from stock_price join indicator_stock on
            indicator_stock.stock_id=stock_price.stock_id where close > sma_20 and date =(select max(date) from stock_price)) i
            on i.stock_id= stock.id""")
        elif currentFilter == 'cross_sma_50':
            cursor.execute("""select id,symbol, name,signal from stock inner join (select stock_price.stock_id from stock_price join indicator_stock on
            indicator_stock.stock_id=stock_price.stock_id where close > sma_50 and date =(select max(date) from stock_price)) i
            on i.stock_id= stock.id """)
        elif currentFilter == 'cross_under_sma_20':
            cursor.execute("""select id,symbol, name,signal from stock inner join (select stock_price.stock_id from stock_price join indicator_stock on
            indicator_stock.stock_id=stock_price.stock_id where close < sma_20 and date =(select max(date) from stock_price)) i
            on i.stock_id= stock.id """)
        elif currentFilter == 'cross_under_sma_50':
            cursor.execute("""select id,symbol,name,signal from stock inner join (select stock_price.stock_id from stock_price join indicator_stock on
            indicator_stock.stock_id=stock_price.stock_id where close < sma_50 and date =(select max(date) from stock_price)) i
            on i.stock_id= stock.id """)
        elif currentFilter == 'rsi_overbought':
            cursor.execute("""select id,symbol,name,signal from stock inner join (select stock_price.stock_id from stock_price join indicator_stock on
            indicator_stock.stock_id=stock_price.stock_id where rsi_14 >= 75  and date =(select max(date) from stock_price)) i
            on i.stock_id= stock.id """)
        elif currentFilter == 'rsi_oversold':
            cursor.execute("""select id,symbol,name,signal from stock inner join (select stock_price.stock_id from stock_price join indicator_stock on
            indicator_stock.stock_id=stock_price.stock_id where rsi_14 <= 25  and date =(select max(date) from stock_price)) i
            on i.stock_id= stock.id """)
        elif currentFilter =='breaking_range':
            cursor.execute("""select id,symbol,name,signal from stock join indicator_stock on indicator_stock.stock_id=stock.id where indicator_stock.range=True """)
        #elif currentFilter == 'range_break_out':


    else:
        cursor.execute("""select symbol,name,signal from stock order by symbol""")
    rows=cursor.fetchall()
    #print(f"currentFilter {currentFilter } & candleStickFilter {candlestickPattern}")

    ####this part is for candle stick filter at index page
    #save the filtered stocks to execute some candlestick filters on they
    # if currentFilter:
    #     for row in rows:
    #         #print(row['id'])
    #         cursor.execute("insert into filtered_stocks (stock_id) values (?)",(row['id'],))
    #     connection.commit()

    # if candlestickPattern:
    #     # get a handle to the function , which is select in webpage
    #     # the name of function is in pattern variable
    #     # like talib.pattern  and  pattern is the string name of function
    #     talibFunc = getattr(talib, candlestickPattern)
    #
    #     # cursor.execute("""select filtered_stocks.stock_id,open,high,low,close from filtered_stocks
    #      # join stock_price on stock_price.stock_id=filtered_stocks.stock_id """)
    #      # fRows=cursor.fetchall()
    #
    #      #get stock_
    #     cursor.execute("""select * from filtered_stocks""")
    #     fs=cursor.fetchall()
    #     for row in fs:
    #          priceRow=pd.read_sql_query("""select stock_id,open,high,low,close from stock_price where stock_id=?""",connection,params=(row['stock_id'],))
    #          res = talibFunc(priceRow['open'], priceRow['high'], priceRow['low'], priceRow['close'])
    #         # tail returns the last n rows of data set.
    #         # select a part of result for possible trades in future because the passt possible trades are gone
    #         # make it works with pandas.trail(n) n ist the last rows of data frame
    #          symbol_signal=''
    #          last = res.tail(1).values[0]
    #          #print(last)
    #          if last > 0:
    #              symbol_signal = 'bullish'
    #          elif last < 0:
    #              symbol_signal= 'bearish'
    #          else:
    #              symbol_signal =None
    #          if symbol_signal is not None:
    #              cursor.execute(""" update stock set poi8765432324156789 = ? where id=? """,(symbol_signal,row['stock_id']))
    #     connection.commit()
    #
    #     cursor.execute("""select symbol, name,signal from stock where signal is not ?""",(None,))
    #     rows=cursor.fetchall()
    #     #delete the temporery list of stocks after execute candle stick filter
    #     cursor.execute("delete  from filtered_stocks")
    #     connection.commit()
    return templates.TemplateResponse("index.html", {"request": request,"stocks":rows,"filterValues":filterValues})


@app.get("/stock/{symbol}")
def stockDetail(request:Request,symbol):
    connection=sqlite3.connect(appConfig.dbAdress)
    connection.row_factory=sqlite3.Row
    #change tuple to object to accsess them like dics
    cursor=connection.cursor()
    cursor.execute("select * from strategy")
    strategies=cursor.fetchall()

    cursor.execute("""select * from stock where symbol=?""",(symbol,))
    row=cursor.fetchone()
    cursor.execute("""select * from stock_price where stock_id=? order by date desc""",(row['id'],))
    prices=cursor.fetchall()
    return templates.TemplateResponse("stockDetail.html", {"request": request,"stock":row,"bars":prices,"strategies":strategies})


@app.post("/apply_strategy")
def apply_strategy(strategy_id:int=Form(...),stock_id:int=Form(...)):
    connection = sqlite3.connect(appConfig.dbAdress)
    connection.row_factory = sqlite3.Row
    # change tuple to object to accsess them like dics
    cursor = connection.cursor()
    cursor.execute(" insert into stock_strategy (stock_id,strategy_id) values (?,?)",(stock_id,strategy_id))
    connection.commit()
    #send status code 303: redirect status response code indicates that
    # redirects don't link to the newly uploaded resources, but to another page (such as a confirmation page or an upload progress page).
    # This response code is usually sent back as a result of PUT or POST. The method used to display this redirected page is always
    return RedirectResponse(url=f"/stock_strategy/{strategy_id}",status_code=303)

@app.get("/stock_strategy/{strategy_id}")
def stockDetail(request: Request,strategy_id):
    connection = sqlite3.connect(appConfig.dbAdress)
    connection.row_factory = sqlite3.Row
    # change tuple to object to accsess them like dics
    cursor = connection.cursor()

    cursor.execute("select name from strategy where id =?",(strategy_id,))
    strategy=cursor.fetchone()

    cursor.execute("""select symbol,name,id from stock
    join stock_strategy on stock_strategy.stock_id=stock.id where stock_strategy.strategy_id= ?""",(strategy_id,))
    stocks=cursor.fetchall()
    return templates.TemplateResponse("stock_strategy.html", {"request": request,"stocks":stocks,"strategy":strategy})


@app.get("/strategies")
def allStrategies(request: Request):
    connection = sqlite3.connect(appConfig.dbAdress)
    connection.row_factory = sqlite3.Row
    # change tuple to object to accsess them like dics
    cursor = connection.cursor()
    cursor.execute("select * from strategy")
    strategies = cursor.fetchall()
    return templates.TemplateResponse("strategies.html", {"request": request,"strategies":strategies})

@app.get("/trades")
def allStrategies(request: Request):

    api = tradeapi.REST(appConfig.apiKey, appConfig.secretKey,base_url=appConfig.baseUrl)  # or use ENV Vars shown below

    today = date.today().isoformat()
    EB = 'America/New_York'
    startTime = pd.Timestamp(f'{today} 09:30', tz=EB)
    endTime = pd.Timestamp(f'{today} 09:45', tz=EB)

    # check if i have already some orders to avoid multiple order on same symbol
    orders = api.list_orders(status='all')
    existing_order = [order for order in orders if order.status != 'canceled']

    return templates.TemplateResponse("trades.html", {"request": request,"orders":existing_order})


@app.post("/apply_to_watchlist")
def apply_strategy(stock_id:int=Form(...)):
    connection = sqlite3.connect(appConfig.dbAdress)
    connection.row_factory = sqlite3.Row
    # change tuple to object to accsess them like dics
    cursor = connection.cursor()
    cursor.execute(" insert into watchlist (stock_id) values (?)",(stock_id,))
    connection.commit()
    #send status code 303: redirect status response code indicates that
    # redirects don't link to the newly uploaded resources, but to another page (such as a confirmation page or an upload progress page).
    # This response code is usually sent back as a result of PUT or POST. The method used to display this redirected page is always
    return RedirectResponse(url=f"/watchlist",status_code=303)


@app.get("/watchlist")
def watchList(request:Request):
    candlestickPattern=request.query_params.get("candlestickPattern",False)
    print(candlestickPattern)
    connection=sqlite3.connect(appConfig.dbAdress)
    connection.row_factory=sqlite3.Row
    #change tuple to object to accsess them like dics
    cursor=connection.cursor()
    cursor.execute("""select symbol,name,signal from stock join watchlist on watchlist.stock_id=stock.id order by symbol""")
    stocks=cursor.fetchall()

    if candlestickPattern:
        # get a handle to the function , which is select in webpage
        # the name of function is in pattern variable
        # like talib.pattern  and  pattern is the string name of function
        talibFunc = getattr(talib, candlestickPattern)
        cursor.execute("""select * from watchlist""")
        fs=cursor.fetchall()
        for row in fs:
             priceRow=pd.read_sql_query("""select stock_id,open,high,low,close from stock_price where stock_id=?""",connection,params=(row['stock_id'],))
             res = talibFunc(priceRow['open'], priceRow['high'], priceRow['low'], priceRow['close'])
            # tail returns the last n rows of data set.
            # select a part of result for possible trades in future because the passt possible trades are gone
            # make it works with pandas.trail(n) n ist the last rows of data frame
             symbol_signal=''
             last = res.tail(1).values[0]
             #print(last)
             if last > 0:
                 symbol_signal = 'bullish'
             elif last < 0:
                 symbol_signal= 'bearish'
             else:
                 symbol_signal =None
             if symbol_signal is not None:
                 cursor.execute(""" update stock set signal = ? where id=? """,(symbol_signal,row['stock_id']))
        connection.commit()

        cursor.execute("select symbol,name,signal from stock join watchlist on watchlist.stock_id=stock.id order by symbol")
        stocks=cursor.fetchall()

    return templates.TemplateResponse("watchlist.html", {"request": request,"stocks":stocks ,"candlestickPatterns":patterns})


#uvicorn main:app --reload