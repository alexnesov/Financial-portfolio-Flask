# python -m Sandbox.get_signals


from utils.fetchData import fetchSignals
from datetime import datetime, timedelta
import pandas as pd
from utils.db_manage import std_db_acc_obj, QuRetType
db_acc_obj = std_db_acc_obj() 


average, items, spSTART, spEND, nSignals, dfSignals = fetchSignals(ALL=True)
today = datetime.now()



def filter_rows_by_delta(dataframe: pd.DataFrame, days_threshold: int = 6) -> pd.DataFrame:
    """
    Filter the rows of a DataFrame based on the difference between the "SignalDate" column and today's date.

    Parameters:
        dataframe (DataFrame): The input DataFrame with a column named "SignalDate" representing dates.
        days_threshold (int, optional): The minimum number of days the difference between "SignalDate" and today
                                        should be greater than. Defaults to 5.

    Returns:
        DataFrame: A new DataFrame containing only the rows where the difference between "SignalDate" and today
                   is greater than the specified threshold.

    Example:
        >>> data = {"SignalDate": ["2023-07-25", "2023-07-27", "2023-07-20", "2023-07-18", "2023-07-10"]}
        >>> df = pd.DataFrame(data)
        >>> filtered_df = filter_rows_by_delta(df, days_threshold=3)
        >>> print(filtered_df)
          SignalDate
        0 2023-07-25
        1 2023-07-27
        2 2023-07-20
        3 2023-07-18
    """

    # Convert "SignalDate" column to datetime type
    dataframe["SignalDate"] = pd.to_datetime(dataframe["SignalDate"])

    # Calculate the difference between "SignalDate" and today
    dataframe["Delta"] = today - dataframe["SignalDate"]

    # Convert the days_threshold to a timedelta
    threshold_timedelta = timedelta(days=days_threshold)

    # Filter rows where the delta is greater than the threshold
    filtered_df = dataframe[dataframe["Delta"] > threshold_timedelta].copy()

    # Drop the "Delta" column as it's no longer needed
    filtered_df.drop(columns=["Delta"], inplace=True)

    return filtered_df


class PriceProvider:

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


def get_price_at_Dx_plus(row: pd.Series, d:int):
    """
    For a given row and column, gets the price at d + something
    """
    pass




if __name__ == '__main__':
    df = filter_rows_by_delta(dfSignals)

    provider = PriceProvider()
    provider.get_price("MSFT", "2023-04-28")
    print(df)