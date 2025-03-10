import pytest
from litestar import Litestar
from litestar.testing import AsyncTestClient


def _get_spotify_track(id_, name, album, artists):
    return {
        'id': id_,
        'name': name,
        'album': {'name': album},
        'artists': [{'name': a} for a in artists],
    }


@pytest.mark.asyncio
async def test_search_tracks(test_client: AsyncTestClient[Litestar], spotify_client):
    spotify_client.search.return_value = {
        'tracks': {
            'items': [
                _get_spotify_track('sdfg24w', 'Dancing Queen', 'Arrival', ['ABBA']),
                _get_spotify_track('52wesfd', 'Dancing Queen', 'The best of', ['ABBA']),
                _get_spotify_track('24t35te', 'Dancing Queen', 'Mamma Mia! OST', ['Meryl Streep', 'Julie Walters']),
                _get_spotify_track('4765rjf', 'Gimme! Gimme! Gimme!', 'Voulez-Vous', ['ABBA']),
            ]
        }
    }

    response = await test_client.get('/search/track', params={'group_id': 'ABBA', 'q': 'Dancing'})
    assert response.status_code == 200, response.text

    assert response.json() == [
        {'id': 'sdfg24w', 'name': 'ABBA - Dancing Queen'},
        {'id': '4765rjf', 'name': 'ABBA - Gimme! Gimme! Gimme!'},
    ]
