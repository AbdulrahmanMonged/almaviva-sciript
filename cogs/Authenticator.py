import base64
import random
import secrets
import string
import requests
import hashlib
from .colors import *


def create_nonce():
    a = string.ascii_letters + string.digits + '-._~'
    A = 45
    y = ''
    try:
        crypto = __import__('crypto', fromlist=['getRandomValues'])
        if hasattr(crypto, 'getRandomValues'):
            S = crypto.getRandomValues(bytearray(A))
            y = ''.join((a[x % len(a)] for x in S))
    except ImportError:
        pass
    if not y:
        y = ''.join((random.choice(a) for _ in range(A)))
    return y

class Authenticator:

    def __init__(self, **kwargs):
        self._session = kwargs.get('session', requests.Session())
        self._headers = {'Accept': 'application/json, text/plain, */*', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}
        self.proxy = kwargs.get('proxy', None)
        self._config = kwargs.get('config', {})
        self._open_id_config = kwargs.get('open_id_config', {})
        self.window = kwargs.get('window', None)
        if not self._config:
            self.get_config_from_site()
        if not self._open_id_config:
            self.get_openid_config_from_site()
        self._state = secrets.token_urlsafe(60)
        self._nonce = secrets.token_urlsafe(60)
        self._code_verifier = secrets.token_urlsafe(43)
        self._code_challenge = base64.urlsafe_b64encode(hashlib.sha256(self._code_verifier.encode()).digest()).decode().replace('=', '')
        self._session_code = ''
        self._execution = ''
        self._tab_id = ''
        self._code = ''
        self.access_token = ''


    def set_proxy(self, proxy):
        self.proxy = proxy

    def get_config_from_site(self):
        api_url = 'https://egy.almaviva-visa.it/assets/config/config.json'
        if self.proxy:
            response = self._session.get(api_url, headers=self._headers, proxies=self.proxy)
        else:
            response = self._session.get(api_url, headers=self._headers)
        if response and response.status_code == 200:
            self._config = response.json()
        else:
            pass
    def get_openid_config_from_site(self):
        api_url = 'https://egyiam.almaviva-visa.it/realms/oauth2-visaSystem-realm-pkce/.well-known/openid-configuration'
        if self.proxy:
            response = self._session.get(api_url, headers=self._headers, proxies=self.proxy)
        else:
            response = self._session.get(api_url, headers=self._headers)
        if response and response.status_code == 200:
            self._open_id_config = response.json()
        else:
            pass
    def _auth(self):
        api_url = f"{self._open_id_config['authorization_endpoint']}?client_id={self._config['environment']['authConfigClientId']}&response_type={self._config['environment']['authConfigResponseType']}&scope={self._config['environment']['authConfigScope']}&redirect_uri={self._config['environment']['authConfigRedirectUri']}&state={self._state}&code_challenge={self._code_challenge}&code_challenge_method=S256&nonce={self._nonce}"
        if self.proxy:
            response = self._session.get(api_url, headers=self._headers, proxies=self.proxy)
        else:
            response = self._session.get(api_url, headers=self._headers)
        if response and response.status_code == 200:
            self._session_code = response.text.split('session_code=')[1].split('&')[0]
            self._execution = response.text.split('execution=')[1].split('&')[0]
            self._tab_id = response.text.split('tab_id=')[1].split('&')[0]
        else:
            pass
    def _authenticate(self, username, password):
        api_url = f"https://egyiam.almaviva-visa.it/realms/oauth2-visaSystem-realm-pkce/login-actions/authenticate?session_code={self._session_code}&execution={self._execution}&client_id={self._config['environment']['authConfigClientId']}&tab_id={self._tab_id}"
        headers = self._headers
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        data = {'username': username, 'password': password, 'credentialId': ''}
        if self.proxy:
            response = self._session.post(api_url, headers=headers, data=data, allow_redirects=False, proxies=self.proxy)
        else:
            response = self._session.post(api_url, headers=headers, data=data, allow_redirects=False)
        if response and response.status_code == 302:
            self._code = response.headers['Location'].split('code=')[1]
        else:
            pass
    def _get_token(self):
        api_url = 'https://egyiam.almaviva-visa.it/realms/oauth2-visaSystem-realm-pkce/protocol/openid-connect/token'
        headers = self._headers
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        headers['Origin'] = 'https://egy.almaviva-visa.it'
        headers['Referer'] = 'https://egy.almaviva-visa.it/'
        data = {'grant_type': 'authorization_code', 'code': self._code, 'redirect_uri': 'https://egy.almaviva-visa.it/', 'code_verifier': self._code_verifier, 'client_id': self._config['environment']['authConfigClientId']}
        if self.proxy:
            response = self._session.post(api_url, headers=headers, data=data, proxies=self.proxy)
        else:
            response = self._session.post(api_url, headers=headers, data=data)
        if response and response.status_code == 200:
            self.window.print_in_log('تم تسجيل الدخول', color=success)
            self.access_token = response.json()['access_token']
        else:
            self.window.print_in_log('تعذر تسجيل الدخول', color=danger)

    def get_site_key(self):
        if not self._config:
            self.get_config_from_site()
        if self._config:
            return self._config['environment']['sitekey']

    def login_and_get_token(self, username, password):
        self._auth()
        self._authenticate(username, password)
        self._get_token()
        return self.access_token
    
if __name__ == '__main__':
    authenticator = Authenticator()
    token = authenticator.login_and_get_token('abdoomonged231@gmail.com', 'Aa23041622')
