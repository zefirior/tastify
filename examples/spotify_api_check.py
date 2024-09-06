import logging
import pathlib

import requests

from tastify.core.log import configure_logging

HOME = pathlib.Path.home()

logger = logging.getLogger(__name__)
configure_logging()


if __name__ == '__main__':
    headers = {
        "Authorization": f"Bearer {"<token>"}"
    }
    response = requests.get(
        'https://api.spotify.com/v1/me',
        headers=headers,
    )
    response.raise_for_status()
    print(response.json())

    # spotify_client = SpotifyClient()

    # print(spotify_client.open_authorize_url())
    # print(spotify_client.get_user_token())

    # UserTokenData(access_token='<token>', token_type='Bearer', scope='user-library-read user-library-modify', refresh_token='<refresh_token>', expires_at=1724549452)
