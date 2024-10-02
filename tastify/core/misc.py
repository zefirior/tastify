from tastify.core.integration.spotify.models.common import Image


def smallest_image(images: list[Image]) -> Image:
    return min(images, key=lambda image: image.height + image.width)


def filter_player(user_uid, players):
    return next((player for player in players if player.user_uid == user_uid), None)
