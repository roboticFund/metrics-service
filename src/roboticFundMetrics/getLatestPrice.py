import requests
import boto3


def get_eod_api_key():
    secret_name = 'eod-robotic-fund'
    region_name = "ap-southeast-2"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager', region_name=region_name)
    get_secret_value_response = client.get_secret_value(
        SecretId=secret_name
    )

    secrets = eval(get_secret_value_response['SecretString'])
    return secrets['api_key']


def get_latest_price(instrument, exchange='AU'):
    url = f"https://eodhd.com/api/real-time/{instrument}.{exchange}?api_token={get_eod_api_key()}&fmt=json"
    response = requests.get(url).json()
    return response['close']
