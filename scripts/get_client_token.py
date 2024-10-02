import logging
import pathlib

from tastify.core.integration.spotify.client import SpotifyClient
from tastify.core.log import configure_logging

HOME = pathlib.Path.home()

logger = logging.getLogger(__name__)
configure_logging()


if __name__ == '__main__':
    spotify_client = SpotifyClient()
    print(spotify_client.get_internal_token().access_token)
