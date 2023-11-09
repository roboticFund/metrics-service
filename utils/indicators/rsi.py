def calculate_rsi(df, close_col='closePrice', window=14):
    """
    Calculates the Relative Strength Index (RSI) for a given DataFrame of prices.
    df: a Pandas DataFrame containing the price data to use in the calculation
    close_col: the name of the column containing the closing prices (default 'close')
    window: the length of the RSI window (default 14)
    """
    # Calculate the price change
    price_change = df[close_col].diff()
    
    # Get the positive and negative price changes
    positive_change = price_change.where(price_change > 0, 0)
    negative_change = -price_change.where(price_change < 0, 0)
    
    # Calculate the average gain and average loss
    average_gain = positive_change.rolling(window).mean()
    average_loss = negative_change.rolling(window).mean()
    
    # Calculate the relative strength (RS)
    rs = average_gain / average_loss
    
    # Calculate the RSI
    rsi = 100 - (100 / (1 + rs))
    
    return rsi