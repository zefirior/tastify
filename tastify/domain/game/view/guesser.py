import reflex as rx

from tastify import db
from tastify.domain.game.state import TRANSITION_MAP, GameState
from tastify.domain.game.view.child import ChildRenderer


class GuesserRenderer(ChildRenderer):
    def render_new(self) -> rx.Component:
        return _render(db.GameState.NEW)

    def render_preparing(self) -> rx.Component:
        return _render(db.GameState.PREPARING)

    def render_propose(self) -> rx.Component:
        return _render(db.GameState.PROPOSE)

    def render_guess(self) -> rx.Component:
        return _render(db.GameState.GUESS)

    def render_result(self) -> rx.Component:
        return _render(db.GameState.RESULTS)


def _render(state: db.GameState) -> rx.Component:
    next_state = TRANSITION_MAP[state]
    return rx.vstack(
        rx.heading(f"Guesser on state {state}"),
        rx.button(f"To {next_state}", on_click=GameState.move_game_state),
    )
