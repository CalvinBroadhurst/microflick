import urequests
import json
from utime import sleep
import gc
from definitions import FLICK_PRICE_ENDPOINT
from urlencode import *

class Flick:
    _token = {}
    _expires = ""
    _client_id = ""
    _client_secret = ""
    _username = ""
    _password = ""


    def __init__(self, client_id, client_secret, username, password):
        print("init Flick")
        self._client_id = client_id
        self._client_secret = client_secret
        self._username = username
        self._password = password

    def authenticate(self):
        print("authenticate")
        gc.collect()
        sleep(1)
        payload = {
            "grant_type": "password",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "username": self._username,
            "password": self._password
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        try:
            print("try getting auth")
            sleep(1)
            req = urequests.post("https://api.flick.energy/identity/oauth/token", data=urlencode(payload), headers=headers)
            if req.status_code is not 200:
                print("error getting auth response")
                return False
            print("got auth response")
            self._token = json.loads(req.text)
            return True
        except:
            print("exception getting auth")
            sleep(1)

    def get_price_per_kwh(self):
        print("get price")
        gc.collect()
        headers = {
            "Authorization": "Bearer %s" % self._token["id_token"]
        }
        try:
            req = urequests.get(FLICK_PRICE_ENDPOINT, headers=headers)
            if req.status_code is not 200:
                print("error getting price data")
                return False
            print("got price response")
            response = json.loads(req.text)
            return response["needle"]["price"]
        except:
            print("exception getting price")
            return False

