import os
from sqlalchemy import create_engine
import boto3


class db_secret:
    def __init__(self, host, user, password) -> None:
        self.host = host
        self.user = user
        self.password = password
        self.database = "main"
        self.port = 3306


def get_secrets() -> db_secret:
    secret_name = "trading-db-secret"
    region_name = "ap-southeast-2"

    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager',region_name=region_name)
    get_secret_value_response = client.get_secret_value(
        SecretId=secret_name
    )

    secrets = eval(get_secret_value_response['SecretString'])
    return db_secret(secrets['host'],secrets['username'],secrets['password'])


def dbConnect():
    if (os.environ.get("ENV").lower() == "dev"):
        print('Connecting to local DB...')
        host=os.environ.get('DB_HOST')
        user=os.environ.get('DB_USER')
        password=os.environ.get('DB_PASSWORD')
        database=os.environ.get('DB_SCHEMA')
        db_connection_str = f'mysql+pymysql://{user}:{password}@{host}/{database}'
        return create_engine(db_connection_str)

    else:
        print('Connecting to remote DB...')
        db = get_secrets()
        db_connection_str = f'mysql+pymysql://{db.user}:{db.password}@{db.host}/{db.database}'
        return create_engine(db_connection_str)
