import abc

import reflex as rx

from tastify import db
from tastify.domain.game.state import TRANSITION_MAP, GameState


class ChildRenderer(abc.ABC):
    @abc.abstractmethod
    def render_new(self) -> rx.Component:
        pass

    @abc.abstractmethod
    def render_preparing(self) -> rx.Component:
        pass

    @abc.abstractmethod
    def render_propose(self) -> rx.Component:
        pass

    @abc.abstractmethod
    def render_guess(self) -> rx.Component:
        pass

    @abc.abstractmethod
    def render_result(self) -> rx.Component:
        pass


def _render_guess(who: str) -> rx.Component:
    state = db.GameState.GUESS
    next_state = TRANSITION_MAP[state]
    return rx.vstack(
        rx.heading(f"{who} on state {state}"),
        rx.heading(f"Proposed artist: {GameState.artist}"),
        rx.button(f"To {next_state}", on_click=GameState.move_game_state),
    )
