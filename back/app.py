import random
from typing import Any
from uuid import uuid4

from advanced_alchemy.extensions.litestar import SQLAlchemySerializationPlugin
from litestar import Litestar, get, post, Request, Response, MediaType
from litestar.config.cors import CORSConfig
from litestar.exceptions import HTTPException
from sqlalchemy import select, and_
from sqlalchemy.orm.attributes import flag_modified

import consts
from back.db.base import create_session, Room, User, UserRole, RoomUser, DBSettings
from back.db.utils import dump_room
from consts import ROOM_CODE_ALLOWED_CHARS


def generate_room_code(length):
    return ''.join(random.choices(ROOM_CODE_ALLOWED_CHARS, k=length))


@post("/room")
async def create_room(admin_uuid: str) -> dict[str, Any]:
    user_stmt = select(User).where(User.pk == admin_uuid)
    async with create_session() as session:
        if (await session.execute(user_stmt)).scalar():
            raise HTTPException(status_code=400, detail="User already exists")

        user = User(pk=admin_uuid)
        room = Room(pk=str(uuid4()), code=generate_room_code(4), game_state={'is_active': True})
        room_user = RoomUser(nickname='admin', role=UserRole.ADMIN.value, user_uuid=admin_uuid, room_uuid=room.pk)
        session.add_all([room_user, room, user])

    return dump_room(admin_uuid, room, [room_user])


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
        room_user = RoomUser(nickname=nickname, role=UserRole.PLAYER.value, user_uuid=user_uuid, room_uuid=room.pk)
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
async def get_game(room_code: str, user_uuid: str) -> dict:
    room_stmt = select(Room).where(Room.code == room_code)

    room_user_stmt = select(RoomUser).join(Room).where(and_(Room.code == room_code))
    async with create_session() as session:
        if not (room := (await session.execute(room_stmt)).scalar()):
            raise HTTPException(status_code=404, detail="Room not found")

        result = await session.execute(room_user_stmt)
        room_users = [item[0] for item in result.all()]

    return dump_room(user_uuid, room, room_users)


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
    cors_config=CORSConfig(allow_origins=consts.ALLOW_ORIGINS),
)
