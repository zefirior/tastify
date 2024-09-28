from dataclasses import dataclass

from reflex import serializer

from tastify.core.integration.spotify.models.common import Image, image_to_dict


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
class Album:
    id: str
    name: str
    images: list[Image]

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
