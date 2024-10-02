import reflex as rx

from tastify import db
from tastify.domain.game.state import TRANSITION_MAP, GameState, SearchArtistState, ArtistDto, SearchArtistTracksState, \
    TrackDto
from tastify.domain.game.view.child import ChildRenderer, _render_guess


class GuesserRenderer(ChildRenderer):
    def render_new(self) -> rx.Component:
        return _render(db.GameState.NEW)

    def render_preparing(self) -> rx.Component:
        return _render(db.GameState.PREPARING)

    def render_propose(self) -> rx.Component:
        return _render(db.GameState.PROPOSE)

    def render_guess(self) -> rx.Component:
        return rx.vstack(  # TODO: add artist card
            rx.button(
                "Not favorite",
                on_click=GameState.guesser_skip_round,
                color_scheme="red",
            ),
            search_tracks(),
        )

    def render_result(self) -> rx.Component:
        return _render(db.GameState.RESULTS)


def _render(state: db.GameState) -> rx.Component:
    next_state = TRANSITION_MAP[state]
    return rx.vstack(
        rx.heading(f"Guesser on state {state}"),
        rx.button(f"To {next_state}", on_click=GameState.move_game_state),
    )


def search_tracks():
    return rx.card(
        rx.flex(
            rx.input(
                rx.input.slot(
                    rx.icon(tag="search"),
                ),
                placeholder="Search songs...",
                on_change=lambda query: SearchArtistTracksState.search(query, GameState.round.artist), # TODO: get artist name
            ),
            rx.flex(
                rx.foreach(
                    SearchArtistTracksState.tracks,
                    track_card,
                ),
                direction="column",
                spacing="1",
            ),
            direction="column",
            spacing="3",
        ),
        style={"maxWidth": 500},
    )


def track_card(track: TrackDto) -> rx.Component:
    return rx.card(
        rx.flex(
            rx.flex(
                rx.image(src=track.album_image_url, width=60, height=60),
                rx.flex(
                    rx.text(track.name, size="2", weight="bold"),
                    direction="column",
                    spacing="1",
                ),
                direction="row",
                align_items="left",
                spacing="1",
            ),
            rx.flex(
                rx.icon(tag="chevron_right"),
                align_items="center",
            ),
            justify="between",
        ),
        on_click=lambda: GameState.select_track(track),
    )
