from dataclasses import dataclass

from tastify.core.integration.spotify.models.common import Image


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
    next: str | None
    offset: int
    previous: str | None
    total: int


@dataclass
class SearchResponse:
    artists: SearchArtistsResponse
