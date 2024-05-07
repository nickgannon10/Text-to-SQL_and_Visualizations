"""
Azure Cache with Redis

References:

- [Azure Cache quickstart](https://learn.microsoft.com/en-us/azure/azure-cache-for-redis/cache-python-get-started)
- [Azure Cache with Entra ID](https://learn.microsoft.com/en-us/azure/azure-cache-for-redis/cache-azure-active-directory-for-authentication)
- [Code example](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/samples/azure-aad-auth-with-redis-py.md)
"""

import logging
import os

import azure.functions as func
import redis

# For auth via Entra ID
import time
from azure.identity import DefaultAzureCredential


def test_cache():
    cache_instance = Cache()  # Retrieve the singleton instance
    cache_instance.test()  # Call test on the instance


def singleton(cls):
    """Singleton class decorator by [PEP318](https://peps.python.org/pep-0318/#examples)"""
    instances = {}

    def get_instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return get_instance


@singleton
class Cache:
    """
    Azure Cache with Redis

    [Code example](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/samples/azure-aad-auth-with-redis-py.md)
    """

    @classmethod
    def test(cls):
        cache = cls()
        cache.set('key1', 'value1')
        test_value = cache.get('key1')
        logging.info(f'cache test value: {test_value}')

    def __init__(self):
        self._scope = "https://redis.azure.com/.default"
        self._host = os.getenv('REDIS-HOST', 'replay.redis.cache.windows.net')
        self._port = 6380
        self._user_name = os.getenv('FUNCTION_PRINCIPAL_ID')
        self._cred = DefaultAzureCredential()
        self._token = self._cred.get_token(self._scope)

        self._r = redis.Redis(
            host=self._host,
            port=self._port,
            ssl=True,  # ssl connection is required.
            username=self._user_name,
            password=self._token.token,
            decode_responses=True,
        )

    def set(self, *args, **kwargs):
        self._re_authenticate_if_needed()
        return self._r.set(*args, **kwargs)

    def get(self, *args, **kwargs):
        self._re_authenticate_if_needed()
        return self._r.get(*args, **kwargs)

    def _re_authenticate_if_needed(self):
        scope = self._scope
        token = self._token
        cred = self._cred
        user_name = self._user_name
        host = self._host
        port = self._port

        def _need_refreshing(token, refresh_offset=300):
            return not token or token.expires_on - time.time() < refresh_offset

        max_retry = 3
        for _ in range(max_retry):
            try:
                if _need_refreshing(self._token):
                    logging.info("Refreshing token...")
                    tmp_token = cred.get_token(scope)
                    if tmp_token:
                        token = tmp_token
                    self._r.execute_command("AUTH", user_name, token.token)
                    self._token = token
                    logging.info("Refreshed token.")
                else:
                    logging.info("Refresh token not needed.")
                break
            except redis.ConnectionError:
                logging.info("Connection lost. Reconnecting.")
                token = cred.get_token(scope)
                self._r = redis.Redis(
                    host=host,
                    port=port,
                    ssl=True,  # ssl connection is required.
                    username=user_name,
                    password=token.token,
                    decode_responses=True,
                )
                self._token = token
            except Exception as e:
                logging.info(f"Unknown failures: {repr(e)}")
                break


class CacheViaAccessKey:
    @classmethod
    def test(cls):
        cache = cls()
        cache.set('key1', 'value1')
        test_value = cache.get('key1')
        logging.info(f'CacheViaAccessKey test value: {test_value}')

    def __init__(self):
        """
        For local testing, since auth via identity only works in Azure environment.

        Need to setup local env var: REDIS_ACCESS_KEY
        """
        host = 'replay.redis.cache.windows.net'
        access_key = os.getenv('REDIS_ACCESS_KEY')
        if access_key:
            logging.info('Got REDIS_ACCESS_KEY')
        self._r = redis.StrictRedis(
            host=host, port=6380, db=0, password=access_key, ssl=True
        )

    def set(self, *args, **kwargs):
        return self._r.set(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self._r.get(*args, **kwargs)
