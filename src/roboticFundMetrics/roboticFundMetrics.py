

import pandas as pd
import numpy as np
from .utils.indicators.rsi import calculate_rsi
from .utils.indicators.aws import calculate_awesome_oscillator
from .utils.indicators.williamsR import calculate_williamsR
from .utils.indicators.stochastic import calculate_stochastic_k


class RoboticFundMetrics():
    position_size: int
    win_rate: float
    max_drawdown: float
    max_profit_streak: float
    average_gain_weighted_to_1: float
    average_gain_score: float
    win_rate_score: int
    drawdown_score: float
    final_score: int

    def __init__(self, market_data: pd.DataFrame):
        # Now we want to construct a DataFrame with all metrics
        self.df = market_data
        self.df = self.df.set_index('snapshotTimeUTC', drop=False)
        self.df = self.df.sort_index()
        self.df['tmp_date'] = pd.to_datetime(self.df['snapshotTimeUTC'])
        self.df['weekNumber'] = self.df['tmp_date'].dt.isocalendar().week
        self.df['dayOfYear'] = self.df['tmp_date'].dt.day_of_week
        self.df['hour'] = self.df['tmp_date'].dt.hour
        self.df['year'] = self.df['tmp_date'].dt.year
        self.df['dayOfWeek'] = self.df['tmp_date'].dt.dayofweek
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
        prev_close = self.df['closePrice'].shift(1)
        self.df['tr'] = np.maximum.reduce([self.df['highPrice'] - self.df['lowPrice'], (
            self.df['highPrice'] - prev_close).abs(), (self.df['lowPrice'] - prev_close).abs()])

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

    def set_bollinger_bands(self, length: int, mult: float, length_std: int) -> None:
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
        m_std = self.df['closePrice'].rolling(window=length).std()
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

    def set_stops_from_atr_direction(self, atr_length: int, mult: int, direction: str) -> None:
        '''
        Description: Calculate the stop price for long or short positions as specific by direction

        Args:
            atr_length (int): ATR length
            mult (int): ATR multipler from closePrice
            direction (str): 'long' or 'short'

        Returns:
            adds float column to dataframe 'long_stop' in class variable 'df' OR
            adds float column to dataframe 'short_stop' in class variable 'df'
        '''
        self.set_atr(atr_length)
        if direction == 'long':
            self.df['long_stop'] = self.df['closePrice'] - self.df['atr']*mult
        elif direction == 'short':
            self.df['short_stop'] = self.df['closePrice'] + \
                self.df['atr']*mult
        else:
            raise Exception(
                'long or short not provided in direction parameter')

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

    def set_limits_from_atr(self, atr_length: int, mult_long: int, mult_short: int) -> None:
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
        self.set_atr(atr_length)
        self.df['long_profit_take'] = self.df['closePrice'] + \
            self.df['atr']*mult_long
        self.df['short_profit_take'] = self.df['closePrice'] - \
            self.df['atr']*mult_short

    def set_limits_from_atr_direction(self, atr_length: int, mult: int, direction: str) -> None:
        '''
        Description: Calculate the limit price for long and short positions

        Args:
            atr_length (int): ATR lenght
            mult (int): ATR multipler
            direction (str): 'long' or 'short'

        Returns:
            adds float column to dataframe 'long/short_profit_take' in class variable 'df'
            adds float column to dataframe 'short/short_profit_take' in class variable 'df'
        '''
        self.set_atr(atr_length)
        if direction == 'long':
            self.df[f'{direction}_profit_take'] = self.df['closePrice'] + \
                self.df['atr']*mult
        elif direction == 'short':
            self.df[f'{direction}_profit_take'] = self.df['closePrice'] - \
                self.df['atr']*mult
        else:
            raise Exception('long or short direction not provided.')

    def calcualte_fibonacci_retracement(self, threshold_large_step: int) -> None:
        reset_index = None
        fibonacci_levels = {}
        fib_count = 0

        for index, row in self.df.iterrows():
            rolling_high = self.df.loc[reset_index:index, 'highPrice'].max()
            rolling_low = self.df.loc[reset_index:index, 'lowPrice'].min()
            difference = abs(rolling_high - rolling_low) * 100000

            if difference > threshold_large_step:
                reset_index = index
                fib_count = 0
                fibonacci_levels = {}
                fibonacci_levels[0] = rolling_low
                fibonacci_levels[1] = rolling_high
                for i in range(2, 6):
                    fibonacci_levels[i] = fibonacci_levels[i - 1] - (
                        fibonacci_levels[i - 1] - fibonacci_levels[i - 2]) / 1.618
                self.df.at[index, 'Fib_Step'] = 1
                for level, value in fibonacci_levels.items():
                    self.df.at[index, f'Fibonacci Level {level}'] = value
            else:
                self.df.at[index, 'Fib_Step'] = 0
                for level, value in fibonacci_levels.items():
                    self.df.at[index, f'Fibonacci Level {level}'] = value

            self.df.at[index, 'Fib_Count'] = fib_count
            fib_count += 1

    def set_stops_from_max(self, max_loss: int) -> None:
        '''
        Description: Calculate the stop price for max_loss


        '''
        self.df['short_stop'] = abs(
            (max_loss / (5000 / 0.004))+1)*(self.df['closePrice'])

    def simulate_trades_intraday_trailing_stop(self, trailing_step_pips=1) -> pd.DataFrame:
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
        self.df['sellPrice'] = np.nan
        self.df['sellDate'] = None
        self.df['buyDate'] = None
        self.df['profit'] = np.nan
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
            # Trailing stop logic
            new_long_stop = long_entry.long_stop
            original_long_stop_gap = long_entry.closePrice - long_entry.long_stop

            for long_exit in scan_forward.itertuples():
                new_long_stop_gap = long_exit.closePrice - new_long_stop
                if (long_exit.lowPrice < new_long_stop and long_exit.snapshotTimeUTC != long_entry.snapshotTimeUTC):
                    sell_price = new_long_stop
                    self.df.loc[long_entry[0], 'sellPrice'] = sell_price
                    self.df.loc[long_exit[0], 'long_exit_signal'] = True
                    self.df.loc[long_entry[0], 'exit_reason'] = 'STOP'
                    self.df.loc[long_entry[0],
                                'sellDate'] = long_exit.snapshotTimeUTC
                    break
                elif (long_exit.highPrice > long_entry.long_profit_take and long_exit.snapshotTimeUTC != long_entry.snapshotTimeUTC):
                    sell_price = long_entry.long_profit_take
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
                elif new_long_stop_gap - original_long_stop_gap > trailing_step_pips:
                    new_long_stop = long_exit.closePrice - original_long_stop_gap

        # Simulate short exit
        for short_entry in short_entry_metrics.itertuples():
            self.df.loc[short_entry[0],
                        'buyDate'] = short_entry.snapshotTimeUTC
            self.df.loc[short_entry[0], 'buyPrice'] = short_entry.closePrice
            scan_forward = self.df[short_entry[0]:]
            # Trailing stop logic
            new_short_stop = short_entry.short_stop
            original_short_stop_gap = short_entry.short_stop - short_entry.closePrice

            for short_exit in scan_forward.itertuples():
                new_short_stop_gap = new_short_stop - short_exit.closePrice

                if (short_exit.highPrice > new_short_stop and (short_exit.snapshotTimeUTC != short_entry.snapshotTimeUTC)):
                    sell_price = new_short_stop
                    self.df.loc[short_entry[0], 'sellPrice'] = sell_price
                    self.df.loc[short_exit[0], 'short_exit_signal'] = True
                    self.df.loc[short_entry[0], 'exit_reason'] = 'STOP'
                    self.df.loc[short_entry[0],
                                'sellDate'] = short_exit.snapshotTimeUTC
                    break
                elif (short_exit.lowPrice < short_entry.short_profit_take and (short_exit.snapshotTimeUTC != short_entry.snapshotTimeUTC)):
                    sell_price = short_entry.short_profit_take
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
                elif new_short_stop_gap - original_short_stop_gap > trailing_step_pips:
                    new_short_stop = short_exit.closePrice + original_short_stop_gap
                    
        return self.df

    def set_df_values(self, buyDate, sell_price, reason, sell_date, direction):
        self.df.loc[buyDate, 'sellPrice'] = sell_price
        self.df.loc[buyDate, 'exit_reason'] = reason
        self.df.loc[buyDate, 'sellDate'] = sell_date
        if direction == 'SHORT':
            self.df.loc[sell_date, 'short_exit_signal'] = True
        else:
            self.df.loc[sell_date, 'long_exit_signal'] = True

    def simulate_trades_intraday(self) -> None:
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

        # Convert to numpy array for speed
        data_2 = self.df[['snapshotTimeUTC', 'entry_long', 'entry_short', 'openPrice',
                          'lowPrice', 'highPrice', 'closePrice', 'long_stop', 'short_stop', 'long_profit_take', 'short_profit_take', 'exit_long', 'exit_short']]
        np_array = data_2.to_numpy()

        # Simulate trades
        self.df['sellPrice'] = np.nan
        self.df['sellDate'] = None
        self.df['buyDate'] = None
        self.df['profit'] = np.nan
        self.df['long_exit_signal'] = False
        self.df['short_exit_signal'] = False
        self.df['exit_reason'] = ''

        for idx, x in enumerate(np_array):
            if x[1] == True:  # Long entry
                buyDate = x[0]
                buyPrice = x[6]
                long_stop = x[7]
                long_profit_take = x[9]
                self.df.loc[buyDate, 'buyDate'] = buyDate
                self.df.loc[buyDate, 'buyPrice'] = buyPrice

                # Check if stop is triggered
                time_stamps = np_array[idx+1:idx+500][:, 0]
                close_prices = np_array[idx+1:idx+500][:, 6]
                low_prices = np_array[idx+1:idx+500][:, 4]
                high_prices = np_array[idx+1:idx+500][:, 5]
                long_exits = np_array[idx+1:idx+500][:, 11]
                try:
                    stop_triggered = np.where(low_prices < long_stop)
                    stop_trigger_idx = stop_triggered[0][0]
                except:
                    stop_trigger_idx = len(long_exits) - 1
                try:
                    limit_triggered = np.where(high_prices >= long_profit_take)
                    limit_trigger_idx = limit_triggered[0][0]
                except:
                    limit_trigger_idx = len(long_exits) - 1
                try:
                    rule_triggered = np.where(long_exits == True)
                    rule_triggered_idx = rule_triggered[0][0]
                except:
                    rule_triggered_idx = len(long_exits) - 1

                # Choose which trigger comes first
                if stop_trigger_idx <= limit_trigger_idx and stop_trigger_idx <= rule_triggered_idx:
                    sell_date = time_stamps[stop_trigger_idx]
                    sell_price = long_stop
                    reason = 'STOP'
                    self.set_df_values(buyDate, sell_price,
                                       reason, sell_date, 'LONG')
                elif limit_trigger_idx <= rule_triggered_idx:
                    sell_date = time_stamps[limit_trigger_idx]
                    sell_price = long_profit_take
                    reason = 'LIMIT'
                    self.set_df_values(buyDate, sell_price,
                                       reason, sell_date, 'LONG')
                else:
                    sell_date = time_stamps[rule_triggered_idx]
                    sell_price = close_prices[rule_triggered_idx]
                    reason = 'RULE'
                    self.set_df_values(buyDate, sell_price,
                                       reason, sell_date, 'LONG')

            if x[2] == True:  # Short entry
                buyDate = x[0]
                buyPrice = x[6]
                short_stop = x[8]
                short_profit_take = x[10]
                self.df.loc[buyDate, 'buyDate'] = buyDate
                self.df.loc[buyDate, 'buyPrice'] = buyPrice

                # Check if stop is triggered
                time_stamps = np_array[idx+1:idx+500][:, 0]
                close_prices = np_array[idx+1:idx+500][:, 6]
                high_prices = np_array[idx+1:idx+500][:, 5]
                low_prices = np_array[idx+1:idx+500][:, 4]
                short_exits = np_array[idx+1:idx+500][:, 12]

                try:
                    stop_triggered = np.where(high_prices >= short_stop)
                    stop_trigger_idx = stop_triggered[0][0]
                except:
                    stop_trigger_idx = len(short_exits) - 1
                try:
                    limit_triggered = np.where(low_prices <= short_profit_take)
                    limit_trigger_idx = limit_triggered[0][0]
                except:
                    limit_trigger_idx = len(short_exits) - 1
                try:
                    rule_triggered = np.where(short_exits == True)
                    rule_triggered_idx = rule_triggered[0][0]
                except:
                    rule_triggered_idx = len(short_exits) - 1

                # Choose which trigger comes first
                if stop_trigger_idx <= limit_trigger_idx and stop_trigger_idx <= rule_triggered_idx:
                    sell_date = time_stamps[stop_trigger_idx]
                    sell_price = short_stop
                    reason = 'STOP'
                    self.set_df_values(buyDate, sell_price,
                                       reason, sell_date, 'SHORT')
                elif limit_trigger_idx <= rule_triggered_idx:
                    sell_date = time_stamps[limit_trigger_idx]
                    sell_price = short_profit_take
                    reason = 'LIMIT'
                    self.set_df_values(buyDate, sell_price,
                                       reason, sell_date, 'SHORT')
                else:
                    sell_date = time_stamps[rule_triggered_idx]
                    sell_price = close_prices[rule_triggered_idx]
                    reason = 'RULE'
                    self.set_df_values(buyDate, sell_price,
                                       reason, sell_date, 'SHORT')
                        
                    
    def add_more_stats(self) -> None:
        '''
        Description: Calculates simulation stats

        Args:
            None

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
        self.df['long_profit'] = np.where(self.df['entry_long'] == True, ((
            self.df['sellPrice'] - self.df['buyPrice']) * self.notional_value * (1/self.df['sellPrice'])), 0)

        self.df['short_profit'] = np.where(
            self.df['entry_short'] == True, ((self.df['buyPrice'] - self.df['sellPrice']) * self.notional_value * (1/self.df['sellPrice'])), 0)

        self.df['profit'] = self.df['long_profit'] + self.df['short_profit']
        self.df['profit'] = self.df['profit'].replace(0, np.nan)

        # Calculate num positions opened
        long_counter = 0
        short_counter = 0
        profit_streak = 0
        drawdown = 0
        stop_violation_counter = 0
        limit_violation_counter = 0
        self.df['long_counter'] = 0
        self.df['short_counter'] = 0
        self.df['profit_streak'] = 0
        self.df['drawdown'] = 0
        self.df['stop_violation'] = 0
        self.df['limit_violation'] = 0
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

            if (row.entry_long == True and row.long_stop > row.closePrice) or (row.entry_short == True and row.short_stop < row.closePrice):
                stop_violation_counter = stop_violation_counter+1
                self.df.loc[row[0], 'stop_violation'] = stop_violation_counter

            if (row.entry_long == True and row.long_profit_take < row.closePrice) or (row.entry_short and row.short_profit_take > row.closePrice):
                limit_violation_counter = limit_violation_counter+1
                self.df.loc[row[0],
                            'limit_violation'] = limit_violation_counter

    def set_notional_value(self, position_size: float = 1):
        if (self.df['instrument'].iloc[0] == 'AUDUSD'):
            self.notional_value = 10000*position_size
        elif (self.df['instrument'].iloc[0] == 'USDJPY'):
            # $10,000USD per point converted to AUD approx. $15k
            self.notional_value = 15000*position_size
        else:
            self.notional_value = 10000*position_size

    def print_stats(self, position_size: float = 1, margin_per_trade: float = 0.04):
        '''
        Description: Print simulation back test results to screen

        Args:
            notional_value (float): notional value of each trade
            margin_per_trade (float): margin % of each trade

        Returns:
            adds float column to dataframe 'hours_held' in class variable 'df'
        '''
        self.set_notional_value(position_size)
        self.add_more_stats()

        # Print trade level data
        print(self.df[['openPrice', 'lowPrice', 'highPrice', 'closePrice', 'entry_long', 'long_stop', 'long_profit_take', 'entry_short', 'short_stop',
                       'short_profit_take', 'sellDate', 'sellPrice', 'profit', 'drawdown', 'exit_long','exit_short','exit_reason', 'long_counter', 'short_counter']].to_string())

        # Output summary stats
        self.df['buyDate'] = pd.to_datetime(self.df['buyDate'])
        self.df['sellDate'] = pd.to_datetime(self.df['sellDate'])
        self.df['hours_held'] = (self.df['sellDate'] -
                                 self.df['buyDate']) / pd.Timedelta(hours=1)
        print(
            f"Notional value per trade ${self.notional_value}. I.e. without leverage.")
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
        print(f"\n----------------------------------------------------------------------------------------------------------------------")
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
        print(
            f"{round(self.df.groupby(self.df.exit_reason)['profit'].count(),1)}")
        account_balance_needed = self.get_account_balance_needed()
        print(
            f"Minimum account balance required ${account_balance_needed}")
        print(f"\n----------------------------------------------------------------------------------------------------------------------")
        self.df['number_of_trades'] = np.where(
            (self.df['profit'].abs() > 0), 1, 0)
        self.df['number_of_profitable_trades'] = np.where(
            (self.df['profit'] > 0), 1, 0)
        print(self.df.groupby(self.df['year']).apply(lambda s: pd.Series({
            "Trades": s["number_of_trades"].sum(),
            "Win rate (%)": round(s["number_of_profitable_trades"].sum()/s["number_of_trades"].sum() * 100, 1),
            "Max drawdown (%)": round(s["drawdown"].min()/account_balance_needed * 100 * -1, 1),
            "Max number of short held trades (#)": s['short_counter'].max(),
            "Max number of long held trades (#)": s['long_counter'].max(),
            "Return on capital (%)": round(s["profit"].sum()/account_balance_needed * 100, 1),
            "Trading capital ($)": round(account_balance_needed, 0),
            "Profit ($)": round(s["profit"].sum(), 0),
        })))
        self.set_model_score(position_size)
        self.print_violations()
        self.print_sharpe_ratio()
        print("\n")

    def get_max_holds(self) -> int:
        '''
        Description: Get the maximum number of positions held at any one time

        Args:
            None

        Returns:
            max_holds (int): maximum number of positions held at any one time
        '''
        if self.df['short_counter'].max() > self.df['long_counter'].max():
            max_holds = self.df['short_counter'].max()
        else:
            max_holds = self.df['long_counter'].max()
        return max_holds

    def get_account_balance_needed(self, position_size: float = 125, average_margin=0.005):
        max_holds = self.get_max_holds()
        account_balance_needed_max_holds = max_holds*position_size/average_margin
        account_balance_need_through_drawdown = abs(
            round(self.df['drawdown'].min(), 0))*2

        account_balance_need = account_balance_needed_max_holds + \
            account_balance_need_through_drawdown

        self.df['account_balance_need'] = account_balance_need
        return account_balance_need

    def print_violations(self):
        print("\n--- Starting violations ---")
        print(f"Stop price violation count {self.df['stop_violation'].sum()}")
        print(
            f"Limit price violation count {self.df['limit_violation'].sum()}")
        print("--- End scoring model ---")

    def print_sharpe_ratio(self):
        print("\n--- Starting Sharpe Ratio ---")
        avg_return = self.df['profit'].groupby(
            self.df['year']).sum()/self.df['account_balance_need'].max()
        total_avg_return = self.df['profit'].sum(
        )/self.df['account_balance_need'].max()
        num_years = len(list({i for i in self.df['year']}))
        annualised_return = pow((1+total_avg_return), 1/num_years)-1
        risk_free_return = 0.03
        std_profit = avg_return.std()
        sharpe_ratio = (annualised_return - risk_free_return) / std_profit
        print(f"Annualised return {round(annualised_return*100,2)}%")
        print(f"Risk free return {round(risk_free_return*100,2)}%")
        print(f"Standard deviation of profit {round(std_profit*100,2)}%")
        print(f"Sharpe ratio {round(sharpe_ratio,2)}")
        print("--- End Sharpe Ratio ---")

    def set_model_score(self, position_size):
        print("\n--- Starting scoring model ---")
        self.position_size = position_size
        self.win_rate = round((self.df[self.df.profit > 0].shape[0] /
                               self.df[abs(self.df.profit) > 0].shape[0]) * 100, 1)
        self.max_drawdown = self.df['drawdown'].min()
        self.max_profit_streak = self.df['profit_streak'].max()
        self.average_gain_weighted_to_1 = self.df['profit'].mean(
        )/position_size
        self.set_win_rate_score()
        self.set_drawdown_score()
        self.set_average_gain_score()
        self.set_monthly_profit_score()

        # Calculate final score
        self.calc_final_score()
        print("--- End scoring model ---")

    def set_monthly_profit_score(self) -> None:
        # Profit per month
        self.profit_per_month = self.df[['tmp_date', 'profit']].groupby(pd.Grouper(key='tmp_date', axis=0,
                                                                                          freq='ME')).sum()
        self.win_rate_per_month = round((self.profit_per_month[self.profit_per_month.profit > 0].shape[0] /
                                         self.profit_per_month[abs(self.profit_per_month.profit) > 0].shape[0]) * 100, 1)

        if self.win_rate_per_month > 90:
            self.win_rate_per_month_score = 5
        elif self.win_rate_per_month > 80:
            self.win_rate_per_month_score = 4
        elif self.win_rate_per_month > 70:
            self.win_rate_per_month_score = 3
        elif self.win_rate_per_month > 60:
            self.win_rate_per_month_score = 2
        elif self.win_rate_per_month > 50:
            self.win_rate_per_month_score = 1
        else:
            self.win_rate_per_month_score = -1
        print(
            f"{self.win_rate_per_month_score}: Monthly win rate score value {self.win_rate_per_month}%")

    def set_average_gain_score(self) -> None:
        # Average profit size weighted heaviest
        if self.average_gain_weighted_to_1 > 10:
            self.average_gain_score = 10
        elif self.average_gain_weighted_to_1 > 9:
            self.average_gain_score = 9
        elif self.average_gain_weighted_to_1 > 8:
            self.average_gain_score = 8
        elif self.average_gain_weighted_to_1 > 7:
            self.average_gain_score = 7
        elif self.average_gain_weighted_to_1 > 6:
            self.average_gain_score = 6
        elif self.average_gain_weighted_to_1 > 5:
            self.average_gain_score = 5
        elif self.average_gain_weighted_to_1 > 4:
            self.average_gain_score = 4
        elif self.average_gain_weighted_to_1 > 3:
            self.average_gain_score = 3
        elif self.average_gain_weighted_to_1 > 2:
            self.average_gain_score = 2
        elif self.average_gain_weighted_to_1 > 1:
            self.average_gain_score = 1
        else:
            self.average_gain_score = -1
        print(
            f"{self.average_gain_score}: Average gain score for value ${round(self.average_gain_weighted_to_1,0)}")

    def set_win_rate_score(self) -> None:
        # Win rate
        if self.win_rate > 90:
            self.win_rate_score = 5
        elif self.win_rate > 80:
            self.win_rate_score = 4
        elif self.win_rate > 70:
            self.win_rate_score = 3
        elif self.win_rate > 60:
            self.win_rate_score = 2
        elif self.win_rate > 50:
            self.win_rate_score = 1
        else:
            self.win_rate_score = -1
        print(
            f"{self.win_rate_score}: Win rate score for value {self.win_rate}%")

    def set_drawdown_score(self) -> None:
        # Largest profit streak divided by max drawdown
        profit_drawdown_ratio = abs(
            self.max_profit_streak)/abs(self.max_drawdown)
        if profit_drawdown_ratio >= 3:
            self.drawdown_score = 3
        elif profit_drawdown_ratio >= 2:
            self.drawdown_score = 2
        elif profit_drawdown_ratio >= 1.5:
            self.drawdown_score = 1.5
        elif profit_drawdown_ratio >= 1:
            self.drawdown_score = 1
        else:
            self.drawdown_score = -1
        print(
            f"{self.drawdown_score}: Profit/drawdown ratio score for value {round(profit_drawdown_ratio,1)}")

    def calc_final_score(self) -> None:
        self.final_score = self.win_rate_score + \
            self.drawdown_score + self.average_gain_score + self.win_rate_per_month_score
        print(f"{self.final_score}: Final model score")
