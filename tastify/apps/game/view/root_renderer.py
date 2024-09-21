import reflex as rx

from tastify import db
from tastify.apps.game.state import GameState
from tastify.apps.game.view.child import ChildRenderer
from tastify.apps.game.view.dashboard import DashboardRenderer
from tastify.apps.game.view.guesser import GuesserRenderer
from tastify.apps.game.view.proposer import ProposerRenderer


class RootRenderer:
    def __init__(self):
        self.dashboard = DashboardRenderer()
        self.proposer = ProposerRenderer()
        self.guesser = GuesserRenderer()

    def render(self) -> rx.Component:
        return rx.cond(
            GameState.is_dashboard,
            self.render_child(self.dashboard),
            rx.cond(
                GameState.is_current_player,
                self.render_child(self.proposer),
                self.render_child(self.guesser),
            ),
        )

    def render_child(self, renderer: ChildRenderer) -> rx.Component:
        return rx.match(
            GameState.game_state,
            (db.GameState.NEW, renderer.render_new()),
            (db.GameState.PREPARING, renderer.render_preparing()),
            (db.GameState.PROPOSE, renderer.render_propose()),
            (db.GameState.GUESS, renderer.render_guess()),
            (db.GameState.RESULTS, renderer.render_result()),
        )