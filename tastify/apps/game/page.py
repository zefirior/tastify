import reflex as rx

from tastify.apps.game.state import GameState
from tastify.apps.router import Router


@rx.page(route=Router.GAME_PATH, on_load=GameState.refresh_game)
def game() -> rx.Component:
    return rx.vstack(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("UID"),
                    rx.table.column_header_cell("Name"),
                    rx.table.column_header_cell("Score"),
                ),
            ),
            rx.table.body(
                rx.foreach(
                    GameState.players,
                    lambda user: rx.table.row(
                        rx.table.row_header_cell(user.user_uid),
                        rx.table.cell(user.name),
                        rx.table.cell(user.score),
                    ),
                )
            ),
            width="100%",
        ),
        width="100%",
        spacing="6",
        padding_x=["1.5em", "1.5em", "3em"],
        on_mount=GameState.load_state,
    )
