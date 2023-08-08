# python -m Sandbox.get_signals


from utils.fetchData import fetchSignals
from datetime import datetime, timedelta
import pandas as pd
from Sandbox.provider import Prices


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





def get_price_at_Dx_plus(row: pd.Series, d:int):
    """
    For a given row and column, gets the price at d + something
    """
    pass

def add_days_to_df(dataframe: pd.DataFrame, date_col_name: str, delta_days: int):
    """
    Adds the specified number of delta days to the 'Signaldate' column of the input dataframe.

    Parameters:
        dataframe (pandas.DataFrame): The input dataframe containing the 'Signaldate' column.
        delta_days (int): The number of days to add to each 'Signaldate' value.

    Returns:
        pandas.DataFrame: A new dataframe with the additional column containing Signaldate + delta_days.
    """
    # Convert the "Signaldate" column to datetime type
    # df["Signaldate"] = pd.to_datetime(df["Signaldate"])

    # Add the specified number of days to the "Signaldate" column and store it in a new column
    df[f"Signaldate_plus_{str(delta_days)}"] = df[date_col_name] + pd.Timedelta(days=delta_days)

    return df

"""
"Date_2" + 2  Days After ScanDate 
"Price_2" + 2  
"PriceEvolution_2"
"Date_3"
"PriceEvolution3"
"Date_4"
"PriceEvolution4"
"""
# Create col D+1, D+2, D+3



if __name__ == '__main__':
    df = filter_rows_by_delta(dfSignals).head(50).copy()

    df['SignalDate'] = pd.to_datetime(df['SignalDate'])
    df['ScanDate'] = pd.to_datetime(df['ScanDate'])

    price_provider = Prices()

    df = add_days_to_df(df, "SignalDate", 1)
    df["Price_day_1"] = df.apply(price_provider.get_price_from_df, axis=1)


    print(df)

# python -m Sandbox.get_signals

