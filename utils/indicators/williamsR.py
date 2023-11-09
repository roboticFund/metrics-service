# Wiliams %R= Highest High− Close / Highest High − Lowest Low
# ​
# where
# Highest High=Highest price in the lookback period, typically 14 days.
# Close=Most recent closing price.
# Lowest Low=Lowest price in the lookback period, typically 14 days.
def calculate_williamsR(df, close_col='closePrice', window=14):
    L_PERIOD = df['lowPrice'].rolling(window).min()
    H_PERIOD = df['highPrice'].rolling(window).max()
    return ((H_PERIOD - df[close_col]) / (H_PERIOD - L_PERIOD)) * 100 * -1
