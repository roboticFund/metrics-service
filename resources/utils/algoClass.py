import pandas as pd  

class AlgoClass:

    def __init__(self, algoTableName, currentPrice, pair, dbConnection):
        self.algoTableName = algoTableName
        self.pair = pair
        self.dbConnection = dbConnection
        self.currentPrice = currentPrice
        self.getAndSetData()
    
    def getAndSetData(self):
        self.limit = 100
        sql_query = pd.read_sql_query (f"Select EMA_12,EMA_26,EMA_50,EMA_80,macd,macd_new,closePrice,highPrice,lowPrice,stoch_k from {self.algoTableName} where pair='{self.pair}' order by dateTime desc limit {self.limit}", self.dbConnection)
        self.df = pd.DataFrame(sql_query, columns = ['EMA_12', 'EMA_26', 'EMA_50', 'EMA_80', 'macd', 'macd_new', 'closePrice', 'highPrice', 'lowPrice', 'stoch_k'])
        self.df['closePriceSum'] = self.df['closePrice'].cumsum()
        self.df['stoch_k_sum'] = self.df['stoch_k'].cumsum()
        self.EMA_12 = self.df['EMA_12'].iloc[0]
        self.EMA_26 = self.df['EMA_26'].iloc[0]
        self.EMA_50 = self.df['EMA_50'].iloc[0]
        self.EMA_80 = self.df['EMA_80'].iloc[0]
        self.macd = self.df['macd'].iloc[0]
        self.macd_new = self.df['macd_new'].iloc[0]

    def RSI(self, period:int):
        delta = self.df['closePrice'].diff(periods=-1)
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()
        rs = avg_gain / avg_loss
        return round((100 - (100 / (1 + rs[self.limit-1]))),4)

    def EMA(self, period:int):
        # First create weighted multipler
        WeightedMultiplier = 2 / (period + 1)
        # Return result as tuple, need to get first value as query returns 1 only
        if (period == 12):
            lastEMA = self.EMA_12
        elif (period == 26):
            lastEMA = self.EMA_26
        elif (period == 50):
            lastEMA = self.EMA_50
        elif (period == 80):
            lastEMA = self.EMA_80
        else:
            return None
        # Calculate EMA
        return self.currentPrice * WeightedMultiplier + \
            lastEMA * (1 - WeightedMultiplier)
    
    # This functions return the exponential moving average of the MACD
    def EMA_MACD(self, currentMACD):
        # First create weighted multipler, hard code to period of 9
        WeightedMultiplier = 2 / (9 + 1)
        # Calculate EMA
        return currentMACD * WeightedMultiplier + \
            self.macd * (1 - WeightedMultiplier)

    # This functions return the exponential moving average of the MACD
    def EMA_MACD_NEW(self, currentMACDNew):
        # First create weighted multipler, hard code to period of 60
        WeightedMultiplier = 2 / (60 + 1)
        # Calculate EMA
        return (currentMACDNew * WeightedMultiplier) + \
            (self.macd_new * (1 - WeightedMultiplier))
    
    def SMA(self, period:int):
        # Run query
        sumClose = self.df['closePriceSum'].iloc[period - 2] + self.currentPrice
        # Calculate SMA
        return (sumClose) / period

    # %k = ( (C-L14)/(H14-L14) ) X 100
    # C = The most recent closing price
    # L14 = The lowest price traded of the 14 previous
    # trading sessions
    # H14 = The highest price traded during the same
    # 14-day period
    # %K = The current value of the stochastic indicator
    def stochastic(self, period):
        df = self.df.head(period)
        L_PERIOD = df['lowPrice'].min()
        H_PERIOD = df['highPrice'].max()
        # Calculate stochastic K first
        stoch_k = ((self.currentPrice - L_PERIOD) / (H_PERIOD - L_PERIOD)) * 100
        stochkSum = self.df['stoch_k_sum'].iloc[1]
        # Calculate stoch d
        stoch_d = (stochkSum + stoch_k) / 3
        # Create return values
        return ({"STOCH_K": stoch_k, "STOCH_D": stoch_d})
    
    # Wiliams %R= Highest High− Close / Highest High − Lowest Low
    # ​
    # where
    # Highest High=Highest price in the lookback period, typically 14 days.
    # Close=Most recent closing price.
    # Lowest Low=Lowest price in the lookback period, typically 14 days.
    def williamsR(self, period):
        df = self.df.head(period)
        L_PERIOD = df['lowPrice'].min()
        H_PERIOD = df['highPrice'].max()
        # Calculate WilliamsR
        return ((H_PERIOD - self.currentPrice) / (H_PERIOD - L_PERIOD)) * 100 * -1