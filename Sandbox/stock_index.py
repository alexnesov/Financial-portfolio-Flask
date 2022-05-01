import pandas as pd
import os, sys



from utils.db_manage import QuRetType, dfToRDS, std_db_acc_obj




def get_historical_stock_prices(stock_exchange: str):
    """
    :param stock_exchange: ex: "NASDAQ"
    """
    qu_historical_prices        = f"SELECT Symbol, Date, Close \
                                FROM marketdata.{stock_exchange}"

    df_hist_prices              = db_acc_obj.exc_query(db_name     = 'marketdata', 
                                                       query       = qu_historical_prices,
                                                       retres      = QuRetType.ALLASPD)

    return df_hist_prices


def get_sectors_info():
    """
    """
    qu_sectors                  = "SELECT * FROM marketdata.sectors"

    df_sectors                  = db_acc_obj.exc_query(db_name     = 'marketdata', 
                                                       query       = qu_sectors,
                                                       retres      = QuRetType.ALLASPD)
    
    return df_sectors


def enrich_sect_info(df_hist_prices: pd.DataFrame): 
    """
    Enriching with sector information
    
    Not doing enrichment withing SQL RDS database because ram is very low (to lower cost), whereas way stronger on personnal
    computer and on AWS EC2. Therefore doing more complex ops on VM.
    Output ex:
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



if __name__ == '__main__':
    db_acc_obj      = std_db_acc_obj() 
    df_hist_prices  = get_historical_stock_prices()
    df_sectors      = get_sectors_info()
    enrich_sect_info()








"""
import plotly.express as px
df = px.data.stocks()
fig = px.line(df,
              x             = "date", 
              y             = df.columns,
              hover_data    = {"date": "|%B %d, %Y"},
              title         = 'custom tick labels')
fig.update_xaxes(
    dtick       = "M1",
    tickformat  = "%b\n%Y")
fig.show()
"""