import reflex as rx

from tastify import db
from tastify.apps.room.state import JoinRoomState, CreateRoomState
from tastify.apps.spotify.state import SpotifyState, SpotifyListUserTracksState
from tastify.core.integration.spotify.client import UserTrack


def index() -> rx.Component:
    return rx.vstack(
        rx.button("Create room", on_click=CreateRoomState.create_room),
        rx.spacer(),
        rx.heading("Join the room", size="4"),
        rx.hstack(
            rx.input(
                placeholder="Your name",
                value=JoinRoomState.user_name,
                on_change=JoinRoomState.set_user_name,
                width="100%",
                margin_bottom="4",
            ),
            rx.input(
                placeholder="Room code",
                value=JoinRoomState.target_room,
                on_change=JoinRoomState.set_target_room,
                width="100%",
                margin_bottom="4",
            ),
            rx.button("Join", on_click=JoinRoomState.join_room),
        ),

        rx.spacer(),
        rx.heading("Your playlists", size="4"),
        rx.cond(
            SpotifyListUserTracksState.state == db.SpotifyConnectorState.DISCONNECTED,
            rx.button("Spotify", on_click=SpotifyState.connect),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("UID"),
                        rx.table.column_header_cell("Name"),
                        rx.table.column_header_cell("Artists"),
                        rx.table.column_header_cell("Preview"),
                    ),
                ),
                rx.table.body(
                    rx.foreach(
                        SpotifyListUserTracksState.tracks,
                        make_track_row,
                    )
                ),
                width="100%",
            ),
        ),
        width="100%",
        spacing="6",
        padding_y=["1.5em", "1.5em", "3em"],
        padding_x=["1.5em", "1.5em", "3em"],
        on_mount=SpotifyListUserTracksState.load_tracks,
    )


def make_track_row(track: UserTrack):
    return rx.table.row(
        rx.table.row_header_cell(track.id),
        rx.table.cell(track.name),
        rx.table.cell(track.artists[0].name),
        rx.table.cell(rx.image(src=track.album.images[0].url, width=60, height=60)),
    )