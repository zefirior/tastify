import random
import string
from typing import Any

from advanced_alchemy.extensions.litestar import SQLAlchemySerializationPlugin
from litestar import Litestar, get, post, Request, Response, MediaType
from litestar.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified

from back.db.base import create_session, Room, User, UserRole, RoomUser, DBSettings

ROOM_CODE_LENGTH = 4
ROOM_CODE_ALLOWED_CHARS = string.ascii_uppercase + string.digits


def generate_room_code(length):
    return ''.join(random.choices(ROOM_CODE_ALLOWED_CHARS, k=length))


@post("/room")
async def create_room() -> Room:
    async with create_session() as session:
        room = Room(code=generate_room_code(4), game_state={})
        session.add(room)
    return room


@post("/room/{room_code:str}/join")
async def join_room(room_code: str, nickname: str, user_uuid: str) -> Response:
    room_stmt = select(Room).where(Room.code == room_code)
    async with create_session() as session:
        if not (room := (await session.execute(room_stmt)).scalar()):
            raise HTTPException(status_code=404, detail="Room not found")

        room_user_stmt = (
            select(RoomUser)
            .where(RoomUser.room_uuid == room.pk, RoomUser.nickname == nickname)
        )
        if (await session.execute(room_user_stmt)).scalar():
            raise HTTPException(status_code=400, detail="Nickname already taken")

        user = User(pk=user_uuid)
        session.add(user)
        room_user = RoomUser(nickname=nickname, role=UserRole.player.value, user_uuid=user_uuid, room_uuid=room.pk)
        session.add(room_user)
    return Response(status_code=201, content={})


@post("/room/{room_code:str}/user/{user_pk:str}/increment")
async def increase_points(room_code: str, user_pk: str) -> dict[str, Any]:
    room_stmt = select(Room).where(Room.code == room_code).with_for_update()
    async with create_session() as session:
        if not (room := (await session.execute(room_stmt)).scalar()):
            raise HTTPException(status_code=404, detail="Room not found")

        room_user_stmt = (
            select(RoomUser)
            .where(RoomUser.room_uuid == room.pk, RoomUser.user_uuid == user_pk)
        )
        if not (await session.execute(room_user_stmt)).scalar():
            raise HTTPException(status_code=400, detail="User not found")

        flag_modified(room, "game_state")
        room.game_state.setdefault("points", {})
        room.game_state["points"].setdefault(user_pk, 0)
        room.game_state["points"][user_pk] += 1

    return room.game_state


@get("/room/{room_code: str}")
async def get_game(room_code: str) -> str:
    return room_code


def plain_text_exception_handler(_: Request, exc: Exception) -> Response:
    status_code = getattr(exc, "status_code", 500)
    detail = getattr(exc, "detail", "")
    return Response(
        media_type=MediaType.TEXT,
        content=detail,
        status_code=status_code,
    )


settings = DBSettings()
settings.setup()
app = Litestar(
    [create_room, join_room, increase_points, get_game],
    plugins=[SQLAlchemySerializationPlugin()],
    exception_handlers={HTTPException: plain_text_exception_handler},
)
