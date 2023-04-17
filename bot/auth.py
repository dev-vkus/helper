import aiohttp
from config.conf import Config
from pyrus import client
from aiohttp.client_exceptions import ContentTypeError
from logger.logger import Logger
import requests
import jwt


class PyrusApi:
    def __init__(self):
        cfg = Config()
        pyrus_client = client.PyrusAPI(login=cfg.pyrus, security_key=cfg.key)
        response = pyrus_client.auth()
        self.access = response.access_token


async def update_tokens(**kwargs) -> dict:
    cfg = Config()
    logger = Logger('post_auth')
    data = {
        'grant_type': 'refresh_token',
        'redirect_uri': cfg.redirect,
        'code_verifier': cfg.verifier,
        'refresh_token': kwargs['refresh']
    }
    headers = {
        "user-agent": 'DodoVkus',
        "Content-Type": "application/x-www-form-urlencoded",
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(kwargs['url'], headers=headers, data=data, allow_redirects=False,
                                auth=aiohttp.BasicAuth(cfg.client, cfg.secret)) as response:
            try:
                response = await response.json()
                logger.info(f'OK post_auth {kwargs["url"]} {response}')
                return response
            except ContentTypeError:
                logger.error(f'ERROR post_auth {kwargs["url"]}{response}')
                return {}


async def get_units(**kwargs) -> dict:
    headers = {
        "user-agent": "DodoVkus",
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Bearer {kwargs['access']}"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.dodois.io/auth/roles/units',
                               headers=headers) as response:
            try:
                response = await response.json()
                return response
            except ContentTypeError:
                return {}


async def get_tokens(code):
    cfg = Config()
    data = {
        'client_id': cfg.client,
        'client_secret': cfg.secret,
        'scope': cfg.scope,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': cfg.redirect,
        'code_verifier': cfg.verifier
    }
    header = {
        "Content-Type": "application/x-www-form-urlencoded",
        "user-agent": 'DodoVkus',
    }
    response = requests.post('https://auth.dodois.io/connect/token', data=data, allow_redirects=False,
                             headers=header)
    tokens = response.json()
    access_token = tokens['access_token']
    refresh_token = tokens['refresh_token']
    jw = jwt.decode(tokens['id_token'], options={"verify_signature": False})
    sub = jw['sub']
    return access_token, refresh_token, sub


async def get_public_api(url) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            try:
                response = await response.json()
                return response
            except ContentTypeError:
                return {}


async def pyrus_api(url, *args):
    pyrus = PyrusApi()
    headers = {
        "Authorization": f'Bearer {pyrus.access}',
        "Content-Type": "application/json",
        "user-agent": 'DodoVkus'
    }
    async with aiohttp.ClientSession() as session:
        if args:
            async with session.post(url, json=args[0], headers=headers) as response:
                try:
                    response = await response.json()
                    return response
                except ContentTypeError:
                    return {}
        else:
            async with session.get(url, headers=headers) as response:
                try:
                    response = await response.json()
                    return response
                except ContentTypeError:
                    return {}
