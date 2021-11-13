
from pandas.core.reshape.merge import merge
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


def SignalDetection(df):
    """
    This function downloads prices for desired quotes (those in the parameter)
    and then tries to catch signals for selected timeframe.
    Stocks for which we catched a signal are stored in variable "validsymbol"

    :param p1: dataframe of eod data
    :returns: df with signals
    """

    close               = df["Close"].to_numpy()
    high                = df["High"].to_numpy()
    low                 = df["Low"].to_numpy()

    # Aroon
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



def getData(tick):
    """
    Pulling from remote RDS
    """

    if tick in NASDAQ_LIST:
        stockExchange = "NASDAQ"
    else:
        stockExchange = "NYSE"


    print(f'Getting tick data from RDS (stock exchange: {stockExchange}). . .')
    qu = f"SELECT * FROM {stockExchange}_20 WHERE Symbol = '{tick}'"
    df = db_acc_obj.exc_query(db_name='marketdata', query=qu,\
        retres=QuRetType.ALLASPD)

    return df



def getsp500(DateSP='2020-01-01'):
    """
    """
    qu                  = f"SELECT Date, Close FROM marketdata.sp500 where Date>='{DateSP}'"
    sp500df             = db_acc_obj.exc_query(db_name='marketdata', query=qu,\
        retres=QuRetType.ALLASPD)
    sp500df.Date        = pd.to_datetime(sp500df.Date)
    sp500df             = sp500df.rename(columns={'Close':'Close_sp'})

    return sp500df
    


def consolidateSignals(tick):
    """
    """

    #### SP500 data fetch + % evol 1D calculation"
    print('Getting SP500 data from RDS to build the benchmark comparison. . .')
    dfsp500                                = getsp500() # YYYY-MM-DD
    dfsp500['returnSP500_1D']              = dfsp500.Close_sp.pct_change()[1:]
    #### SP500 data fetch + % evol 1D calculation"

    initialDF                              = getData(tick)
    df_signals                             = SignalDetection(initialDF)
    df_signals[f'return_1D']               = df_signals.Close.pct_change()[1:] # YYYY-MM-DD
    df_signals.Date                        = pd.to_datetime(df_signals.Date)
    df_signals                             = pd.merge(df_signals, dfsp500, on='Date',how='inner')
    df_signals['diff_stock_bench']         = df_signals['return_1D'] - df_signals['returnSP500_1D']
    df_signals[f'rolling_mean_{35}']       = df_signals['diff_stock_bench'].rolling(35).mean()
    df_signals[f'rolling_mean_{10}']       = df_signals['diff_stock_bench'].rolling(10).mean()
    df_signals[f'rolling_mean_{5}']        = df_signals['diff_stock_bench'].rolling(5).mean()

    qu_gap = f"SELECT * FROM marketdata.Technicals WHERE Ticker='{tick}'"

    # print('Getting the technicals')

    """
    df_gap                              = db_acc_obj.exc_query(db_name  = 'marketdata', 
                                                               query    = qu_gap, 
                                                               retres   = QuRetType.ALLASPD)

    df_gap['Date']                      = df_gap['Date'].astype('datetime64[ns]')
    merged                              = df_signals.merge(df_gap[['Date','Gap']], on='Date', how='left')

    print(merged)
    """
    return df_signals


