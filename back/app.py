import random
import string

from advanced_alchemy.extensions.litestar import SQLAlchemySerializationPlugin
from litestar import Litestar, get, post, Request, Response, MediaType
from litestar.config.cors import CORSConfig
from litestar.exceptions import HTTPException
from sqlalchemy import select

import consts
from back.db.base import create_session, Room, User, UserRole, RoomUser, DBSettings
from consts import ROOM_CODE_ALLOWED_CHARS


def generate_room_code(length):
    return ''.join(random.choices(ROOM_CODE_ALLOWED_CHARS, k=length))


@post("/room")
async def create_room() -> Room:
    async with create_session() as session:
        room = Room(code=generate_room_code(4), game_state={})
        session.add(room)
    return room


@post("/room/{room_code:str}/join")
async def join_room(room_code: str, nickname: str) -> Response:
    stmt = select(Room).where(Room.code == room_code)
    async with create_session() as session:
        if not (room := (await session.execute(stmt)).scalar()):
            raise HTTPException(status_code=404, detail="Room not found")

        stmt = (
            select(RoomUser)
            .where(RoomUser.room_uuid == room.pk, RoomUser.nickname == nickname)
        )
        if (await session.execute(stmt)).scalar():
            raise HTTPException(status_code=400, detail="Nickname already taken")

        user = User()
        session.add(user)
        await session.flush()
        room_user = RoomUser(nickname=nickname, role=UserRole.player.value, user_uuid=user.pk, room_uuid=room.pk)
        session.add(room_user)
    return Response(status_code=201, content={})


@post("/r/{room_code: str}/user/{uuid: str}/inc")
async def increase_points(request: Request, room_code: str, uuid: str) -> dict:
    data = request.json()
    new_data = {}
    # return Response(content=new_data, media_type="application/json")
    return {}

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
    cors_config=CORSConfig(allow_origins=consts.ALLOW_ORIGINS),
)
