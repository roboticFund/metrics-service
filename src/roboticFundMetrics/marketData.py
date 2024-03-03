import pandas
import requests
from datetime import datetime
import os
from .dbConnect import dbConnect


class MarketData:

    def __init__(self):
        pass

    def return_market_data_from_db(self, instrument: str, resolution: str, from_date: str = '2000-01-01', to_date: str = '2050-01-01') -> pandas.DataFrame:
        '''
        Description: returns market data from local or remote db

        Args:
            instrument (string): name of instrument, i.e, AUDUSD
            resolution (string): MINUTE_15, MINUTE_30, DAY
            from_date (string): '2000-01-01'
            to_date (string): '2000-01-01'

        Returns:
            pandas dataframe with market data
        '''
        # Connect to database
        con = dbConnect()

        # Load data from roboticfund DB
        market_data = pandas.read_sql(
            f"Select * from market_data where instrument = '{instrument}' and resolution = '{resolution}' and datetime >= '{from_date}' and datetime <= '{to_date}' order by datetime desc", con)

        return market_data

    def return_eod_market_data_from_EOD(self, instrument: str, exchange: str = 'AU', from_date='2000-01-01', to_date='2024-12-31') -> pandas.DataFrame:
        '''
        Description: returns end of the day market data from EOD historical API

        Args:
            instrument (string): name of instrument, i.e, AUDUSD
            resolution (string): MINUTE_15, MINUTE_30, DAY
            from_date (string): '2000-01-01'
            to_date (string): '2000-01-01'

        Returns:
            pandas dataframe with market data
        '''
        # EOD Historical
        url = f"https://eodhd.com/api/eod/{instrument}.{exchange}?period=d&api_token={os.getenv('EOD_API_KEY')}&fmt=json&from={from_date}&to={to_date}"
        response = requests.get(url).json()
        market_data = pandas.DataFrame.from_dict(response)
        market_data = market_data.rename(columns={
            'date': 'snapshotTimeUTC', 'open': 'openPrice', 'high': 'highPrice', 'low': 'lowPrice', 'close': 'closePrice', 'volume': 'volume'})
        market_data = market_data.drop(['adjusted_close'], axis=1)
        market_data['instrument'] = instrument
        market_data['datetime'] = market_data['snapshotTimeUTC']
        market_data['snapshotTimeUTC'] = pandas.to_datetime(
            market_data['snapshotTimeUTC'])
        market_data['insertStamp'] = datetime.now()
        market_data['resolution'] = "DAY"

        return market_data

    def return_intraday_market_data_from_EOD(self, instrument: str, resolution: str, exchange: str = 'AU', from_date: str = '2000-01-01', to_date: str = '2024-12-31') -> pandas.DataFrame:
        '''
        Description: returns intraday market data from EOD historical API

        Args:
            instrument (string): name of instrument, i.e, AUDUSD
            resolution (string): 15m, 30m, d
            from_date (string): '2000-01-01'
            to_date (string): '2000-01-01'

        Returns:
            pandas dataframe with market data
        '''
        # Set market data parameters
        myformat = "%Y-%m-%d"
        start_date = datetime.strptime(from_date, myformat)
        from_utc = start_date.strftime("%s")
        end_date = datetime.strptime(to_date, myformat)
        to_utc = end_date.strftime("%s")

        # EOD Historical
        url = f"https://eodhd.com/api/intraday/{instrument}.{exchange}?interval={resolution}&api_token={os.getenv('EOD_API_KEY')}&fmt=json&from={from_utc}&to={to_utc}"
        response = requests.get(url).json()
        market_data = pandas.DataFrame.from_dict(response)
        market_data = market_data.rename(columns={
            'datetime': 'snapshotTimeUTC', 'open': 'openPrice', 'high': 'highPrice', 'low': 'lowPrice', 'close': 'closePrice', 'volume': 'volume'})
        market_data['instrument'] = instrument
        market_data['datetime'] = market_data['snapshotTimeUTC']
        market_data['snapshotTimeUTC'] = pandas.to_datetime(
            market_data['snapshotTimeUTC'])
        market_data['insertStamp'] = datetime.now()
        market_data['resolution'] = resolution.upper()
        market_data = market_data[market_data['openPrice'].notna()]
        return market_data
