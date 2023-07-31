import pandas as pd
from utils.db_manage import std_db_acc_obj, QuRetType
import numpy as np

db_acc_obj = std_db_acc_obj() 


class Prices:

    def __init__(self) -> None:
        self.NASDAQ_LIST     = pd.read_csv('utils/nasdaq_list.csv').iloc[:,0].tolist()
        self.NYSE_LIST       = pd.read_csv('utils/nyse_list.csv').iloc[:,0].tolist()


    def detect_stock_exchange(self, ticker: str):
        """
        """
        
        if ticker in self.NASDAQ_LIST:
            return "NASDAQ"
        elif ticker in self.NYSE_LIST:
            return "NYSE"
        else:
            print("Ticker not recognized. . . ")
            return "NA"


    def get_price(self, ticker: str, date: str):
        """
        "Date" format: YYYY-MM-DD
        """
        print(f"Getting price for {ticker}. . .")

        SE = self.detect_stock_exchange(ticker)

        print(f'Ticker is in: {SE}. . .')

        qu = f'SELECT * FROM marketdata.{SE}_20 Where Symbol = "{ticker}" and Date = "{date}"'

        res = db_acc_obj.exc_query(db_name='marketdata', 
                                   query=qu, 
                                   retres=QuRetType.ALLASPD)

        print(res['Close'])

    def quer_d_plus_1(self):

        one_day = pd.Timedelta(days=1)
        self.date = self.date + one_day

        qu = f'SELECT * FROM marketdata.{self.SE}_20 Where Symbol = "{self.ticker}" and Date = "{self.date}"'
        res = db_acc_obj.exc_query(db_name='marketdata', 
                                    query=qu,
                                    retres=QuRetType.ALLASPD)
        return res['Close']
        
               
    def get_price_from_df(self, row: pd.Series):
        """
        """
        print(row.to_dict())
        if (row['Sector'] == None):
            return np.nan
        else:
            self.ticker = row["ValidTick"]
            self.date = row["Signaldate_plus_1"]

            self.SE = self.detect_stock_exchange(self.ticker)

            qu = f'SELECT * FROM marketdata.{self.SE}_20 Where Symbol = "{self.ticker}" and Date = "{self.date}"'

            res = db_acc_obj.exc_query(db_name='marketdata', 
                                       query=qu,
                                       retres=QuRetType.ALLASPD)

            if res['Close'].empty:
                print(f"No Closing price for {self.ticker} for the date {self.date}. Certainly due to vacation day, advancing in time. . .")
                # If res empty means if there is vacation, we add one business day to get to the first business day. We consider that there
                # can't be more then 4 consecutive days of vacation days on the trading floor
                new_res = self.quer_d_plus_1()
                if new_res.empty:
                    new_res = self.quer_d_plus_1()
                    if new_res.empty:
                        return self.quer_d_plus_1()
                    else:
                        return new_res
                else:
                    return new_res
            else:
                return res['Close']

            

