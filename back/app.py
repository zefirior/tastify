import logging
import random
from typing import Any
from uuid import uuid4

from advanced_alchemy.extensions.litestar import SQLAlchemySerializationPlugin
from litestar import Litestar, get, post, Request, Response, MediaType
from litestar.config.cors import CORSConfig
from litestar.exceptions import HTTPException
from litestar.logging import LoggingConfig
from sqlalchemy import select, and_
from sqlalchemy.orm.attributes import flag_modified

import consts
from back.db.base import create_session, Room, User, UserRole, RoomUser, DBSettings, RoomStatus
from back.db.utils import dump_room
from consts import ROOM_CODE_ALLOWED_CHARS
from spotify import spotify_api


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logger.addHandler(logging.StreamHandler())


def generate_room_code(length):
    return ''.join(random.choices(ROOM_CODE_ALLOWED_CHARS, k=length))


async def get_user(session, user_uuid: str) -> User:
    user_stmt = select(User).where(User.pk == user_uuid)
    if not (user := (await session.execute(user_stmt)).scalar()):
        user = User(pk=user_uuid)
        session.add(user)
        await session.flush()
    return user


@post("/room")
async def create_room(admin_uuid: str) -> dict[str, Any]:
    async with create_session() as session:
        user = await get_user(session, admin_uuid)

        room = Room(
            pk=str(uuid4()),
            code=generate_room_code(4),
            game_state={},
            status=RoomStatus.NEW.value,
            created_by=user.pk,
        )
        session.add(room)

        return dump_room(admin_uuid, room, [])


@post("/room/{room_code:str}/join")
async def join_room(room_code: str, nickname: str, user_uuid: str) -> Response:
    room_stmt = select(Room).where(Room.code == room_code)
    async with create_session() as session:
        if not (room := (await session.execute(room_stmt)).scalar()):
            raise HTTPException(status_code=404, detail="Room not found")
        if room.status != RoomStatus.NEW:
            raise HTTPException(status_code=400, detail="Room is not accepting new players")

        room_user_stmt = (
            select(RoomUser)
            .where(RoomUser.room_uuid == room.pk, RoomUser.nickname == nickname)
        )
        if (await session.execute(room_user_stmt)).scalar():
            raise HTTPException(status_code=400, detail="Nickname already taken")

        user = await get_user(session, user_uuid)
        room_user = RoomUser(nickname=nickname, role=UserRole.PLAYER.value, user_uuid=user.pk, room_uuid=room.pk)
        session.add(room_user)
    return Response(status_code=201, content={})


@post("/room/{room_code:str}/user/{user_pk:str}/increment", deprecated=True)
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


@get("/search/group")
async def search_groups(q: str) -> list:
    groups = []
    results = spotify_api.search(q=q, limit=10, type='artist')
    for artist in results['artists']['items']:
        if artist['images']:
            image_url = sorted(artist['images'], key=lambda image: image['height'])[0]['url']
        else:
            image_url = ''

        groups.append({
            'name': artist['name'],
            'id': artist['id'],
            'image_url': image_url,
        })

    return groups


@get("/search/track")
async def search_tracks(group_id: str, q: str) -> list:
    artist = spotify_api.artist(group_id)
    tracks = []
    results = spotify_api.search(q=f'{q} artist:"{artist["name"]}"', limit=50, type='track')
    for track in results['tracks']['items']:
        if track['artists'][0]['id'] == group_id:
            tracks.append({
                'id': track['id'],
                'name': track['name'],
            })

    return tracks


def plain_text_exception_handler(_: Request, exc: Exception) -> Response:
    status_code = getattr(exc, "status_code", 500)
    detail = getattr(exc, "detail", "")
    return Response(
        media_type=MediaType.TEXT,
        content=detail,
        status_code=status_code,
    )


logging_config = LoggingConfig(
    root={"level": "INFO", "handlers": ["queue_listener"]},
    formatters={
        "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
    },
    log_exceptions="always",
)

settings = DBSettings()
settings.setup()
app = Litestar(
    [create_room, join_room, increase_points, get_game, search_groups, search_tracks],
    plugins=[SQLAlchemySerializationPlugin()],
    exception_handlers={HTTPException: plain_text_exception_handler},
    cors_config=CORSConfig(allow_origins=consts.ALLOW_ORIGINS),
    logging_config=logging_config,
)
