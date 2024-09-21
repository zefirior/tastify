import base64
import json
import logging
import pathlib
import random
import string
import time
import webbrowser
from datetime import datetime, timezone, timedelta
from functools import lru_cache
from pydantic.dataclasses import dataclass

import requests
from reflex import serializer

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
    expires_at: datetime

    def is_expired(self):
        return self.expires_at < time.time()


@dataclass
class UserTokenData:
    access_token: str
    token_type: str
    scope: str
    refresh_token: str
    expires_at: datetime

    def is_expired(self):
        return self.expires_at < datetime.now(tz=timezone.utc)


@dataclass
class Artist:
    id: str
    name: str


@serializer
def artist_to_dict(self: Artist):
    return {
        'id': self.id,
        'name': self.name,
    }


@dataclass
class AlbumImage:
    url: str
    height: int
    width: int


@serializer
def image_to_dict(self: AlbumImage):
    return {
        'url': self.url,
        'height': self.height,
        'width': self.width,
    }


@dataclass
class Album:
    id: str
    name: str
    images: list[AlbumImage]

    def get_smallest_image(self):
        return min(self.images, key=lambda x: x.height)


@serializer
def album_to_dict(self: Album):
    return {
        'id': self.id,
        'name': self.name,
        'images': [image_to_dict(i) for i in self.images],
    }


@dataclass
class UserTrack:
    # TODO: separate into model and domain
    id: str
    name: str
    popularity: int
    preview_url: str | None
    album: Album
    artists: list[Artist]

    def get_artists(self):
        # TODO: fix using foreach
        return ' feat '.join(*[a.name for a in self.artists])


@serializer
def track_to_dict(self: UserTrack):
    return {
        'id': self.id,
        'name': self.name,
        'popularity': self.popularity,
        'preview_url': self.preview_url,
        'album': album_to_dict(self.album),
        'artists': [artist_to_dict(a) for a in self.artists],
    }


@dataclass
class UserTrackItem:
    track: UserTrack


@dataclass
class UserTracks:
    next: str
    offset: int
    total: int
    items: list[UserTrackItem]


def generate_random_string(length: int) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


class SpotifyClient:
    API_URL = f'{SPOTIFY_HOST}/api'
    PERMISSION_SCOPE = 'user-library-read user-library-modify'
    REGISTER_CALLBACK = '/register-spotify/'
    REDIRECT_URL = f'http://tastify.zefirior.com{REGISTER_CALLBACK}'

    def get_user_tracks(self, token_data: UserTokenData):
        response = requests.get(
            f'{SPOTIFY_API_HOST}/me/tracks',
            headers={
                'Authorization': f'{token_data.token_type} {token_data.access_token}',
            }
        )
        if response.status_code != 200:
            logger.error(response.text)
            response.raise_for_status()
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

    def authorize(self):
        """
        Authorize the app to access the user's Spotify account.
        link: https://developer.spotify.com/documentation/web-api/tutorials/code-flow
        """
        state = generate_random_string(16)
        client_data = self._get_client_data()

        logger.info(f'SpotifyClient.authorize with {state}')
        response = requests.get(
            f'{SPOTIFY_HOST}/authorize',
            params={
                'client_id': client_data['client_id'],
                'response_type': 'code',
                'redirect_uri': self.REDIRECT_URL,
                'state': state,
                'scope': self.PERMISSION_SCOPE,
            }
        )
        logger.info(f'SpotifyClient.authorize request: {response.url}')
        response.raise_for_status()
        return response.text

    def open_authorize_url(self):
        authorize_url = self.build_authorize_url()
        webbrowser.open_new_tab(authorize_url)

    def get_token(self, token_data: TokenData) -> TokenData:
        logger.info('SpotifyClient.get_internal_token')

        if not SPOTIFY_USER_TOKEN_PATH.exists():
            self._refresh_token()
        token_data = self._read_token()
        if token_data.is_expired():
            self._refresh_token()
            return self._read_token()
        else:
            return token_data

    def get_token_with_refresh(self, ) -> TokenData:
        logger.info('SpotifyClient.get_internal_token')

        if not SPOTIFY_USER_TOKEN_PATH.exists():
            self._refresh_token()
        token_data = self._read_token()
        if token_data.is_expired():
            self._refresh_token()
            return self._read_token()
        else:
            return token_data

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
            expires_at=datetime.now(tz=timezone.utc) + timedelta(seconds=token_data['expires_in']),
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

    def _read_token(self) -> TokenData:
        with open(SPOTIFY_TOKEN_PATH) as f:
            return TokenData(**json.load(f))

    def _refresh_token(self):
        token_data = self._get_token()
        with open(SPOTIFY_TOKEN_PATH, 'w') as f:
            json.dump(dataclasses.asdict(token_data), f)
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

