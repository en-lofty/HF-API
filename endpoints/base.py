import json
import os
from datetime import datetime, timedelta

import requests
from pushbullet import Pushbullet, InvalidKeyError

from utilities.logger import log, exception

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/39.0.2171.95 Safari/537.36'}

data_file_name = "data.json"
config_file_name = "config.json"


class BaseEndpoint:
    """
    The base endpoint class with all default methods and variables.
    """
    API_URL = "https://{}:@hackforums.net/api/v1/{}/{}/"
    PB_URL = 'https://api.pushbullet.com/v2/{}'
    endpoint: str
    sleep_until: datetime = None
    _hf_api_key: str
    _pb_api_key: str
    _ready = False
    _using_pushbullet = False
    _session: requests.Session()
    data: dict = {}
    pb: Pushbullet
    if os.path.exists(config_file_name):
        with open(config_file_name, "r") as f:
            load_config = json.load(f)
        if "hf_key" in load_config:
            _hf_api_key = load_config["hf_key"]
            log("Loaded Hackforums API key from config.json")
        if "pb_key" in load_config:
            _pb_api_key = load_config["pb_key"]
            log("Loaded Pushbullet API key from config.json")

        _ready = True

    if os.path.exists(data_file_name):
        with open(data_file_name, "r") as f:
            data = json.load(f)

    @property
    def json(self):
        return BaseEndpoint.data

    @classmethod
    def save_data(cls):
        """
        This will save all of the forum data returns from Hackforums
        :return:
        """
        if len(cls.data) == 0:
            cls.data['threads'] = {}
            cls.data['inbox'] = {}
        with open(data_file_name, 'w') as file:
            json.dump(cls.data, file, indent=2)

    @classmethod
    def save_config(cls):
        """
        This will save api keys
        """
        config = {}
        if cls._hf_api_key:
            config["hf_key"] = cls._hf_api_key
        if cls._pb_api_key:
            config["pb_key"] = cls._pb_api_key
        with open(config_file_name, "w") as f:
            json.dump(config, f, indent=2)

    @classmethod
    def add_api(cls, hf_api, pb_api=None):
        if not cls._hf_api_key == hf_api:
            cls._hf_api_key = hf_api
            if cls.test_api():
                log("Your Hackforums API key has successfully been validated.")
                cls._ready = True
            else:
                raise Exception("The Hackforums API key validation test failed.")
        if pb_api and not cls._pb_api_key == pb_api:
            cls._pb_api_key = pb_api
            if cls.test_pushbullet():
                log("Your Pushbullet API key has successfully been validated")
            else:
                raise Exception("The Pushbullet API key validation test failed.")
        cls.save_config()

    @classmethod
    def test_api(cls) -> bool:
        log("Testing API key...")
        try:
            r = requests.get(cls.API_URL.format(cls._hf_api_key, "users", "2015410"), headers=headers)
            return r.json()["message"] != "INVALID_API_KEY"
        except Exception as e:
            exception(e)
            raise Exception("Unable to validate Hackforums API key.")

    @classmethod
    def test_pushbullet(cls) -> bool:
        log("Testing Pushbullet key...")
        try:
            cls.pb = Pushbullet(cls._pb_api_key)
            return True
        except Exception as e:
            exception(e)
            raise Exception("Pushbullet API key validation failed.")

    @classmethod
    def notify(cls):
        pass

    @classmethod
    def update(cls):
        """
        This will check the respective endpoint for changes and update the data if any changes are made
        :return:
        """
        if not cls._ready:
            raise Exception("Please enter your HackForms API key with BaseEndpoint.add_api() first.")
        elif not os.path.exists(data_file_name):
            cls.save_data()

    def api_query(self, id_=None):
        try:
            response = requests.get(self.API_URL.format(self._hf_api_key, self.endpoint, id_), headers=headers).json()
            if response["message"] == "MAX_HOURLY_CALLS_EXCEEDED":
                BaseEndpoint.sleep_until = datetime.now() + timedelta(minutes=10)
                return None
            return response
        except requests.exceptions.ConnectionError as ce:
            exception(ce)
        except json.decoder.JSONDecodeError:
            log("Unable to parse json")
        except Exception as e:
            exception(e)

    @classmethod
    def push_bullet(cls, method, options=None):
        if not cls._using_pushbullet:
            return
        headers_ = {"Access-Token": cls._pb_api_key}
        requests_url = cls.PB_URL.format(method)
        return requests.post(requests_url, headers=headers_, data=options).json()
