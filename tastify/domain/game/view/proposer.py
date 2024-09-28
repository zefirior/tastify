import reflex as rx

from tastify import db
from tastify.domain.game.state import TRANSITION_MAP, GameState, SearchArtistState, ArtistDto
from tastify.domain.game.view.child import ChildRenderer, _render_guess


class ProposerRenderer(ChildRenderer):
    def render_new(self) -> rx.Component:
        return _render(db.GameState.NEW)

    def render_preparing(self) -> rx.Component:
        return _render(db.GameState.PREPARING)

    def render_propose(self) -> rx.Component:
        return search_artist()

    def render_guess(self) -> rx.Component:
        return _render_guess("Proposer")

    def render_result(self) -> rx.Component:
        return _render(db.GameState.RESULTS)


def _render(state: db.GameState) -> rx.Component:
    next_state = TRANSITION_MAP[state]
    return rx.vstack(
        rx.heading(f"Proposer on state {state}"),
        rx.button(f"To {next_state}", on_click=GameState.move_game_state),
    )


def search_artist():
    return rx.card(
        rx.flex(
            rx.input(
                rx.input.slot(
                    rx.icon(tag="search"),
                ),
                placeholder="Search songs...",
                on_change=SearchArtistState.search,
            ),
            rx.flex(
                rx.foreach(
                    SearchArtistState.artists,
                    artist_card,
                ),
                direction="column",
                spacing="1",
            ),
            direction="column",
            spacing="3",
        ),
        style={"maxWidth": 500},
    )


def artist_card(artist: ArtistDto) -> rx.Component:
    return rx.card(
        rx.flex(
            rx.flex(
                rx.image(src=artist.image_url, width=60, height=60),
                rx.flex(
                    rx.text(artist.name, size="2", weight="bold"),
                    rx.text(
                        artist.genres[0], size="1", color_scheme="gray"
                    ),
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
        on_click=lambda: GameState.select_artist(artist),
    )
