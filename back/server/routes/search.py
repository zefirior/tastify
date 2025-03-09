from litestar import get

from back.spotify import spotify_api


@get('/search/group')
async def search_groups(q: str) -> list:
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
    artist = spotify_api.artist(group_id)
    tracks = []
    results = spotify_api.search(q=f'{q} artist:"{artist["name"]}"', limit=50, type='track')
    for track in results['tracks']['items']:
        if track['artists'][0]['id'] == group_id:
            tracks.append(
                {
                    'id': track['id'],
                    'name': track['name'],
                }
            )

    return tracks
