
from utils.db_manage import QuRetType, std_db_acc_obj
from signals_lib.ta import aroon, rsi

import sys
import pandas as pd
from datetime import datetime, timedelta 
from time import strftime
import numpy as np

sys.stdout.flush()
pd.options.mode.chained_assignment  = None 
db_acc_obj                          = std_db_acc_obj() 


#today = str(datetime.today().strftime('%Y-%m-%d'))
today       = datetime.today()
today_str   = today.strftime('%Y-%m-%d')

now         = strftime("%H:%M:%S")
now         = now.replace(":","-")

# PARAMETERS
Aroonval        = 40
short_window    = 10
long_window     = 50
timePeriodRSI   = 14

# start_date and end_date are used to set the time interval that in which a signal is going to be searched
start_date      = today - timedelta(days=20)
end_date        = f'{today}'


NASDAQ_LIST     = pd.read_csv('utils/nasdaq_list.csv').iloc[:,0].tolist()
NYSE_LIST       = pd.read_csv('utils/nyse_list.csv').iloc[:,0].tolist()


def SignalDetection(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function downloads prices for desired quotes (those in the parameter)
    and then tries to catch signals for selected timeframe.
    Stocks for which we catched a signal are stored in variable "validsymbol"

    :param p1: dataframe of eod data
    :returns: df with signals
    """

    # Aroon
    print("Raw df: ")
    df.sort_values(by='Date', inplace=True)
    print(df)

    aroonUP, aroonDOWN = aroon(df, Aroonval)
    
    # RSI
    ind_rsi             = rsi(df, timePeriodRSI)

    df['RSI']           = ind_rsi
    df['Aroon Down']    = aroonDOWN
    df['Aroon Up']      = aroonUP
    df['signal']        = pd.Series(np.zeros(len(df)))
    df['signal_aroon']  = pd.Series(np.zeros(len(df)))
    df                  = df.reset_index()
    # Moving averages
    df['short_mavg']    = df['Close'].rolling(window=short_window, min_periods=1, center=False).mean()
    df['long_mavg']     = df['Close'].rolling(window=long_window, min_periods=1, center=False).mean()

    # When 'Aroon Up' crosses 'Aroon Down' from below
    df["signal"][short_window:]         = np.where(df['short_mavg'][short_window:] > df['long_mavg'][short_window:], 1,0)
    df["signal_aroon"][short_window:]   = np.where(df['Aroon Down'][short_window:] < df['Aroon Up'][short_window:], 1,0)

    df['positions']                     = df['signal'].diff()
    df['positions_aroon']               = df['signal_aroon'].diff()
    df['positions_aroon'].value_counts()

    # Trend reversal detection
    # Aroon alone doesn't give us enough information.
    # Too many false signals are given
    # We blend moving averages crossing strategy
    df['doubleSignal'] = np.where(
        (df["Aroon Up"] > df["Aroon Down"]) & (df['positions']==1) & (df["Aroon Down"]<75) &(df["Aroon Up"]>55),
        1,0)

    return df



def getData(tick: str) -> pd.DataFrame:
    """
    Retrieves data for a specific stock ticker from a remote RDS.
    :param tick: Stock ticker symbol.
    :return: A DataFrame containing the stock data.
    """

    if tick in NASDAQ_LIST:
        stockExchange = "NASDAQ"
    else:
        stockExchange = "NYSE"


    print(f'==> :INFO: Getting tick data from RDS (stock exchange: {stockExchange}). . .')
    qu = f"SELECT * FROM {stockExchange}_20 WHERE Symbol = '{tick}'"
    df = db_acc_obj.exc_query(db_name   = 'marketdata', 
                              query     = qu,\
                              retres    = QuRetType.ALLASPD)

    return df



def getsp500(DateSP='2020-01-01') -> pd.DataFrame:
    """
    Retrieves SP500 data from a specified date onwards and returns it as a DataFrame.
    :param DateSP: Start date for retrieving SP500 data (default: '2020-01-01').
    :return: A DataFrame containing SP500 data.
    """
    qu                  = f"SELECT Date, Close FROM marketdata.sp500 where Date>='{DateSP}'"
    sp500df             = db_acc_obj.exc_query(db_name  = 'marketdata', 
                                               query    = qu,\
                                               retres   = QuRetType.ALLASPD)

    sp500df.Date        = pd.to_datetime(sp500df.Date)
    sp500df             = sp500df.sort_values(by='Date', ascending=True)
    sp500df             = sp500df.rename(columns={'Close':'Close_sp'})

    return sp500df
    

def consolidateSignals(tick: str) -> pd.DataFrame:
    """
    Consolidates signals dataframe for a given stock ticker by fetching SP500 data, calculating percentage evolution,
    and merging it with the stock data.
    :param tick: Stock ticker symbol.
    :return: DataFrame containing consolidated signals.
    """

    #### SP500 data fetch + % evol 1D calculation"
    print('==> :INFO: Getting SP500 data from RDS to build the benchmark comparison. . .')
    dfsp500                             = getsp500() # YYYY-MM-DD

    print(":INFO: dfsp500 from consolidateSignals(): ")
    print(dfsp500)
    dfsp500['returnSP500_1D']           = dfsp500.Close_sp.pct_change()[1:]
    #### SP500 data fetch + % evol 1D calculation"

    initialDF                           = getData(tick)

    print('==> :INFO: initialDF: ')
    print(initialDF)

    dfStock                             = SignalDetection(initialDF)
    dfStock[f'return_1D']               = dfStock.Close.pct_change()[1:] # YYYY-MM-DD
    print("dfStock: ")
    print(dfStock)
    dfStock.Date                        = pd.to_datetime(dfStock.Date)
    print("dfStock.Date: ")
    print(dfStock.Date)
    dfStock                             = pd.merge(dfStock, dfsp500, on='Date',how='inner')
    dfStock['diff_stock_bench']         = dfStock['return_1D'] - dfStock['returnSP500_1D']
    dfStock[f'rolling_mean_{35}']       = dfStock['diff_stock_bench'].rolling(35).mean()
    dfStock[f'rolling_mean_{10}']       = dfStock['diff_stock_bench'].rolling(10).mean()
    dfStock[f'rolling_mean_{5}']        = dfStock['diff_stock_bench'].rolling(5).mean()

    return dfStock


if __name__ == '__main__':
    pass