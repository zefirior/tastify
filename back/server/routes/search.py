from typing import Annotated

import spotipy
from litestar import get
from litestar.exceptions import HTTPException
from litestar.params import Dependency


@get('/search/group')
async def search_groups(spotify_client: Annotated[spotipy.Spotify, Dependency()], q: str) -> list:
    if not q:
        raise HTTPException(status_code=400, detail='Query cannot be empty')

    groups = []
    results = spotify_client.search(q=q, limit=10, type='artist')
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
async def search_tracks(spotify_client: Annotated[spotipy.Spotify, Dependency()], group_id: str, q: str) -> list:
    if not group_id:
        raise HTTPException(status_code=400, detail='Group ID cannot be empty')
    if not q:
        raise HTTPException(status_code=400, detail='Query cannot be empty')

    results = spotify_client.search(q=f'{group_id} - {q}', limit=50, type='track')

    tracks, seen = [], set()
    for track in results['tracks']['items']:
        if not any(group_id == a['name'] for a in track['artists']):
            continue

        if (name := f"{group_id} - {track['name']}") in seen:
            continue

        tracks.append({'id': track['id'], 'name': name})
        seen.add(name)

    return tracks
