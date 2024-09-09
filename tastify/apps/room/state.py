import asyncio
from typing import Optional

import reflex as rx
from sqlmodel import select
from PIL.Image import Image

from tastify.apps.common.state import CommonState
from tastify.apps.room.utils import generate_room_code
from tastify.apps.router import Router
from tastify.core.qrcode_utils import make_qrcode
from tastify import db

COUNT_REQUIRED_PLAYERS = 2


class RoomState(rx.State):
    room: db.Room = None
    room_link: str = None
    room_qrcode: Image = None
    users_in_room: list[db.UserRoom] = []
    is_enough_players: bool = False
    _n_tasks: int = 0

    def load_room(self):
        """Load a room."""
        print("loading state")
        with rx.session() as session:
            self.room = session.exec(select(db.Room).where(db.Room.code == self.room_code)).first()
            self.users_in_room = list(session.exec(
                select(db.UserRoom).where(db.UserRoom.room_id == self.room.id)
            ).all())
            self.is_enough_players = len(self.users_in_room) >= COUNT_REQUIRED_PLAYERS
            self.room_qrcode = make_qrcode(Router.join_link(self.room_code)).get_image()
            self.room_link = Router.join_link(self.room_code)

    @rx.background
    async def refresh_room(self):
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
                if self.router.page.path != Router.ROOM_PATH:
                    print("Not in room page")
                    return
                self.load_room()

            # Await long operations outside the context to avoid blocking UI
            await asyncio.sleep(2)

    @rx.var
    def room_code(self) -> str | None:
        return self.router.page.params.get("room_code", None)

    def join_room_redirect(self):
        return Router.to_join_room(self.room_code)

    def start_game(self):
        """Start a game."""
        self.load_room()
        with rx.session() as session:
            if not self.is_enough_players:
                return rx.toast.error("Not enough players")
            game = session.exec(select(db.Game).where(
                db.Game.room_id == self.room.id,
                db.Game.state == db.GameState.NEW,
            )).first()
            if game:
                return Router.to_game(self.room.code)

            game = db.Game(room_id=self.room.id, state=db.GameState.NEW)
            session.add(game)
            session.flush()

            for i, user_room in enumerate(self.users_in_room):
                player = db.UserGame(
                    user_uid=user_room.user_uid,
                    game_id=game.id,
                    name=user_room.name,
                    order=i,
                )
                session.add(player)
            session.commit()
        return Router.to_game(self.room.code)


def get_user_room(session, user_uid: str, room_id: int) -> Optional[db.UserRoom]:
    """Get a user room."""
    return session.exec(
        select(db.UserRoom).where(
            db.UserRoom.user_uid == user_uid,
            db.UserRoom.room_id == room_id
        )
    ).first()


class JoinRoomState(rx.State):
    user_name: str = ""
    target_room: str = ""

    @rx.var
    def room_code(self) -> str | None:
        return self.router.page.params.get("room_code", None)

    async def join_room(self):
        """Join a room."""
        if not self.user_name:
            return rx.toast.error("Please enter your name")

        target_room_code = self.room_code or self.target_room
        with rx.session() as session:
            room = session.exec(select(db.Room).where(db.Room.code == target_room_code.upper())).first()
            if not room:
                return rx.toast.error("Room not found")
            common = await self.get_state(CommonState)
            user = common.get_or_create_user(session)
            user_room = get_user_room(session, user.uid, room.id)
            if not user_room:
                user_room = db.UserRoom(user_uid=user.uid, room_id=room.id, name=self.user_name)
                session.add(user_room)
                session.commit()
            return Router.to_room(room.code)

    def get_room(self, session, room_code: str) -> db.Room:
        """Get a room."""
        room = session.exec(select(db.Room).where(db.Room.code == room_code)).first()
        if not room:
            raise


class CreateRoomState(rx.State):
    def create_room(self):
        """Create a new room."""
        room_code = generate_room_code()
        with rx.session() as session:
            room = db.Room(code=room_code)
            session.add(room)
            session.commit()
        return Router.to_room(room_code=room_code)
