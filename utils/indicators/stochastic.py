# %k = ( (C-L14)/(H14-L14) ) X 100
# C = The most recent closing price
# L14 = The lowest price traded of the 14 previous
# trading sessions
# H14 = The highest price traded during the same
# 14-day period
# %K = The current value of the stochastic indicator
def calculate_stochastic_k(df, close_col='closePrice', window=14):

    L_PERIOD = df['lowPrice'].rolling(window).min()
    H_PERIOD = df['highPrice'].rolling(window).max()

    return ((df[close_col] - L_PERIOD) /
            (H_PERIOD - L_PERIOD)) * 100
