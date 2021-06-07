import sqlite3

connection=sqlite3.connect('app.db')
#need to have a cursor in this connection to execute sql-cpmmand
cursor=connection.cursor()
cursor.execute(""" 
    create table if not exists stock(
            id integer primary key,
            symbol text not null unique,
            name text not null,
            exchange text not null,
            signal text,
            shortable boolean not null            
            )
""")
cursor.execute("""
    create table if not exists stock_price(
        id integer primary key,
        stock_id integer ,
        date not null,
        open not null,
        high not null ,
        low not null ,
        close not null,
        volume not null ,
        foreign key (stock_id) references stocks(id)
    )
""")

cursor.execute("""
    create table if not exists minit_stock_price(
        id integer primary key,
        stock_id integer ,
        minit_date not null,
        open not null,
        high not null ,
        low not null ,
        close not null,
        volume not null ,
        foreign key (stock_id) references stocks(id)
    )
""")
cursor.execute("""
    create table if not exists strategy(
        id integer primary key,
        name not null  )
""")

cursor.execute("""
    create table if not exists stock_strategy(
        stock_id integer not null,
        strategy_id integer not null,
        foreign key (stock_id) references stocks(id),
        foreign key (strategy_id) references strategy(id))
""")
strategies=['opening_range_breakout','opening_range_breakdown','Bollinger_Bands']
# for str in strategies:
#     cursor.execute("""
#     insert into strategy (name) values (?)
#     """,(str,))

cursor.execute("""
    create table if not exists filtered_stocks(
        stock_id integer not null,
        foreign key (stock_id) references stocks(id))
""")
cursor.execute("""
    create table if not exists indicator_stock(
        stock_id integer not null,
        sma_20  float,
        sma_50 float ,
        rsi_14 float,
        range boolean,
        foreign key (stock_id) references stocks(id))
""")

cursor.execute("""
    create table if not exists watchlist(
        stock_id integer not null,
        foreign key (stock_id) references stocks(id))
""")
# commit changes to db
connection.commit()
