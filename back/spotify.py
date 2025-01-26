from pydantic_settings import BaseSettings
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


class SpotifySettings(BaseSettings):
    client_id: str = ''
    secret_id: str = ''

    class Config:
        env_prefix = 'SPOTIFY_'


spotify_settings = SpotifySettings()


spotify_api = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=spotify_settings.client_id or 'placeholder',
    client_secret=spotify_settings.secret_id or 'placeholder',
))
