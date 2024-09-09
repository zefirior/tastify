import asyncio

import reflex as rx
from sqlmodel import select

from tastify.apps.router import Router
from tastify.db.game import Game, UserGame
from tastify.db.room import Room


class GameState(rx.State):
    game: Game = None
    players: list[UserGame] = []
    current_player: bool = None
    _n_tasks: int = 0

    @rx.var
    def room_code(self) -> str | None:
        return self.router.page.params.get("room_code", None)

    @rx.background
    async def refresh_game(self):
        print(f"Refreshing state for {self.__class__.__name__}")
        # TODO: limit this task
        async with self:
            # The latest state values are always available inside the context
            if self._n_tasks > 0:
                # only allow 1 concurrent task
                return

            # State mutation is only allowed inside context block
            self._n_tasks += 1

        while True:
            async with self:
                if self.router.page.path != Router.GAME_PATH:
                    print("Not in room page")
                    return
                self.load_state()

            # Await long operations outside the context to avoid blocking UI
            await asyncio.sleep(2)

    def load_state(self):
        """Load a game."""
        with rx.session() as session:
            self.game = session.exec(
                select(Game).join(
                    Room, Room.id == Game.room_id,
                ).order_by(
                    Game.created_at,
                ).where(
                    Room.code == self.room_code,
                )
            ).first()

            self.players = list(session.exec(
                select(
                    UserGame
                ).join(
                    Game,
                    Game.id == UserGame.game_id
                ).where(Game.id == self.game.id)
            ).all())
