import pandas as pd
from utils.indicators.rsi import calculate_rsi
from utils.indicators.aws import calculate_awesome_oscillator
from utils.indicators.williamsR import calculate_williamsR
from utils.indicators.stochastic import calculate_stochastic_k


class RoboticFundMetrics():

    def __init__(self, market_data: pd.DataFrame):
        # Now we want to construct a DataFrame with all metrics
        self.df = market_data
        self.df = self.df.set_index('snapshotTimeUTC', drop=False)
        self.df = self.df.sort_index()
        self.df['tmp_date'] = pd.to_datetime(self.df['snapshotTimeUTC'])
        self.df['weekNumber'] = self.df['tmp_date'].dt.isocalendar().week
        self.df['dayOfYear'] = self.df['tmp_date'].dt.day_of_week
        self.df['SMA_12'] = self.df['closePrice'].rolling(window=12).mean()
        self.df['SMA_25'] = self.df['closePrice'].rolling(window=25).mean()
        self.df['SMA_50'] = self.df['closePrice'].rolling(window=50).mean()
        self.df['SMA_80'] = self.df['closePrice'].rolling(window=80).mean()
        self.df['EMA_12'] = self.df['closePrice'].ewm(span=12).mean()
        self.df['EMA_26'] = self.df['closePrice'].ewm(span=26).mean()
        self.df['EMA_50'] = self.df['closePrice'].ewm(span=50).mean()
        self.df['EMA_80'] = self.df['closePrice'].ewm(span=80).mean()
        self.df['RSI'] = calculate_rsi(
            self.df, close_col='closePrice', window=14)
        self.df['AWS'] = calculate_awesome_oscillator(
            self.df, high='highPrice', low='lowPrice', window1=4, window2=64)
        self.df['MACD_12_26'] = self.df['EMA_12'] - self.df['EMA_26']
        self.df['MACD_SIGNAL_12_26'] = self.df['MACD_12_26'].ewm(span=9).mean()
        self.df['MACD_HIST_12_26'] = self.df['MACD_12_26'] - \
            self.df['MACD_SIGNAL_12_26']
        self.df['MACD_50_80'] = self.df['EMA_50'] - self.df['EMA_80']
        self.df['MACD_SIGNAL_50_80'] = self.df['MACD_50_80'].ewm(span=9).mean()
        self.df['MACD_HIST_50_80'] = self.df['MACD_50_80'] - \
            self.df['MACD_SIGNAL_50_80']
        self.df['WILLIAMS_R_14'] = calculate_williamsR(
            self.df, close_col='closePrice', window=14)
        self.df['STOCH_K_14'] = calculate_stochastic_k(
            self.df, close_col='closePrice', window=14)
        self.df['STOCH_D_14'] = self.df['STOCH_K_14'].rolling(window=3).mean()
