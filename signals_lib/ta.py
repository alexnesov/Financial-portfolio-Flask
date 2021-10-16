def aroon(data, lb=25):

    df = data.copy()
    df['up'] = 100 * df.High.rolling(lb + 1).apply(lambda x: x.argmax()) / lb
    df['dn'] = 100 * df.Low.rolling(lb + 1).apply(lambda x: x.argmin()) / lb

    return df['up'].tolist(), df['dn'].tolist() 


def rsi(df, timePeriodRSI):
    close = df['Close']
    # Get the difference in price from previous step
    delta = close.diff()
    # Get rid of the first row, which is NaN since it did not have a previous 
    # row to calculate the differences
    delta = delta[1:] 


    # Make the positive gains (up) and negative gains (down) Series
    up, down = delta.clip(lower=0), delta.clip(upper=0)
    

    # Calculate the EWMA
    roll_up1 = up.ewm(span=timePeriodRSI).mean()
    roll_down1 = down.abs().ewm(span=timePeriodRSI).mean()

    # Calculate the RSI based on EWMA
    RS1 = roll_up1 / roll_down1
    RSI1 = 100.0 - (100.0 / (1.0 + RS1))

    # Calculate the SMA
    roll_up2 = up.rolling(timePeriodRSI).mean()
    roll_down2 = down.abs().rolling(timePeriodRSI).mean()

    # Calculate the RSI based on SMA
    RS2 = roll_up2 / roll_down2
    RSI2 = 100.0 - (100.0 / (1.0 + RS2))

    return RSI2


