import appConfig
import pandas, sqlite3
from datetime import date, datetime, time, timedelta
import backtrader as bt

class bollingerBands(bt.Strategy):
    params = (('period', 20),)

    def __init__(self):
        self.dataclose = self.datas[0].close
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.redline = None
        self.blueline = None

        # Add a BBand indicator
        self.bband = bt.indicators.BBands(self.datas[0], period=self.params.period)


    def log(self, txt, dt=None):
        if dt is None:
            dt = self.datas[0].datetime.datetime()
        print('%s, %s' % (dt, txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        if order.status in [order.Completed]:
            order_details = f"{order.executed.price}, Cost: {order.executed.value}, Comm {order.executed.comm}"

            if order.isbuy():
                self.log(f"BUY EXECUTED, Price: {order_details}")
            else:  # Sell
                self.log(f"SELL EXECUTED, Price: {order_details}")

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def next(self):
        if self.bband.lines.bot:
            current_bar = self.datas[0]
            previous_bar = self.datas[-1]
            cbBarish= True if current_bar.close<current_bar.open else False
            #pbBeatish= True if previous_bar.close<previous_bar.open  else False

            if self.bband.lines.top < previous_bar.close and self.bband.top > current_bar.close and cbBarish and not self.position:
                self.order=self.sell()
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.redline=True

            elif self.bband.lines.bot < previous_bar.close and self.bband.bot < current_bar.close and not cbBarish and not self.position:
                self.order = self.buy()
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.blueline=True


            elif self.position:
                if self.redline and self.dataclose <self.bband.mid:
                    self.close()
                    self.log('Close Sell at Price  %.2f' % self.dataclose[0])
                elif self.blueline and self.dataclose>self.bband.mid:
                    self.close()
                    self.log('Close Buy at Price  %.2f' % self.dataclose[0])

    def stop(self):
        self.log('(Num Opening Bars %2d) Ending Value %.2f' %
                 (self.params.period, self.broker.getvalue()))

        if self.broker.getvalue() > 130000:
            self.log("*** BIG WINNER ***")

        if self.broker.getvalue() < 70000:
            self.log("*** MAJOR LOSER ***")


if __name__ == '__main__':
    conn = sqlite3.connect(appConfig.dbAdress)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT(stock_id) as stock_id FROM minit_stock_price
    """)
    stocks = cursor.fetchall()
    for stock in stocks:
        print(f"== Testing {stock['stock_id']} ==")

        cerebro = bt.Cerebro()
        cerebro.broker.setcash(100000.0)
        cerebro.addsizer(bt.sizers.PercentSizer, percents=95)

        dataframe = pandas.read_sql("""
            select minit_date, open, high, low, close, volume
            from minit_stock_price
            where stock_id = :stock_id
            and strftime('%H:%M:%S', minit_date) >= '09:30:00' 
            and strftime('%H:%M:%S', minit_date) < '16:00:00'
            order by minit_date asc
        """, conn, params={"stock_id": stock['stock_id']}, index_col='minit_date', parse_dates=['minit_date'])

        data = bt.feeds.PandasData(dataname=dataframe)

        cerebro.adddata(data)
        cerebro.addstrategy(bollingerBands)

        # strats = cerebro.optstrategy(OpeningRangeBreakout, num_opening_bars=[15, 30, 60])

        cerebro.run()
        # cerebro.plot()