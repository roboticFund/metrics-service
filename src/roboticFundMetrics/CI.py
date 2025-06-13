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
    ci_session_token: str

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
        self.ci_session_token = response['Session']

    def return_ci_resolution(self, resolution) -> str:
        if resolution == "MINUTE_10":
            return "10"
        elif resolution == "MINUTE_15":
            return "15"
        elif resolution == "MINUTE_30":
            return "30"
        else:
            return ""

    def get_latest_tick(self, market_name, resolution):
        print(
            f"Getting latest price from CI for {market_name} for resolution {resolution}")
        epic = Broker_Id_Resolver(market_name).return_ci_epic()
        print(f"CI market id for {market_name} is {epic}")
        ciRes = self.return_ci_resolution(resolution)
        r = requests.get(
            f"{self.ci_url}/market/{epic}/barhistory?interval=MINUTE&span={ciRes}&PriceBars=1&priceType=ASK", headers=self.headers)
        response_json = r.json()
        print(f"CI responded with this data {response_json}")
        market_data = pandas.DataFrame.from_dict(response_json['PriceBars'])
        if market_data.empty:
            return
        else:
            market_data['BarDateUTCNumber'] = market_data['BarDate'].str.extract(
                '(\d+)')
            market_data['snapshotTimeUTC'] = pandas.to_datetime(
                market_data['BarDateUTCNumber'], utc=True, unit='ms').dt.round('5min')
            market_data = market_data.rename(columns={
                'Open': 'openPrice', 'High': 'highPrice', 'Low': 'lowPrice', 'Close': 'closePrice', 'volume': 'volume'})
            market_data['instrument'] = market_name
            market_data['datetime'] = market_data['snapshotTimeUTC']
            market_data['insertStamp'] = datetime.datetime.now()
            market_data['resolution'] = resolution
            market_data = market_data[market_data['openPrice'].notna()]
            market_data = market_data.set_index('snapshotTimeUTC')

            # Drop unwanted columns
            market_data = market_data.drop(
                ['BarDateUTCNumber', 'BarDate'], axis=1)
            return market_data

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

    def get_market_data_history(self, market_name, resolution, year=2023, month=1):
        print(
            f"Getting market data history from CI for {market_name} for year {year} and month {month}")
        epic = Broker_Id_Resolver(market_name).return_ci_epic()
        print(f"CI market id for {market_name} is {epic}")
        if (month == 12):
            from_year = year
            to_year = year + 1
            from_month = 12
            to_month = 1
        else:
            from_month = month
            to_month = month+1
            from_year = year
            to_year = year

        from_date = datetime.date(from_year, from_month, 1).strftime("%s")
        to_date = datetime.date(to_year, to_month, 1).strftime("%s")

        r = requests.get(
            f"{self.ci_url}/market/{epic}/barhistorybetween?interval=MINUTE&span={resolution}&fromTimestampUTC={from_date}&toTimestampUTC={to_date}&priceType=ASK", headers=self.headers)
        response_json = r.json()
        market_data = pandas.DataFrame.from_dict(response_json['PriceBars'])
        if market_data.empty:
            pass
        else:
            market_data['BarDateUTCNumber'] = market_data['BarDate'].str.extract(
                '(\d+)')
            market_data['snapshotTimeUTC'] = pandas.to_datetime(
                market_data['BarDateUTCNumber'], utc=True, unit='ms').dt.round('5min')
            market_data = market_data.rename(columns={
                'Open': 'openPrice', 'High': 'highPrice', 'Low': 'lowPrice', 'Close': 'closePrice', 'volume': 'volume'})
            market_data['instrument'] = market_name
            market_data['datetime'] = market_data['snapshotTimeUTC']
            market_data['insertStamp'] = datetime.datetime.now()
            market_data['resolution'] = f"MINUTE_{resolution}"
            market_data = market_data[market_data['openPrice'].notna()]
            market_data = market_data.set_index('snapshotTimeUTC')

            # Drop unwanted columns
            market_data = market_data.drop(
                ['BarDateUTCNumber', 'BarDate'], axis=1)

            return market_data

    def get_one_year_data(self, market_name, resolution, year=2023):
        df = pandas.DataFrame()
        for i in range(1, 13):
            market_data = self.get_market_data_history(
                market_name, resolution, year=year, month=i)
            df = pandas.concat([df, market_data], axis=0)

        df = df.drop_duplicates(
            subset=['instrument', 'resolution', 'datetime'])

        return df

    def store_multiple_years_in_db(self, market_name, resolution, from_year=2022, to_year=2024):
        con = dbConnect()
        df = pandas.DataFrame()
        for i in range(from_year, to_year):
            market_data = self.get_one_year_data(market_name, resolution, i)
            df = pandas.concat([df, market_data], axis=0)

        df = df.drop_duplicates(
            subset=['instrument', 'resolution', 'datetime'])
        df.to_sql('market_data', con, if_exists='append')

    def delete_session(self) -> None:
        r = requests.post(
            f'{self.ci_url}/session/deleteSession?UserName={self.account_id}&Session={self.ci_session_token}', json={"UserName": self.account_id, "Session": self.ci_session_token, "AppVersion": "1", "AppComments": "", "AppKey": self.api_key}, headers={"Version": "3", "Content-Type": self.content_type, "Accept": self.accept})
        print(f"CI deleting session - {r.status_code}")


# instrument = "GOLD"
# resolution = "30"
# ci = CI()
# ci.store_multiple_years_in_db(
#     instrument, resolution, from_year=2015, to_year=2026)
# ci.delete_session()
# ci.get_latest_tick("US500", "MINUTE_15")
