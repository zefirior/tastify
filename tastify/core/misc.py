from tastify.core.integration.spotify.client import Image


def smallest_image(images: list[Image]) -> Image:
    return min(images, key=lambda image: image.height + image.width)