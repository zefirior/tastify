from pydantic.dataclasses import dataclass

from tastify.core.integration.spotify.models.common import Image


@dataclass
class Album:
    id: str
    href: str
    name: str
    images: list[Image]


@dataclass
class Track:
    id: str
    duration_ms: int
    href: str
    name: str
    album: Album
    preview_url: str | None = None


@dataclass
class Artist:
    id: str
    name: str
    images: list[Image]
    genres: list[str]


@dataclass
class SearchArtistsResponse:
    href: str
    items: list[Artist]
    limit: int
    offset: int
    total: int
    next: str | None = None
    previous: str | None = None


@dataclass
class SearchTracksResponse:
    href: str
    items: list[Track]
    limit: int
    offset: int
    total: int
    next: str | None = None
    previous: str | None = None


@dataclass
class SearchResponse:
    artists: SearchArtistsResponse | None = None
    tracks: SearchTracksResponse | None = None

    # def __init__(self, artists: dict | None = None, tracks: dict | None = None):
    #     self.artists = SearchArtistsResponse(**artists) if artists else None
    #     self.tracks = SearchTracksResponse(**tracks) if tracks else None
