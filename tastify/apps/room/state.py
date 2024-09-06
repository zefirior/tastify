import asyncio
from typing import Optional

import reflex as rx
from sqlmodel import select

from tastify.apps.common import CommonState
from tastify.apps.room.model import Room, UserRoom
from tastify.apps.room.utils import generate_room_code
from tastify.apps.router import Router


class RoomState(rx.State):
    room: Room = None
    users_in_room: list[UserRoom] = []
    _n_tasks: int = 0

    @rx.var
    def room_code(self) -> str | None:
        return self.router.page.params.get("room_code", None)

    def load_room(self):
        """Load a room."""
        with rx.session() as session:
            self.room = session.exec(select(Room).where(Room.code == self.room_code)).first()
            self.users_in_room = list(session.exec(
                select(UserRoom).where(UserRoom.room_id == self.room.id)
            ).all())

    @rx.background
    async def refresh_room(self):
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


def get_user_room(session, user_uid: str, room_id: int) -> Optional[UserRoom]:
    """Get a user room."""
    return session.exec(
        select(UserRoom).where(
            UserRoom.user_uid == user_uid,
            UserRoom.room_id == room_id
        )
    ).first()


class JoinRoomState(rx.State):
    user_name: str = ""
    target_room: str = ""

    async def join_room(self):
        """Join a room."""
        if not self.user_name:
            return rx.toast.error("Please enter your name")
        with rx.session() as session:
            room = session.exec(select(Room).where(Room.code == self.target_room.upper())).first()
            if not room:
                return rx.toast.error("Room not found")
            common = await self.get_state(CommonState)
            user = common.get_or_create_user(session)
            user_room = get_user_room(session, user.uid, room.id)
            if not user_room:
                user_room = UserRoom(user_uid=user.uid, room_id=room.id, name=self.user_name)
                session.add(user_room)
                session.commit()
            return Router.to_room(room.code)

    def get_room(self, session, room_code: str) -> Room:
        """Get a room."""
        room = session.exec(select(Room).where(Room.code == room_code)).first()
        if not room:
            raise


class CreateRoomState(rx.State):
    def create_room(self):
        """Create a new room."""
        room_code = generate_room_code()
        with rx.session() as session:
            room = Room(code=room_code)
            session.add(room)
            session.commit()
        return Router.to_room(room_code=room_code)
