
from helper import alpacaApi

#this function has to be execute 20 minits bevor market_closing
def closeAllPositions():
    api=alpacaApi()
    close=api.close_all_positions()
    print(close)

closeAllPositions()

print("all Positions are Closed!")