import requests


class IG:

    content_type = "application/json; charset=UTF-8"
    accept = "application/json; charset=UTF-8"
    access_token = ""

    def __init__(self, secret_name):
        self.secret_name = secret_name
        self.account_id = "test"
        self.api_key = "to-do"
        self.connect()

    def set_headers(self, access_token=None):
        self.headers = {
            "Version": "3",
            "Content-Type": self.content_type,
            "Accept": self.accept,
            "X-IG-API-KEY": self.api_key,
            "Authorization": f"Bearer {access_token}",
            "IG-ACCOUNT-ID": self.account_id
        }

    def connect(self):
        # Connect with oAuth, POST /session v3
        # POST /session v3 returns OAuth access and refresh tokens which the user can pass in subsequent API requests via the Authorization header, e.g.:
        # Authorization : Bearer 5d1ea445-568b-4748-ab47-af9b982bfb74
        # The access token only identifies the client so users should also pass an IG-ACCOUNT-ID header to specify the account the request applies to, e.g.:
        # IG-ACCOUNT-ID : PZVI2
        # The access token is only valid for a limited period of time (e.g. 60 seconds) specified by the login response.
        #        "oauthToken": {
        #                "access_token": "702f6580-25c7-4c04-931d-6000efa824f8",
        #                "refresh_token": "a9cec2d7-fd01-4d16-a2dd-7427ef6a471d",
        #                "scope": "profile",
        #                "token_type": "Bearer",
        #                "expires_in": "60"
        #        }
        r = requests.post(
            'https://demo-api.ig.com/gateway/deal/session', json={
                "identifier": "to-do",
                "password": "to-do",
                "IG-ACCOUNT-ID": self.account_id
            }, headers={"Version": "3", "Content-Type": self.content_type, "Accept": self.accept, "X-IG-API-KEY": self.api_key})
        print(f"IG connect attempt REST response code {r.status_code}")
        response = r.json()
        self.set_headers(response['oauthToken']['access_token'])

    def get_latest_price(self, epic) -> float:
        print(f"Getting latest price from IG for {epic}")
        print(self.headers)
        r = requests.get(
            f"https://demo-api.ig.com/gateway/deal/prices/{epic}", headers=self.headers)
        response_json = r.json()
        print(response_json)


ig = IG("test")
ig.get_latest_price("AA.D.ANZ.CASH.IP")
