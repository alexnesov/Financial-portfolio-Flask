import pandas as pd
import os, sys
import plotly.express as px

PROJECT_ROOT = os.path.abspath(os.path.join(
               os.path.dirname(__file__),
               os.pardir))

sys.path.append(PROJECT_ROOT)

from utils.db_manage import QuRetType, dfToRDS, std_db_acc_obj

# rolling periof for time series smoothening
NB_SMOOTHEN = 7


Sectors = ['Healthcare', 
            'Basic Materials', 
            'Industrials', 
            'Consumer Cyclical', 
            'Real Estate', 
            'Financial',
            'Consumer Defensive',
            'Technology',
            'Utilities',
            'Communication Services',
            'Energy']



def get_historical_stock_prices(stock_exchange: str) -> pd.DataFrame:
    """
    :param stock_exchange: ex: "NASDAQ"
    """
    qu_historical_prices        = f"SELECT Symbol, Date, Close \
                                FROM marketdata.{stock_exchange}_20"

    df_hist_prices              = db_acc_obj.exc_query(db_name     = 'marketdata', 
                                                       query       = qu_historical_prices,
                                                       retres      = QuRetType.ALLASPD)

    return df_hist_prices


def get_sectors_info() -> pd.DataFrame:
    """
    """
    qu_sectors                  = "SELECT * FROM marketdata.sectors"

    df_sectors                  = db_acc_obj.exc_query(db_name     = 'marketdata', 
                                                       query       = qu_sectors,
                                                       retres      = QuRetType.ALLASPD)
    
    return df_sectors


def enrich_sect_info(df_hist_prices: pd.DataFrame, df_sectors: pd.DataFrame) -> pd.DataFrame: 
    """
    Enriching with sector information
    
    Not doing enrichment withing SQL RDS database because ram is very low (to lower cost), whereas way stronger on personnal
    computer and on AWS EC2. Therefore doing more complex ops on VM.
    :returns: (Example)
            Symbol        Date  Close                     Company      Sector                Industry\
    0            A  2020-01-01  85.31  Agilent Technologies, Inc.  Healthcare  Diagnostics & Research\
    1            A  2020-01-02  85.95  Agilent Technologies, Inc.  Healthcare  Diagnostics & Research\
    2            A  2020-01-03  84.57  Agilent Technologies, Inc.  Healthcare  Diagnostics & Research\
    3            A  2020-01-06  84.82  Agilent Technologies, Inc.  Healthcare  Diagnostics & Research\
    4            A  2020-01-07  85.08  Agilent Technologies, Inc.  Healthcare  Diagnostics & Research\
    1336487    NXE  2022-04-25   5.02          NexGen Energy Ltd.      Energy                 Uranium\
    1336488    NXE  2022-04-26   4.99          NexGen Energy Ltd.      Energy                 Uranium\
    1336489    NXE  2022-04-27   4.93          NexGen Energy Ltd.      Energy                 Uranium\
    1336490    NXE  2022-04-28   5.06          NexGen Energy Ltd.      Energy                 Uranium\
    1336491    NXE  2022-04-29   4.93          NexGen Energy Ltd.      Energy                 Uranium\
    """

    df_sectors                  = df_sectors.rename(columns={"Ticker":"Symbol"})
    df_enriched_quote_prices    = pd.merge(df_hist_prices, df_sectors, how="inner", on=["Symbol"])

    return df_enriched_quote_prices


def get_average_stock_price_day(df_sector_filtered: pd.DataFrame, sector:str) -> pd.DataFrame:
    """
    Calculating average stock price for a given sector per day
    Goal: get it's evolution through time

    To do: Implement a weigthed oned relatively to Market Value of company behind ticker

    :param df_sector_filtered:  Stock prices, senctor enriched and filterd for a given sector
    :param sector:              Ex: "Energy"
    """
    
    unique_dates            = df_sector_filtered['Date'].unique().tolist()
    dict_date_price_average = {}


    for date in unique_dates:
        print(date)
        price_average                   = df_sector_filtered.loc[df_sector_filtered['Date'] == date]['Close'].mean()
        dict_date_price_average[date]   = price_average 
    
    df_avg_quote_day            = pd.DataFrame(dict_date_price_average, index = [f'Avg_price_{sector}']).transpose().sort_index()
    df_avg_quote_day_smoothed   = df_avg_quote_day[f'Avg_price_{sector}'].rolling(NB_SMOOTHEN).sum()

    return df_avg_quote_day_smoothed


    
def get_all_sector_avg_price_evol(df_sector_enriched: pd.DataFrame) -> pd.DataFrame:
    """
    """
    # Making a dict of dataframes
    dict_dfs_sectors        = {}
    init                    = True
    final_df                = pd.DataFrame()

    for sector in Sectors:
        print(sector)
        dict_dfs_sectors[sector]    = df_sector_enriched.loc[df_sector_enriched['Sector'] == sector]
        df_avg_quote_day_smoothed   = get_average_stock_price_day(dict_dfs_sectors[sector], sector)
        df_avg_quote_day_smoothed   = df_avg_quote_day_smoothed.reset_index().rename({'index':'Date'}, axis = 'columns')

        if init == False:
            final_df                = pd.merge(final_df, df_avg_quote_day_smoothed, how="inner", on=["Date"])
        else:
            final_df                = df_avg_quote_day_smoothed.copy()

        init                        = False

    return final_df.iloc[NB_SMOOTHEN-1: , :]


if __name__ == '__main__':
    db_acc_obj              = std_db_acc_obj() 
    df_hist_prices          = get_historical_stock_prices("NYSE")
    
    df_sectors              = get_sectors_info()
    df_sector_enriched      = enrich_sect_info(df_hist_prices, df_sectors)
    
    # df_enriched_reduced     = df_sector_enriched.iloc[::2, :] # keep every nth row only
    final_df                = get_all_sector_avg_price_evol(df_sector_enriched)
    final_df                = final_df.set_index('Date')
    final_df_normalized     = (final_df / final_df.iloc[0])

    """
    fig                     = px.line(final_df_normalized, 
                                        x = final_df_normalized.index, 
                                        y = final_df_normalized.columns)

    fig.show()
    """