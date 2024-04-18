import boto3
import requests
from .utils.market_id_resolver import Broker_Id_Resolver


class IG:

    content_type = "application/json; charset=UTF-8"
    accept = "application/json; charset=UTF-8"

    def __init__(self, secret_name):
        self.secret_name = secret_name
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
        self.url = secrets['url']

    def set_headers(self):
        self.headers = {
            "Version": "3",
            "Content-Type": self.content_type,
            "Accept": self.accept,
            "X-IG-API-KEY": self.api_key,
            "Authorization": f"Bearer {self.access_token}",
            "IG-ACCOUNT-ID": self.cfd_account_id
        }

    def connect(self):
        print(f"Attempting to connect to IG Account {self.account_id}")
        r = requests.post(
            f"{self.url}/session", json={
                "identifier": self.account_id,
                "password": self.password
            }, headers={"Version": "3", "Content-Type": self.content_type, "Accept": self.accept, "X-IG-API-KEY": self.api_key})
        print(f"IG connect attempt REST response code {r.status_code}")
        response = r.json()
        self.access_token = response['oauthToken']['access_token']
        self.cfd_account_id = response['accountId']
        self.set_headers()

    def get_latest_offer_price(self, market_name) -> float:
        epic = Broker_Id_Resolver(market_name).return_ig_epic()
        print(f"Getting latest price from IG for {epic}")
        r = requests.get(
            f"{self.url}/markets/{epic}", headers=self.headers)
        print(f"IG fetch price REST response code {r.status_code}")
        response_json = r.json()
        return response_json['snapshot']['offer']
