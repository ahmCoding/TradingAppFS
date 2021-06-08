import sqlite3
import appConfig

connection=sqlite3.connect(appConfig.dbAdress)
cursor=connection.cursor()
cursor.execute("""Drop table stock """)
cursor.execute("""Drop Table stock_price """)
cursor.execute("""Drop Table strategy """)
cursor.execute("""Drop Table stock_strategy """)
cursor.execute("""Drop Table filtered_stocks """)
cursor.execute("""Drop Table indicator_stock""")
cursor.execute("Drop table watchlist")
cursor.execute("Drop table minit_stock_price")




connection.commit()
