import sqlite3
import alpaca_trade_api as tradeapi
import appConfig
from datetime import date,datetime
import pandas as pd

api = tradeapi.REST(appConfig.apiKey, appConfig.secretKey, base_url=appConfig.baseUrl)
print(api.get_account())