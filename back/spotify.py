import spotipy
from pydantic_settings import BaseSettings
from spotipy.oauth2 import SpotifyClientCredentials


class SpotifySettings(BaseSettings):
    client_id: str = 'placeholder'
    secret_id: str = 'placeholder'

    class Config:
        env_prefix = 'SPOTIFY_'


spotify_settings = SpotifySettings()


spotify_api = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=spotify_settings.client_id,
        client_secret=spotify_settings.secret_id,
    )
)
