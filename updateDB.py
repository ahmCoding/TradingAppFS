import sqlite3
import alpaca_trade_api as tradeapi
import appConfig
from datetime import date
from datetime import datetime
from populateStockPrices import setupForDB
from  populateStockPrices import keep_db_clean

def updateExistingstock():
    #api = tradeapi.REST(appConfig.apiKey, appConfig.secretKey, base_url=appConfig.baseUrl) # or use ENV Vars shown below
    connection = sqlite3.connect(appConfig.dbAdress)
    #connection.row_factory = sqlite3.Row
    # change tuple to object to accsess them like dics
    cursor = connection.cursor()
    cursor.execute( """select date from (select symbol,date from stock_price 
    join stock on stock.id =stock_price.stock_id order by date desc) where symbol="ABC" """)
    dbDate=cursor.fetchone()[0]
    cursor.close()
    today=date.today().isoformat()
    weekD=date.today().weekday()

    tNow = datetime.now()
    #!!!
    tTUpdate = tNow.replace(hour=22, minute=00, second=0, microsecond=0)
    #if today is not saturday or sunday
    if weekD != 6 and weekD!= 0 :
        #if db is alerady out of date and markt ist close
        #!!!
        if today!=dbDate and tNow > tTUpdate:
        #if today != dbDate :
            print("updating DB")
            setupForDB(startDate=dbDate,endDate=today)

def checkForNewstock():
    api = tradeapi.REST(appConfig.apiKey, appConfig.secretKey, base_url=appConfig.baseUrl) # or use ENV Vars shown below
    assets = api.list_assets()
    connection=sqlite3.connect(appConfig.dbAdress)
    connection.row_factory=sqlite3.Row
    #change tuple to object to accsess them like dics
    cursor=connection.cursor()
    cursor.execute("""select symbol,name from stock""")
    rows=cursor.fetchall()
    #list of symbols
    symbols=[row['symbol'] for row in rows]
    for asset in assets:
        try:
            if asset.status=='active' and asset.tradable and asset.symbol not in symbols:
                print(f"add new symbol {asset.symbol}, {asset.name}")
                cursor.execute(" insert into stock (symbol,name,exchange,shortable) values(?,?,?,?)",(asset.symbol,asset.name,asset.exchange,asset.shortable))
        except Exception as e:
           print(e)
           print(asset.symbol)
    connection.commit()
    connection.close()
#ToDO may be check if the existing stocks are still tradeable
def checkStcokDetals():
    pass

updateExistingstock()
checkForNewstock()
keep_db_clean()

