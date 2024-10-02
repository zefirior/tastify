from pydantic.dataclasses import dataclass
from reflex import serializer


@dataclass
class Image:
    url: str
    height: int
    width: int


@serializer
def image_to_dict(self: Image):
    return {
        'url': self.url,
        'height': self.height,
        'width': self.width,
    }
