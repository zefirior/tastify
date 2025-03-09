from litestar import get
from litestar.exceptions import HTTPException

from back.spotify import spotify_api


@get('/search/group')
async def search_groups(q: str) -> list:
    if not q:
        raise HTTPException(status_code=400, detail='Query cannot be empty')

    groups = []
    results = spotify_api.search(q=q, limit=10, type='artist')
    for artist in results['artists']['items']:
        if artist['images']:
            image_url = sorted(artist['images'], key=lambda image: image['height'])[0]['url']
        else:
            image_url = ''

        groups.append(
            {
                'name': artist['name'],
                'id': artist['id'],
                'image_url': image_url,
            }
        )

    return groups


@get('/search/track')
async def search_tracks(group_id: str, q: str) -> list:
    if not q:
        raise HTTPException(status_code=400, detail='Query cannot be empty')

    tracks = []
    results = spotify_api.search(q=f'{group_id} - {q}', limit=50, type='track')
    for track in results['tracks']['items']:
        if any(group_id == a['name'] for a in track['artists']):
            tracks.append(
                {
                    'id': track['id'],
                    'name': f"{group_id} - {track['name']} ({track['album']['name']})",
                }
            )

    return tracks
