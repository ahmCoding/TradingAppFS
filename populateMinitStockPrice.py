import sqlite3
#import alpaca_trade_api as tradeapi
import appConfig
import pandas as pd
from helper import *
#for financial modelling grupp
from urllib.request import urlopen
import json
from datetime import datetime,timedelta

# stratDate= -1 means that DB is empty and needs to be initialized

# EB = 'America/New_York'
# if startDate!=-1:
#     start=pd.Timestamp(startDate, tz=EB).isoformat()
#end=pd.Timestamp('2021-05-20', tz=EB).isoformat()
#1Min, 5Min, 15Min, day or 1D. minute is an alias of 1Min
timeF='5Min'
api = alpacaApi() # or use ENV Vars shown below
startDate=datetime(2020,12,1).date()
endDate=datetime(2021,6,4).date()
EB = 'America/New_York'

connection=sqlite3.connect(appConfig.dbAdress)
connection.row_factory=sqlite3.Row
cursor=connection.cursor()
cursor.execute("""select * from stock""")
rows=cursor.fetchall()

stockId={}
for row in rows:
    s=row['symbol']
    stockId[s]=row['id']

#load top 100 Nasdaq Companies
url = ("https://financialmodelingprep.com/api/v3/nasdaq_constituent?apikey=6898f075ced362a15d64a8b0e8a5833f")
response = urlopen(url)
data = response.read().decode("utf-8")
#parse json to dic
companies=json.loads(data)
#companies=['ABC']
for company_symbol in companies:
    company_symbol=company_symbol['symbol']
    startDate = datetime(2020, 12, 1).date()
    endDate = datetime(2021, 6, 4).date()
    while startDate<endDate:
        tmpStart=pd.Timestamp(startDate,tz=EB).isoformat()
        tmpEnd=pd.Timestamp(startDate+timedelta(days=4),tz=EB).isoformat()
        barsets = api.get_barset(company_symbol, timeF,limit=1000, start=tmpStart, end=tmpEnd).df
        # resample downloaded panda data frame with 5 min frequency and if any bar is missing ,fill it with last bar
        barsets=barsets.resample('5min').ffill()
        for index,bar in barsets.iterrows():
            #print(index)
            #print(bar[company_symbol]['close'])
            cursor.execute("insert into minit_stock_price (stock_id,minit_date,open,high,low,close,volume) values (?,?,?,?,?,?,?)",\
                           (stockId[company_symbol],index.tz_localize(None).isoformat(),bar[company_symbol]['open'],bar[company_symbol]['high'],\
                            bar[company_symbol]['low'],bar[company_symbol]['close'],bar[company_symbol]['volume']))
        startDate+=timedelta(days=7)
    print(f"processing {company_symbol} from {tmpStart} to {tmpEnd}")
    connection.commit()



# while startDate<endDate:
#
#     endWeek=startDate+timedelta(days=4)
#     print(startDate,endWeek)
#     startDate+=timedelta(days=7)





