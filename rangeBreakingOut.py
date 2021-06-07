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

# prosentage=3
# connection=sqlite3.connect(appConfig.dbAdress)
# connection.row_factory=sqlite3.Row
# #change tuple to object to accsess them like dics
# cursor=connection.cursor()
# #cursor.execute("select symbol from stock")
# #rows=cursor.fetchall()
# stocks=[]
# #symbols=[stock['symbol'] for stock in rows]
# #for i in range(0,len(symbols),100):
# #    currentSymbols=symbols[i:i+100]
#     #for symbol in currentSymbols:
# cursor.execute("select stock_id from filtered_stocks")
# stockIds=cursor.fetchall()
# # for id in stockIds:
# #     print(id['stock_id'])
#
def detectStockpriceRange(closes,procentage=3):
    #for id in stockIds:
    #cursor.execute("select close from stock_price where stock_id=? ", (id['stock_id'],))
    #df = cursor.fetchall()
    if (len(closes)) >= 16:
        #df = closes[-1:-16]
        #df = pd.DataFrame(df, columns=['close'])
        lasst3Weeks = closes[-16:-1]
        newdayClose = closes[-1]
        maxClose = lasst3Weeks.max()
        minClose = lasst3Weeks.min()
        pro = 1 - (procentage / 100)
        if minClose >= (maxClose * pro):
            if newdayClose>maxClose:
                return True
        return False


    # if not stocks:
    #     for stock_id in stocks:
    #         cursor.execute("insert into indicator_stock (range_breaking_out) values (True) where stock_id =?", (id,))
    #         print(f"prcessing {stock_id}")

#
# for id in stockIds:
#     cursor.execute("select close from stock_price where stock_id=? ",(id['stock_id'],))
#     df=cursor.fetchall()
#     if (len(df))>=16:
#         df=df[:16]
#         df=pd.DataFrame(df,columns=['close'])
#         lasst3Weeks=df.close[1:16].values
#         newdayClose=df.close[0:1].values
#         maxClose=lasst3Weeks.max()
#         minClose=lasst3Weeks.min()
#         pro=1-(prosentage/100)
#         if minClose >=(maxClose*pro):
#             if newdayClose > maxClose:
#                 stocks.append(id)
# cursor.execute("delete  from filtered_stocks")
# connection.commit()
#
# if not stocks:
#     for stock_id in stocks:
#         cursor.execute("insert into indicator_stock (range_breaking_out) values (True) where stock_id =?",(id,))
#         print(f"prcessing {stock_id}")
#
# print("finish")
#print(stocks)