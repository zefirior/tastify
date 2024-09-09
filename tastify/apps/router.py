import reflex as rx

from tastify.core.integration.spotify.client import SpotifyClient


class Router:
    HOME_PATH = "/"
    ROOM_PATH = "/room/[room_code]"
    JOIN_ROOM_PATH = "/room/[room_code]/join"
    GAME_PATH = "/room/[room_code]/game"
    REGISTER_SPOTIFY_PATH = SpotifyClient.REGISTER_CALLBACK

    @staticmethod
    def join_link(room_code: str):
        """Redirect to room."""
        return "http://tastify.zefirior.com" + Router.JOIN_ROOM_PATH.replace("[room_code]", room_code)

    @staticmethod
    def to_join_room(room_code: str):
        """Redirect to room."""
        return redirect_with_params(
            Router.JOIN_ROOM_PATH,
            params={
                "[room_code]": room_code,
            },
            external=True,
        )

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
    def to_game(room_code: str):
        """Redirect to room."""
        return redirect_with_params(
            Router.GAME_PATH,
            params={
                "[room_code]": room_code,
            },
        )

    @staticmethod
    def to_home():
        """Redirect to room."""
        return rx.redirect(Router.HOME_PATH)


def redirect_with_params(path: str, params: dict[str, str], external=False):
    """Replace args in path."""
    for key, value in params.items():
        if key not in path:
            raise ValueError(f"Key {key} not found in path {path}")
        path = path.replace(key, value)
    return rx.redirect(path, external=external)
