import pandas as pd
from utils.db_manage import std_db_acc_obj, QuRetType

import warnings

# Filter out the specific UserWarning related to pandas and SQLAlchemy
warnings.filterwarnings("ignore", category=UserWarning, module="pandas")


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

        res = db_acc_obj.exc_query(db_name='marketdata', query=qu, \
        retres=QuRetType.ALLASPD)

        print(res['Close'])


    def get_price_from_df(self, row: pd.Series):
        """
        """
        ticker = row["ValidTick"]
        date = row["Signaldate_plus_1"]

        SE = self.detect_stock_exchange(ticker)

        qu = f'SELECT * FROM marketdata.{SE}_20 Where Symbol = "{ticker}" and Date = "{date}"'

        res = db_acc_obj.exc_query(db_name='marketdata', query=qu, \
        retres=QuRetType.ALLASPD)

        return res['Close']

