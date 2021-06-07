import sqlite3
import alpaca_trade_api as tradeapi
import appConfig
api = tradeapi.REST(appConfig.apiKey, appConfig.secretKey, base_url=appConfig.baseUrl) # or use ENV Vars shown below
assets = api.list_assets()
connection=sqlite3.connect(appConfig.dbAdress)
#change tuple to object to accsess them like dics
connection.row_factory=sqlite3.Row
cursor=connection.cursor()


for asset in assets:
    try:
        if asset.status=='active' and asset.tradable:
            cursor.execute(" insert into stock (symbol,name,exchange,shortable) values(?,?,?,?)",(asset.symbol,asset.name,asset.exchange,asset.shortable))
    except Exception  as e:
        print(e)
        print(asset.symbol)
connection.commit()
connection.close()