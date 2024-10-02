import base64
import datetime
import json
import logging
import pathlib
import random
import string
import time
import webbrowser
from datetime import timedelta
from functools import lru_cache
from pydantic.dataclasses import dataclass

import requests

from tastify.core.integration.spotify.models.search import SearchResponse
from tastify.core.integration.spotify.models.user_tracks import UserTracks

HOME = pathlib.Path.home()
SPOTIFY_TOKEN_PATH = HOME / '.tastify' / 'token'
SPOTIFY_USER_TOKEN_PATH = HOME / '.tastify' / 'user_token'
SPOTIFY_SECRET_PATH = HOME / '.tastify' / 'secrets'
SPOTIFY_HOST = "https://accounts.spotify.com"
SPOTIFY_API_HOST = "https://api.spotify.com/v1"

logger = logging.getLogger(__name__)


@dataclass
class TokenData:
    access_token: str
    token_type: str
    expires_at: datetime.datetime

    def is_expired(self):
        return self.expires_at < datetime.datetime.now(datetime.UTC)


@dataclass
class UserTokenData:
    access_token: str
    token_type: str
    scope: str
    refresh_token: str
    expires_at: datetime.datetime

    def is_expired(self):
        return self.expires_at < datetime.datetime.now(tz=datetime.UTC)


def generate_random_string(length: int) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


class SpotifyClient:
    API_URL = f'{SPOTIFY_HOST}/api'
    PERMISSION_SCOPE = 'user-library-read user-library-modify'
    REGISTER_CALLBACK = '/register-spotify/'
    REDIRECT_URL = f'http://tastify.zefirior.com{REGISTER_CALLBACK}'

    def search_artists(self, query: str, limit: int = 10):
        response = self._client_request(
            '/search',
            params={
                'q': query,
                'type': 'artist',
                'limit': limit,
            },
        )
        return SearchResponse(**response.json())

    def search_artist_tracks(self, query: str, artist_name: str, limit: int = 10):
        response = self._client_request(
            '/search',
            params={
                'q': query + f' artist:"{artist_name}"',
                'type': 'track',
                'limit': limit,
            },
        )
        return SearchResponse(**response.json())

    def get_user_tracks(self, token_data: UserTokenData):
        response = self._client_request('/me/tracks', token=token_data)
        return [item.track for item in UserTracks(**response.json()).items]

    def build_authorize_url(self, state: str = None):
        state = state or generate_random_string(16)
        client_data = self._get_client_data()

        logger.info(f'SpotifyClient.authorize with {state}')
        r = requests.Request(
            'GET',
            f'{SPOTIFY_HOST}/authorize',
            params={
                'client_id': client_data['client_id'],
                'response_type': 'code',
                'redirect_uri': "http://tastify.zefirior.com/register-spotify/",
                'state': state,
                'scope': self.PERMISSION_SCOPE,
            }
        )
        return r.prepare().url

    def open_authorize_url(self):
        authorize_url = self.build_authorize_url()
        webbrowser.open_new_tab(authorize_url)

    def get_user_token(self, code: str) -> UserTokenData:
        client_data = self._get_client_data()
        client_auth = base64.b64encode(f'{client_data["client_id"]}:{client_data["client_secret"]}'.encode()).decode()

        response = requests.post(
            f'{self.API_URL}/token',
            params={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': self.REDIRECT_URL,
            },
            headers={
                "Authorization": f"Basic {client_auth}",
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )

        if response.status_code != 200:
            logger.error(response.text)
            response.raise_for_status()
        token_data = response.json()

        return UserTokenData(
            access_token=token_data['access_token'],
            token_type=token_data['token_type'],
            scope=token_data['scope'],
            expires_at=datetime.datetime.now(tz=datetime.UTC) + timedelta(seconds=token_data['expires_in']),
            refresh_token=token_data['refresh_token'],
        )

    def get_internal_token(self) -> TokenData:
        logger.info('SpotifyClient.get_internal_token')

        if not SPOTIFY_TOKEN_PATH.exists():
            self._refresh_token()
        token_data = self._read_token()
        if token_data.is_expired():
            self._refresh_token()
            return self._read_token()
        else:
            return token_data

    def _client_request(self, route: str, method: str = 'GET', token = None,  **kwargs):
        token = token or self.get_internal_token()
        logger.info(f'calling {method} {route} with params {kwargs}')
        response = requests.request(
            method,
            f'{SPOTIFY_API_HOST}{route}',
            headers={
                'Authorization': f'{token.token_type} {token.access_token}',
            },
            **kwargs,
        )
        if response.status_code != 200:
            logger.error(response.text)
            response.raise_for_status()
        return response

    @staticmethod
    def _read_token() -> TokenData:
        with open(SPOTIFY_TOKEN_PATH) as f:
            data = json.load(f)
            return TokenData(
                access_token=data['access_token'],
                token_type=data['token_type'],
                expires_at=datetime.datetime.fromisoformat(data['expires_at']),
            )

    def _refresh_token(self):
        token_data = self._get_token()
        with open(SPOTIFY_TOKEN_PATH, 'w') as f:
            json.dump(dict(
                access_token=token_data.access_token,
                token_type=token_data.token_type,
                expires_at=token_data.expires_at.isoformat(),
            ), f)
        logger.info('Spotify token refreshed')

    def _get_token(self) -> TokenData:
        client_data = self._get_client_data()
        response = requests.post(
            f'{self.API_URL}/token',
            data={
                'grant_type': 'client_credentials',
                'client_id': client_data['client_id'],
                'client_secret': client_data['client_secret'],
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )
        response.raise_for_status()
        token_data = response.json()

        return TokenData(
            access_token=token_data['access_token'],
            token_type=token_data['token_type'],
            expires_at=token_data['expires_in'] + int(time.time()),
        )

    @lru_cache()
    def _get_client_data(self):
        logger.info('SpotifyClient._get_client_data')
        with open(SPOTIFY_SECRET_PATH) as f:
            return json.load(f)

