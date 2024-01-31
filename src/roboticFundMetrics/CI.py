import requests
import boto3
from .utils.market_id_resolver import Broker_Id_Resolver
from .dbConnect import dbConnect
import datetime
import pandas


class CI:

    content_type = "application/json; charset=UTF-8"
    accept = "application/json; charset=UTF-8"
    access_token = ""
    ci_url = "https://ciapi.cityindex.com/TradingAPI"

    def __init__(self):
        self.secret_name = "ci-robotic-fund"
        self.get_secret_from_aws()
        self.connect()

    def get_secret_from_aws(self):
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager', region_name="ap-southeast-2")
        get_secret_value_response = client.get_secret_value(
            SecretId=self.secret_name
        )
        secrets = eval(get_secret_value_response['SecretString'])
        self.account_id = secrets['account_id']
        self.api_key = secrets['api_key']
        self.password = secrets['password']

    def set_headers(self, access_token=None):
        self.headers = {
            "Username": self.account_id,
            "Content-type": "application/json",
            "Session": access_token
        }

    def connect(self):
        r = requests.post(
            f'{self.ci_url}/session', json={"UserName": self.account_id, "Password": self.password, "AppVersion": "1", "AppComments": "", "AppKey": self.api_key}, headers={"Version": "3", "Content-Type": self.content_type, "Accept": self.accept})
        print(f"CI connect attempt REST response code {r.status_code}")
        response = r.json()
        self.set_headers(response['Session'])

    def get_latest_price(self, market_name) -> float:
        print(f"Getting latest price from CI for {market_name}")
        epic = Broker_Id_Resolver(market_name).return_ci_epic()
        print(f"CI market id for {market_name} is {epic}")
        r = requests.get(
            f"{self.ci_url}/market/{epic}/barhistory?interval=MINUTE&span=1&PriceBars=1&priceType=ASK", headers=self.headers)
        response_json = r.json()
        latest_price = response_json['PriceBars'][0]['Close']
        print(f"latest price is {latest_price}")
        return latest_price

    def market_search(self, market_name):
        r = requests.get(
            f"{self.ci_url}/market/search?SearchByMarketName=TRUE&Query={market_name}&MaxResults=10", headers=self.headers)
        response_json = r.json()
        print(response_json)

    def get_market_data_history(self, market_name, year=2023, month=1):
        print(
            f"Getting market data history from CI for {market_name} for year {year} and month {month}")
        epic = Broker_Id_Resolver(market_name).return_ci_epic()
        print(f"CI market id for {market_name} is {epic}")
        from_date = datetime.date(year, month, 1).strftime("%s")
        to_date = datetime.date(year, month+1, 1).strftime("%s")
        r = requests.get(
            f"{self.ci_url}/market/{epic}/barhistorybetween?interval=MINUTE&span=15&fromTimestampUTC={from_date}&toTimestampUTC={to_date}", headers=self.headers)
        response_json = r.json()
        market_data = pandas.DataFrame.from_dict(response_json['PriceBars'])
        market_data['BarDateUTCNumber'] = market_data['BarDate'].str.extract(
            '(\d+)')
        market_data['snapshotTimeUTC'] = pandas.to_datetime(
            market_data['BarDateUTCNumber'], utc=True, unit='ms').dt.round('5min')
        market_data = market_data.rename(columns={
                                         'Open': 'openPrice', 'High': 'highPrice', 'Low': 'lowPrice', 'Close': 'closePrice', 'volume': 'volume'})
        market_data['instrument'] = market_name
        market_data['datetime'] = market_data['snapshotTimeUTC']
        market_data['insertStamp'] = datetime.datetime.now()
        market_data['resolution'] = "15M"
        market_data = market_data[market_data['openPrice'].notna()]
        market_data = market_data.set_index('snapshotTimeUTC')
        print(market_data.head())
        # Drop unwanted columns
        market_data = market_data.drop(
            ['BarDateUTCNumber', 'BarDate'], axis=1)

        return market_data

    def store_market_data_history_in_db(instrument, market_name, year=2023):
        con = dbConnect()
        df = pandas.DataFrame()
        for i in range(1, 12):
            market_data = ci.get_market_data_history(
                market_name, year=year, month=i)
            df = pandas.concat([df, market_data], axis=0)

        df = df.drop_duplicates(
            subset=['instrument', 'resolution', 'datetime'])
        df.to_sql('market_data', con, if_exists='append')
