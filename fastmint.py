import json
import os
import time
from urllib.parse import parse_qs, unquote
import requests
from datetime import datetime


def print_(word):
    now = datetime.now().isoformat(" ").split(".")[0]
    print(f"[{now}] {word}")


class Fastmint():
    def __init__(self):
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://chaingn.org/",
            "Origin": "https://chaingn.org",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type":"application/json",
            "User-Agent" : "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
        }

    def make_request(self, method, url, header, data=None):
        retry_count = 0
        while True:
            time.sleep(2)
            if method.upper() == "GET":
                response = requests.get(url, headers=header, json=data)
            elif method.upper() == "POST":
                response = requests.post(url, headers=header, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=header, json=data)
            else:
                raise ValueError("Invalid method. Only GET, PUT and POST are supported.")
            if response.status_code >= 500:
                if retry_count >= 3:
                    print_(f"Status Code : {response.status_code} | {response.text}")
                    return None
                retry_count += 1
            elif response.status_code >= 400:
                print_(f"Status Code : {response.status_code} | {response.text}")
                return None
            elif response.status_code >= 200:
                return response
    
    def login(self, query):
        url = 'https://api.chaingn.org/auth/login'
        payload = {"OAuth": query}
        response = self.make_request('post', url, self.headers, payload)
        if response is not None:
            jsons = response.json()
            token = jsons.get('sessionToken', "")
            return token
    
    def user(self, token):
        url = 'https://api.chaingn.org/user'
        self.headers.update({
            'Authorization': f"Bearer {token}"
            })
        response = self.make_request('get', url, self.headers)
        if response is not None:
            jsons = response.json()
            return jsons
    
    def daily_checkin(self, token):
        url = 'https://api.chaingn.org/user/daily_visits'
        self.headers.update({
            'Authorization': f"Bearer {token}"
            })
        response = self.make_request('get', url, self.headers)
        if response is not None:
            jsons = response.json()
            return jsons

    def wallet(self, token):
        url = 'https://api.chaingn.org/wallets'
        self.headers.update({
            'Authorization': f"Bearer {token}"
            })
        response = self.make_request('get', url, self.headers)
        if response is not None:
            jsons = response.json()
            return jsons
    
    def claim_farming(self, token, id):
        url = "https://api.chaingn.org/wallet/claim"
        self.headers.update({
            'Authorization': f"Bearer {token}"
            })
        payload = {"id": id}
        response = self.make_request('post', url, self.headers, payload)
        if response is not None:
            jsons = response.json()
            return jsons
        
    def start_farming(self, token, id):
        url = "https://api.chaingn.org/wallet/farm"
        self.headers.update({
            'Authorization': f"Bearer {token}"
            })
        payload = {"id": id}
        response = self.make_request('post', url, self.headers, payload)
        if response is not None:
            jsons = response.json()
            return jsons
    
    def claim_ref(self, token):
        url = 'https://api.chaingn.org/referral/claim'
        self.headers.update({
            'Authorization': f"Bearer {token}"
            })
        payload = {}
        response = self.make_request('post', url, self.headers, payload)
        if response is not None:
            response
        
    def get_tasks(self, token):
        url = 'https://api.chaingn.org/sub_tasks'
        self.headers.update({
            'Authorization': f"Bearer {token}"
            })
        response = self.make_request('get', url, self.headers)
        if response is not None:
            jsons = response.json()
            return jsons
    
    def done_task(self, token, id):
        url = 'https://api.chaingn.org/sub_task'
        self.headers.update({
            'Authorization': f"Bearer {token}"
            })
        payload = {"recourceId": id}
        response = self.make_request('post', url, self.headers, payload)
        if response is not None:
            jsons = response.json()
            return jsons
    
    def complete_task(self, token, id):
        url = 'https://api.chaingn.org/sub_task/claim'
        self.headers.update({
            'Authorization': f"Bearer {token}"
            })
        payload = {"id": id}
        response = self.make_request('put', url, self.headers, payload)
        if response is not None:
            jsons = response.json()
            return jsons
    
    def check_external(self, token):
        url = 'https://api.chaingn.org/wallets/external'
        self.headers.update({
            'Authorization': f"Bearer {token}"
            })
        response = self.make_request('get', url, self.headers)
        if response is not None:
            jsons = response.json()
            return jsons
    
    def create_wallet(self, token):
        url = 'https://api.chaingn.org/wallet/external'
        self.headers.update({
            'Authorization': f"Bearer {token}"
            })
        payload = {}
        response = self.make_request('post', url, self.headers, payload)
        if response is not None:
            jsons = response.json()
            return jsons
    
    def validate_wallet(self, token, mnemonic):
        url = 'https://api.chaingn.org/wallet/external'
        self.headers.update({
            'Authorization': f"Bearer {token}"
            })
        payload = {"mnemonic": mnemonic}
        response = self.make_request('post', url, self.headers, payload)
        if response is not None:
            jsons = response.json()
            return jsons