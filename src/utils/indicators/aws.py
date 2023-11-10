def calculate_awesome_oscillator(df, high='highPrice', low='lowPrice', window1=4, window2=64):
        """
        Calculates the Awesome Oscillator for a given DataFrame of high and low prices.
        df: a Pandas DataFrame containing the high and low prices to use in the calculation
        high: the name of the column containing the high prices (default 'high')
        low: the name of the column containing the low prices (default 'low')
        window1: the length of the first moving average (default 5)
        window2: the length of the second moving average (default 34)
        """
        # Calculate the midpoint price
        mid = (df[high] + df[low]) / 2

        # Calculate the moving averages
        sma1 = mid.rolling(window=window1).mean()
        sma2 = mid.rolling(window=window2).mean()

        # Calculate the Awesome Oscillator
        awesome_oscillator = sma1 - sma2

        return round(awesome_oscillator*10000, 2)