import reflex as rx

from tastify.core.integration.spotify.client import SpotifyClient


class Router:
    HOME_PATH = "/"
    ROOM_PATH = "/room/[room_code]"
    REGISTER_SPOTIFY_PATH = SpotifyClient.REGISTER_CALLBACK

    @staticmethod
    def to_room(room_code: str):
        """Redirect to room."""
        return redirect_with_params(
            Router.ROOM_PATH,
            params={
                "[room_code]": room_code,
            },
        )

    @staticmethod
    def to_home():
        """Redirect to room."""
        return rx.redirect(Router.HOME_PATH)


def redirect_with_params(path: str, params: dict[str, str]):
    """Replace args in path."""
    for key, value in params.items():
        if key not in path:
            raise ValueError(f"Key {key} not found in path {path}")
        path = path.replace(key, value)
    return rx.redirect(path)
