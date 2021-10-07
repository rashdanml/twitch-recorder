# Imports
import requests
import time
import json
import random
import socket
import urllib3
import configparser as cp


class Config():
    def __init__(self):
        self.conf = cp.ConfigParser()
        self.conf.read('config.ini')

        self.clientid = self.conf['DEFAULT']['clientid']
        self.clientsecret = self.conf['DEFAULT']['clientsecret']
        self.oauthtoken = self.conf['DEFAULT']['oauthtoken']

    def validate(self, try_number=1):
        self.conf.read('config.ini')
        self.oauthtoken = self.conf['DEFAULT']['oauthtoken']

        validate_url = "https://id.twitch.tv/oauth2/validate"
        valid_headers = {'client-id': self.clientid, 'Authorization': 'OAuth ' + self.oauthtoken}

        try:
            valid = requests.get(validate_url, headers=valid_headers).json()
        except (requests.exceptions.ConnectionError, json.decoder.JSONDecodeError, urllib3.exceptions.MaxRetryError, urllib3.exceptions.NewConnectionError, socket.gaierror):
            time.sleep(15)
            return self.validate(self, try_number=try_number+1)
        else:
            return valid

    def refresh(self, try_number=1):
        auth_url = "https://id.twitch.tv/oauth2/token"
        auth_params = {'client_id': self.clientid, 'client_secret': self.clientsecret,
                       'grant_type': 'client_credentials'}

        try:
            key = requests.post(auth_url, params=auth_params).json()
        except (requests.exceptions.ConnectionError, json.decoder.JSONDecodeError, urllib3.exceptions.MaxRetryError, urllib3.exceptions.NewConnectionError, socket.gaierror):
            time.sleep(15)
            return self.refresh(self, try_number=try_number+1)
        else:
            self.oauthtoken = key['access_token']
            self.conf['DEFAULT']['oauthtoken'] = self.oauthtoken

            with open('config.ini', 'w') as file:
                self.conf.write(file)

            file.close()
            return key


conf = Config()
