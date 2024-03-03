

import pandas as pd
import numpy as np
from .utils.indicators.rsi import calculate_rsi
from .utils.indicators.aws import calculate_awesome_oscillator
from .utils.indicators.williamsR import calculate_williamsR
from .utils.indicators.stochastic import calculate_stochastic_k


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
        self.df['lowestLowPriceStreak'] = self.df.groupby(
            (self.df['lowPrice'] > self.df['lowPrice'].shift(1)).cumsum()).cumcount()+1
        self.df['highestHighPriceStreak'] = self.df.groupby(
            (self.df['highPrice'] < self.df['highPrice'].shift(1)).cumsum()).cumcount()+1
        self.df['ATR_14'] = self.df['closePrice'].diff(
        ).abs().rolling(window=14).mean()

    def set_sma(self, length: int) -> None:
        '''
        Description: Calculates the Simple Moving Average

        Args:
            period (int): 

        Returns:
            adds column to dataframe 'SMA_{length}' in class variable 'df'
        '''
        self.df[f'SMA_{length}'] = self.df['closePrice'].rolling(
            window=length).mean()

    def set_ema(self, length: int) -> None:
        '''
        Description: Calculates the Exoponential Moving Average

        Args:
            period (int): 

        Returns:
            adds column to dataframe 'EMA_{length}' in class variable 'df'
        '''
        self.df[f'EMA_{length}'] = self.df['closePrice'].ewm(
            span=length).mean()

    def set_stochastic(self, length_k: int = 14, length_d: int = 3) -> None:
        '''
        Description: Calculates the Stochastics

        Args:
            period (int): 

        Returns:
            adds column to dataframe 'STOCH_K_{length_k}' in class variable 'df'
            adds column to dataframe 'STOCH_K_{length_d}' in class variable 'df'
        '''
        self.df[f'STOCH_K_{length_k}'] = calculate_stochastic_k(
            self.df, close_col='closePrice', window=length_k)
        self.df[f'STOCH_D_{length_d}'] = self.df['STOCH_K_14'].rolling(
            window=length_d).mean()

    def set_true_range(self) -> None:
        '''
        Description: Calculates the True Range

        Args:
            length (int): 

        Returns:
            adds column to dataframe 'tr' in class variable 'df'
        '''
        self.df['tr'] = self.df.apply(lambda row: max(row['highPrice'] - row['lowPrice'], abs(
            row['highPrice'] - row['closePrice']), abs(row['lowPrice'] - row['closePrice'])), axis=1)

    def set_atr(self, length: int) -> None:
        '''
        Description: Calculates the Average True Range

        Args:
            length (int): 

        Returns:
            adds column to dataframe 'atr' in class variable 'df'
        '''
        self.set_true_range()
        self.df['atr'] = self.df['tr'].rolling(window=length).mean()

    def set_adx(self, period=14) -> None:
        '''
        Description: Calculates the ADX

        Args:
            period (float): 

        Returns:
            adds column to dataframe 'adx' in class variable 'df'
        '''
        # Step 1: Calculate True Range (TR)
        self.set_true_range()

        # Step 2: Calculate Directional Movement (DM) and Directional Index (DI)
        self.df['DM_plus'] = self.df['highPrice'] - \
            self.df['highPrice'].shift(1)

        self.df['DM_minus'] = self.df['lowPrice'].shift(
            1) - self.df['lowPrice']

        self.df.loc[self.df['DM_plus'] < 0, 'DM_plus'] = 0
        self.df.loc[self.df['DM_minus'] < 0, 'DM_minus'] = 0
        self.df['DI_plus'] = 100 * (self.df['DM_plus'].rolling(
            window=period).mean() / self.df['tr'].rolling(window=period).mean())
        self.df['DI_minus'] = 100 * (self.df['DM_minus'].rolling(
            window=period).mean() / self.df['tr'].rolling(window=period).mean())

        # Step 3: Calculate Directional Index Difference (DX) and ADX
        self.df['DX'] = 100 * (abs(self.df['DI_plus'] - self.df['DI_minus']
                                   ) / (self.df['DI_plus'] + self.df['DI_minus']))

        self.df['adx'] = self.df['DX'].rolling(window=period).mean()

        self.df.drop(['DM_plus', 'DM_minus', 'DI_plus',
                      'DI_minus', 'DX'], axis=1, inplace=True)

    def set_parabolic_sar(self, initial_acceleration=0.02, acceleration_factor=0.02, max_acceleration_factor=0.2) -> None:
        '''
        Description: Calculates the Parabolic Stop and Reverse (SAR) & Trend

        Args:
            initial_acceleration (float): 
            acceleration_factor (float): 
            max_acceleration_factor (float):

        Returns:
            adds column to dataframe 'sar' in class variable 'df'
            adds column to dataframe 'sar_trend' in class variable 'df'
        '''
        # Initial values
        initial_af = initial_acceleration
        sar = []
        trend = []

        # Initialize first SAR value
        if self.df['highPrice'].iloc[1] > self.df['highPrice'].iloc[0]:
            sar.append(self.df['lowPrice'].iloc[0])
            trend.append('up')
        else:
            sar.append(self.df['highPrice'].iloc[0])
            trend.append('down')

        # Calculation loop
        for i in range(1, len(self.df)):
            if trend[-1] == 'up':
                if self.df['lowPrice'].iloc[i] < sar[-1]:
                    trend.append('down')
                    sar.append(self.df['highPrice'].iloc[i])
                    acceleration_factor = initial_af
                else:
                    trend.append('up')
                    sar.append(sar[-1] + acceleration_factor *
                               (self.df['lowPrice'].iloc[i] - sar[-1]))
                    if self.df['highPrice'].iloc[i] > self.df['highPrice'].iloc[i - 1]:
                        acceleration_factor = min(
                            acceleration_factor + initial_af, max_acceleration_factor)
            else:
                if self.df['highPrice'].iloc[i] > sar[-1]:
                    trend.append('up')
                    sar.append(self.df['lowPrice'].iloc[i])
                    acceleration_factor = initial_af
                else:
                    trend.append('down')
                    sar.append(sar[-1] - acceleration_factor *
                               (sar[-1] - self.df['highPrice'].iloc[i]))
                    if self.df['lowPrice'].iloc[i] < self.df['lowPrice'].iloc[i - 1]:
                        acceleration_factor = min(
                            acceleration_factor + initial_af, max_acceleration_factor)

        self.df['sar'] = sar
        self.df['sar_trend'] = trend

    def set_linear_regression(self, length: int = 21) -> None:
        '''
        Description: Calculates the linear regression of the close price

        Args:
            length (int): the lookback period (rolling) to run the regression on

        Returns:
            adds column to dataframe 'linear_regression' in class variable 'df'
        '''
        m_avg = self.df['closePrice'].rolling(window=length).mean()
        # calculate bar value
        highest = self.df['highPrice'].rolling(window=length).max()
        lowest = self.df['lowPrice'].rolling(window=length).min()
        m1 = (highest + lowest)/2
        value = (self.df['closePrice'] - (m1 + m_avg)/2)
        fit_y = np.array(range(0, length))
        self.df['linear_regression'] = round(value.rolling(window=length).apply(lambda x:
                                                                                np.polyfit(fit_y, x, 1)[0] * (length-1) +
                                                                                np.polyfit(fit_y, x, 1)[1], raw=True)*1000, 2)

    def set_keltner_channel(self, length: int, mult: int) -> None:
        '''
        Description: Calculates the keltner channel

        Args:
            length (int): the lookback period (rolling) for the moving average
            mult (int): how many multiples way from the ATR are the kc bands

        Returns:
            adds columns to dataframe 'upper_kc' in class variable 'df'
            adds columns to dataframe 'lower_kc' in class variable 'df'
        '''
        m_avg = self.df['closePrice'].rolling(window=length).mean()
        self.set_atr(length)
        upper_kc = m_avg + self.df['atr'] * mult
        lower_kc = m_avg - self.df['atr'] * mult

        self.df['upper_kc'] = upper_kc
        self.df['lower_kc'] = lower_kc

    def set_bollinger_bands(self, length: int, mult: int) -> None:
        '''
        Description: Calculates the bollinger bands

        Args:
            length (int): the lookback period (rolling) for the moving average
            mult (int): how many multiples way from the ATR are the bollinger bands

        Returns:
            adds columns to dataframe 'upper_bb' in class variable 'df'
            adds columns to dataframe 'lower_bb' in class variable 'df'
        '''
        m_avg = self.df['closePrice'].rolling(window=length).mean()
        m_std = self.df['closePrice'].rolling(window=length).std(ddof=0)
        self.df['upper_bb'] = m_avg + mult * m_std
        self.df['lower_bb'] = m_avg - mult * m_std

    def set_squeeze(self, length_bb, mult_bb, length_kc, mult_kc) -> None:
        '''
        Description: Determines if squeeze is on

        Args:
            length_bb (int): the lookback period (rolling) for the moving average bollinger band
            mult_bb (int): how many multiples way from the ATR are the bollinger bands
            length_kc (int): the lookback period (rolling) for the moving average keltner channel
            mult_kc (int): how many multiples way from the ATR are the keltner channel bands

        Returns:
            adds boolean column to dataframe 'squeeze_on' in class variable 'df'
        '''
        self.set_bollinger_bands(length_bb, mult_bb)
        self.set_keltner_channel(length_kc, mult_kc)
        self.df['squeeze_on'] = (self.df['upper_bb'] < self.df['upper_kc']) & (
            self.df['lower_bb'] > self.df['lower_kc'])

    def set_stops_from_pips(self, stop_pips_long: int, stop_pips_short: int, one_pip: float) -> None:
        '''
        Description: Calculate the stop price for long and short positions

        Args:
            stop_pips_long (int): number of pips below the entry price
            stop_pips_short (int): number of pips above the entry price
            one_pip (int): pip size

        Returns:
            adds float column to dataframe 'long_stop' in class variable 'df'
            adds float column to dataframe 'short_stop' in class variable 'df'
        '''
        self.df['long_stop'] = self.df['closePrice'] - stop_pips_long*one_pip
        self.df['short_stop'] = self.df['closePrice'] + stop_pips_short*one_pip

    def set_stops_from_atr(self, atr_length: int, mult_long: int, mult_short: int) -> None:
        '''
        Description: Calculate the stop price for long and short positions

        Args:
            stop_pips_long (int): number of pips below the entry price
            stop_pips_short (int): number of pips above the entry price
            one_pip (int): pip size

        Returns:
            adds float column to dataframe 'long_stop' in class variable 'df'
            adds float column to dataframe 'short_stop' in class variable 'df'
        '''
        self.set_atr(atr_length)
        self.df['long_stop'] = self.df['closePrice'] - self.df['atr']*mult_long
        self.df['short_stop'] = self.df['closePrice'] + \
            self.df['atr']*mult_short

    def set_stops_from_spikes(self, look_back_period: int) -> None:
        '''
        Description: Calculate the stop price for long and short positions

        Args:
            look_back_period (int): how far to look back for peaks

        Returns:
            adds float column to dataframe 'long_stop' in class variable 'df'
            adds float column to dataframe 'short_stop' in class variable 'df'
        '''
        self.df['long_stop'] = self.df['lowPrice'].rolling(
            window=look_back_period).min()
        self.df['short_stop'] = self.df['highPrice'].rolling(
            window=look_back_period).max()

    def set_limits(self, limit_pips_long: int, limit_pips_short: int, one_pip: float) -> None:
        '''
        Description: Calculate the limit price for long and short positions

        Args:
            stop_pips_long (int): number of pips above the entry price
            stop_pips_short (int): number of pips below the entry price
            one_pip (int): pip size

        Returns:
            adds float column to dataframe 'long_profit_take' in class variable 'df'
            adds float column to dataframe 'short_profit_take' in class variable 'df'
        '''
        self.df['long_profit_take'] = self.df['closePrice'] + \
            limit_pips_long*one_pip
        self.df['short_profit_take'] = self.df['closePrice'] - \
            limit_pips_short*one_pip

    def set_limits_from_atr(self, mult_long: int, mult_short: int) -> None:
        '''
        Description: Calculate the limit price for long and short positions

        Args:
            stop_pips_long (int): number of pips above the entry price
            stop_pips_short (int): number of pips below the entry price
            one_pip (int): pip size

        Returns:
            adds float column to dataframe 'long_profit_take' in class variable 'df'
            adds float column to dataframe 'short_profit_take' in class variable 'df'
        '''
        self.df['long_profit_take'] = self.df['closePrice'] + \
            self.df['atr']*mult_long
        self.df['short_profit_take'] = self.df['closePrice'] - \
            self.df['atr']*mult_short

    def simulate_trades_intraday(self) -> pd.DataFrame:
        """ Run a back test for a given trading strategy
        The dataframe requires the following fields:
        - snapshotTimeUTC: date
        - entry_long: boolean
        - entry_short: boolean
        - long_profit_take: numeric
        - short_profit_take: numeric
        - long_stop: numeric
        - short_stop: numeric
        - exit_long: boolean
        - exit_short: boolean \n
        It will return the original dataframe + the following new fields:
        - buyDate: date
        - sellDate: date
        - sellPrice: numeric
        - long_exit_signal: boolean
        - short_exit_signal: boolean
        - exit_reason: string
        """

        # Simulate trades
        self.df['sellPrice'] = np.NaN
        self.df['sellDate'] = None
        self.df['buyDate'] = None
        self.df['profit'] = np.NaN
        self.df['long_exit_signal'] = False
        self.df['short_exit_signal'] = False
        self.df['exit_reason'] = ''

        # Create two filtered arrays of the long & short entries
        long_entry_metrics = self.df[self.df['entry_long'] == True]
        short_entry_metrics = self.df[self.df['entry_short'] == True]

        for long_entry in long_entry_metrics.itertuples():
            self.df.loc[long_entry[0], 'buyDate'] = long_entry.snapshotTimeUTC
            self.df.loc[long_entry[0], 'buyPrice'] = long_entry.closePrice
            scan_forward = self.df[long_entry[0]:]
            for long_exit in scan_forward.itertuples():
                limit_level = self.df.loc[long_entry[0], 'long_profit_take']
                if (long_exit.lowPrice < long_entry.long_stop and long_exit.snapshotTimeUTC != long_entry.snapshotTimeUTC):
                    sell_price = long_entry.long_stop
                    self.df.loc[long_entry[0], 'sellPrice'] = sell_price
                    self.df.loc[long_exit[0], 'long_exit_signal'] = True
                    self.df.loc[long_entry[0], 'exit_reason'] = 'STOP'
                    self.df.loc[long_entry[0],
                                'sellDate'] = long_exit.snapshotTimeUTC
                    break
                elif (long_exit.highPrice > limit_level and long_exit.snapshotTimeUTC != long_entry.snapshotTimeUTC):
                    sell_price = limit_level
                    self.df.loc[long_entry[0], 'sellPrice'] = sell_price
                    self.df.loc[long_exit[0], 'long_exit_signal'] = True
                    self.df.loc[long_entry[0], 'exit_reason'] = 'LIMIT'
                    self.df.loc[long_entry[0],
                                'sellDate'] = long_exit.snapshotTimeUTC
                    break
                elif (long_exit.exit_long == True and (long_exit.snapshotTimeUTC != long_entry.snapshotTimeUTC)):
                    sell_price = long_exit.closePrice
                    self.df.loc[long_entry[0], 'sellPrice'] = sell_price
                    self.df.loc[long_exit[0], 'long_exit_signal'] = True
                    self.df.loc[long_entry[0], 'exit_reason'] = 'RULE'
                    self.df.loc[long_entry[0],
                                'sellDate'] = long_exit.snapshotTimeUTC
                    break

        # Simulate short exit
        for short_entry in short_entry_metrics.itertuples():
            self.df.loc[short_entry[0],
                        'buyDate'] = short_entry.snapshotTimeUTC
            self.df.loc[short_entry[0], 'buyPrice'] = short_entry.closePrice
            scan_forward = self.df[short_entry[0]:]
            for short_exit in scan_forward.itertuples():
                limit_level = self.df.loc[short_entry[0], 'short_profit_take']
                if (short_exit.highPrice > short_entry.short_stop and (short_exit.snapshotTimeUTC != short_entry.snapshotTimeUTC)):
                    sell_price = short_entry.short_stop
                    self.df.loc[short_entry[0], 'sellPrice'] = sell_price
                    self.df.loc[short_exit[0], 'short_exit_signal'] = True
                    self.df.loc[short_entry[0], 'exit_reason'] = 'STOP'
                    self.df.loc[short_entry[0],
                                'sellDate'] = short_exit.snapshotTimeUTC
                    break
                elif (short_exit.lowPrice < limit_level and (short_exit.snapshotTimeUTC != short_entry.snapshotTimeUTC)):
                    sell_price = limit_level
                    self.df.loc[short_entry[0], 'sellPrice'] = sell_price
                    self.df.loc[short_exit[0], 'short_exit_signal'] = True
                    self.df.loc[short_entry[0], 'exit_reason'] = 'LIMIT'
                    self.df.loc[short_entry[0],
                                'sellDate'] = short_exit.snapshotTimeUTC
                    break
                elif ((short_exit.exit_short == True) and (short_exit.snapshotTimeUTC != short_entry.snapshotTimeUTC)):
                    sell_price = short_exit.closePrice
                    self.df.loc[short_entry[0], 'sellPrice'] = sell_price
                    self.df.loc[short_exit[0], 'short_exit_signal'] = True
                    self.df.loc[short_entry[0], 'exit_reason'] = 'RULE'
                    self.df.loc[short_entry[0],
                                'sellDate'] = short_exit.snapshotTimeUTC
                    break
        return self.df

    def add_more_stats(self, notional_value: float) -> None:
        '''
        Description: Calculates simulation stats

        Args:
            notional_value (float): notional value of each trade

        Returns:
            adds float column to dataframe 'long_profit' in class variable 'df'
            adds float column to dataframe 'short_profit' in class variable 'df'
            adds float column to dataframe 'profit' in class variable 'df'
            adds int column to dataframe 'long_counter' in class variable 'df'
            adds int column to dataframe 'short_counter' in class variable 'df'
            adds float column to dataframe 'profit_streak' in class variable 'df'
            adds float column to dataframe 'drawdown' in class variable 'df'
        '''
        # Calculate profit
        self.df['long_profit'] = np.where(
            self.df['entry_long'] == True, (self.df['sellPrice']/self.df['buyPrice'] - 1)*notional_value, 0)

        self.df['short_profit'] = np.where(
            self.df['entry_short'] == True, (1 - self.df['sellPrice']/self.df['buyPrice'])*notional_value, 0)

        self.df['profit'] = self.df['long_profit'] + self.df['short_profit']
        self.df['profit'] = self.df['profit'].replace(0, np.NaN)

        # Calculate num positions opened
        long_counter = 0
        short_counter = 0
        profit_streak = 0
        drawdown = 0
        self.df['long_counter'] = 0
        self.df['short_counter'] = 0
        self.df['profit_streak'] = 0
        self.df['drawdown'] = 0
        for row in self.df.itertuples():
            if (row.profit > 0):
                profit_streak = profit_streak + row.profit
                self.df.loc[row[0], 'profit_streak'] = profit_streak
                drawdown = 0
            elif (row.profit < 0):
                drawdown = drawdown + row.profit
                self.df.loc[row[0], 'drawdown'] = drawdown
                profit_streak = 0

            if row.entry_long == True:
                long_counter = long_counter + 1
                self.df.loc[row[0], 'long_counter'] = long_counter
            if row.entry_short == True:
                short_counter = short_counter + 1
                self.df.loc[row[0], 'short_counter'] = short_counter
            if row.short_exit_signal == True:
                short_counter = 0
            if row.long_exit_signal == True:
                long_counter = 0

    def print_stats(self, notional_value: int = 1000000, margin_per_trade: float = 0.04):
        '''
        Description: Print simulation back test results to screen

        Args:
            notional_value (float): notional value of each trade
            margin_per_trade (float): margin % of each trade

        Returns:
            adds float column to dataframe 'hours_held' in class variable 'df'
        '''
        self.add_more_stats(notional_value)

        # Print trade level data
        print(self.df[['openPrice', 'lowPrice', 'highPrice', 'closePrice', 'entry_long', 'long_stop', 'long_profit_take', 'entry_short', 'short_stop',
                       'short_profit_take', 'sellDate', 'sellPrice', 'profit', 'drawdown', 'exit_reason']].to_string())

        # Output summary stats
        self.df['buyDate'] = pd.to_datetime(self.df['buyDate'])
        self.df['sellDate'] = pd.to_datetime(self.df['sellDate'])
        self.df['hours_held'] = (self.df['sellDate'] -
                                 self.df['buyDate']) / pd.Timedelta(hours=1)
        print(
            f"Notional value per trade ${notional_value}. I.e. without leverage.")
        print(f"At 0.4% margin, the margin requirement is $5,000 per trade.")
        print(f"Instrument is {self.df['instrument'].iloc[0]}")
        print(f"----------------------------------------------------------------------------------------------------------------------")
        print(
            f"Total profit is ${round(self.df['profit'].sum(), 1)}")
        print(
            f"Average profit per trade ${round(self.df['profit'].mean(), 1)}")
        print(
            f"Total number of trades {self.df[abs(self.df.profit) > 0].shape[0]}")
        print(
            f"Mean hold time is {round(self.df['hours_held'].mean(), 0)} hours")
        print(
            f"Max hold time is {round(self.df['hours_held'].max(), 0)} hours on {self.df.loc[self.df['hours_held'].idxmax()]['snapshotTimeUTC']}")
        win_rate = round((self.df[self.df.profit > 0].shape[0] /
                          self.df[abs(self.df.profit) > 0].shape[0]) * 100, 1)
        print(f"Win rate is {win_rate}%")
        print(f"----------------------------------------------------------------------------------------------------------------------")
        print(
            f"{round(self.df.groupby(self.df.index.year)['profit'].sum(),1)}")
        print(f"----------------------------------------------------------------------------------------------------------------------")
        print(f"Max number of long positions {self.df['long_counter'].max()}")
        print(
            f"Max number of short positions {self.df['short_counter'].max()}")
        print(
            f"Biggest single loss ${round(self.df['profit'].min(),0)} on {self.df.loc[self.df['profit'].idxmin()]['snapshotTimeUTC']}")
        print(
            f"Biggest single profit ${round(self.df['profit'].max(),0)} on {self.df.loc[self.df['profit'].idxmax()]['snapshotTimeUTC']}")
        print(f"Max drawdown ${round(self.df['drawdown'].min(),0)}")
        print(
            f"Largest profit streak ${round(self.df['profit_streak'].max(),0)}")
        # Add breakdown by Long or short
        print(
            f"Long profit ${round(self.df[self.df['entry_long']==True]['profit'].sum(),1)}")
        print(
            f"Short profit ${round(self.df[self.df['entry_short']==True]['profit'].sum(),1)}")

        # Calculate what Account balance is required to trade this
        if self.df['short_counter'].max() > self.df['long_counter'].max():
            max_holds = self.df['short_counter'].max()
        else:
            max_holds = self.df['long_counter'].max()
        account_balance_need = margin_per_trade + max_holds * margin_per_trade + \
            abs(round(self.df['drawdown'].min(), 0))
        print(
            f"Minimum account balance required ${account_balance_need}")
        print(f"----------------------------------------------------------------------------------------------------------------------")
